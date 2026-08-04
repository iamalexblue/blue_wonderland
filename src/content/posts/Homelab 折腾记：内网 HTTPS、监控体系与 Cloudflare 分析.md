---
title: Homelab 折腾记：内网 HTTPS、监控体系与 Cloudflare 分析
pubDate: 2026-08-05
categories:
    - tech
    - homelab
    - networking
    - monitoring
description: 从 Firefox 打不开 Nextcloud Talk 出发，一路搞定内网 HTTPS 受信证书、Grafana 监控全家桶和 Cloudflare Analytics 面板，顺便踩了三个 GraphQL 的坑
lastmod: 2026-08-05T12:00:00.000Z
---

> 从 Firefox 打不开 Nextcloud Talk 出发，一路搞定内网 HTTPS 受信证书、Grafana 监控全家桶和 Cloudflare Analytics 面板。

---

## 起因：Firefox 打不开 Nextcloud Talk

某天发现局域网里的 Firefox 和 Safari 打不开 Nextcloud Talk，而 Chrome 和 Edge 一切正常。控制台里一堆 CSP 警告，禁用了所有浏览器扩展依然如此，一度以为是 Nextcloud 配置问题。

排查了半天，真相和 Nextcloud 一点关系都没有——**是浏览器安全模型**。

## 根因：安全上下文与浏览器的策略差异

WebRTC（摄像头、麦克风、`crypto.subtle` 等）只能在**安全上下文**（HTTPS 或 localhost）下工作。我访问的是 `http://10.10.10.10:10081`——既不是 HTTPS 也不是 localhost，Firefox/Safari 严格遵守规范直接禁用。

而 Chrome/Edge（Chromium 系）有一个刻意的放宽：**把非公网 IP（10.x、192.168.x 这类 RFC1918 地址）也判定为可信任来源**——理由是内网 IP 无法被公网中间人攻击。所以同样的地址，Chromium 能用 WebRTC，Firefox/Safari 不能。

结论：Firefox 在内网 HTTP 下让 Talk 正常工作，浏览器层面无解（`media.navigator.mediadevices.insecure.enabled` 只放宽了 mediaDevices，改不了 `window.isSecureContext`）。

## 方案：内网专用域名 + 受信证书

既然必须 HTTPS，那就给内网访问配上 HTTPS。设计要点：**绝不动公网域名**（`next.iamalex.blue` 走 Cloudflare 隧道，原样保留），新建一个内网专用子域 `nc.iamalex.blue`：

```
CF DNS: nc.iamalex.blue → 10.10.10.10（A 记录，不代理）
Let's Encrypt: DNS-01 验证签发受信证书（无需公网端口）
Caddy（mac mini）: https://nc.iamalex.blue → 127.0.0.1:10081
局域网设备: 解析 nc.iamalex.blue 得到内网 IP，直连
```

几个关键机制：

- **DNS 只是"域名 → IP"对照表**，IP 填内网地址完全合法。CF 权威 DNS 让所有设备（包括 iPhone，不用改 hosts）自动把 `nc.iamalex.blue` 解析到 `10.10.10.10`，局域网内直连，不绕公网。
- **DNS-01 验证只需要能操控 DNS 记录**（CF API token），CA 查询 `_acme-challenge` TXT 记录确认域名归属，**完全不要求服务器公网可达**——所以"域名指向内网 IP"和"签发受信证书"毫不冲突。
- **证书绑定域名而非 IP**：TLS 握手验证的是"域名匹配 + CA 受信"，IP 是什么不参与验证。浏览器看到 `https://nc.iamalex.blue` 就是安全上下文，WebRTC 全部解锁。

证书用 acme.sh + DNS-01 签发（Let's Encrypt，90 天有效期），cron 每天检查、到期前约 30 天自动续期。顺手把 Glance 仪表盘也挂了个 `home.iamalex.blue`，两个内网域名一套体系。

## 顺手的收益：内网域名体系

| 域名 | 指向 | 用途 |
|---|---|---|
| `nc.iamalex.blue` | Nextcloud | Firefox/Safari 内网用 Talk |
| `home.iamalex.blue` | Glance | 仪表盘内网访问 |
| `next.iamalex.blue` | 公网隧道 | 外网访问，原样不变 |

内网域名不受运营商 CGNAT 影响（不走公网），速度更快更稳定。

## 从零搭起 Grafana 监控体系

既然这台 Mac mini M4（16GB）跑着整套 CasaOS 虚拟机（Debian），正好把一直没配置的 Grafana 用起来。最终架构：

```
Prometheus（虚拟机，systemd）
 ├─ node_exporter（虚拟机 9100 + mac mini 19100）
 ├─ cAdvisor（8081，容器级指标）
 ├─ cloudflared metrics（127.0.0.1:20241，隧道指标）
 └─ postgres_exporter（9187）
Grafana：Prometheus 数据源 + 官方仪表盘（1860/14282）
```

几个值得一提的点：

- **cloudflared 自带 Prometheus 指标端点**（默认 127.0.0.1:20241），连接数、请求量、错误数全有——把之前讨论过的"watchdog 盲区"（隧道活着但后端全挂）变成了可视化的 5xx 曲线。
- **全部二进制 + systemd 部署**（用户偏好），Prometheus 88MB、cAdvisor 37MB、node_exporter 15MB，整套路 ~170MB，比一个 jellyfin 还轻。
- 踩了个坑：**OrbStack 会自动把虚拟机监听的端口发布到 mac mini 宿主**，导致 mac 上的 node_exporter 和虚拟机端口冲突（9100），换个端口（19100）解决——差点把虚拟机的数据当成 mac 的。
- Grafana 数据源用 **provisioning 文件注入**（`/etc/grafana/provisioning/`），不需要登录 UI 配置，重启自动加载。

## Cloudflare Analytics：三次踩坑记录

Cloudflare 有 GraphQL Analytics API，但免费套餐的规则比较阴：

1. **`httpRequestsAdaptiveGroups`（支持按路径/状态码/国家分组）查询窗口最长 1 天**——想查 30 天直接报 `time range wider than 1d`。
2. **adaptive 的 `filter` 里不能放 `zoneTag`**——它在 `zones(filter:)` 外层。
3. **date 参数只接受纯日期 `YYYY-MM-DD`**（不接受 ISO 时间戳），状态码维度叫 `edgeResponseStatus` 而不是 `responseStatus`。

于是拆成两个仪表盘：

- **Cloudflare Analytics（30 天趋势）**：用 `httpRequests1dGroups`（不限窗口），请求/带宽/威胁曲线 + 每日明细。
- **Cloudflare Live（24h 分布）**：用 adaptive 数据集，状态码/路径/国家/缓存，**每天 00:05 由 cron 自动滚动日期**（写死日期 + 定时更新，绕开宏替换的不可控）。

另一个坑：**Grafana provisioning 导入的 dashboard 修改后必须递增 `version`**，否则 Grafana 认为配置没变直接跳过更新——"改了没用"的假象就是这么来的。还有 Infinity 数据源的面板 target 必须带 `source` 字段，缺失会静默返回空。

数据源认证走了个取巧的路：Infinity 的认证配置在 3.11 有 bug（UI 里 Bearer Token 选项点击跳 about:blank），干脆在 mac mini 上用 Caddy 起了一个本地代理（:8801），自动注入 `Authorization` 头转发到 CF API——认证逻辑从数据源里完全剥离，谁来访问都带 token。

## 清理与维护

顺手把积压的垃圾清了一轮：

- **Jellyfin**（已停用）：容器、镜像（1GB）、Glance 链接、UptimeKuma 监控项全部清除
- **Dashdot**（和 Grafana 功能重叠）：容器 + 镜像（212MB）删除，Glance/UptimeKuma 同步清理
- **Glance Quick Links** 重新排版：删掉图标失效的 OpenList/dPanel/1Panel/CasaOS，三组各 2 个，整齐对称
- **UptimeKuma**：删除失效的 Jellyfin/Dashdot 监控项 + Smart Home 空分组

## 总结

这一轮从"一个浏览器打不开的页面"出发，最后落成了一套完整的 homelab 基础设施：

- 内网 HTTPS 域名体系（受信证书、自动续期、局域网零配置）
- 全栈监控（系统/容器/隧道/数据库/Cloudflare 分析）
- 一次彻底的清理

最大的体会：**浏览器安全模型不是 bug，是特性**——与其和它对抗（改 hosts、关安全设置），不如顺着它把基础设施做对（内网也上 HTTPS），一劳永逸。
