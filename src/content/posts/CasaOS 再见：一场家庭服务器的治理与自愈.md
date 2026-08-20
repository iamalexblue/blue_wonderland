---
title: CasaOS 再见：一场家庭服务器的治理与自愈
pubDate: 2026-08-21
categories:
    - tech
    - homelab
    - devops
description: 从卸载 CasaOS 开始，把家庭服务器彻底治理了一遍：容器迁入 Dockge、数据库正名、cloudflared 自动更新、路由器告别每天定时重启，最后把一切收进 dotfiles
lastmod: 2026-08-21T12:00:00.000Z
---

> 从卸载 CasaOS 开始，我把家庭服务器彻底治理了一遍：容器全部迁入 Dockge、数据库正名、cloudflared 自动更新、路由器告别每天定时重启，最后把整套"自愈体系"收进了 dotfiles。

---

## 起因：一个越用越难受的面板

CasaOS 是我早期折腾 NAS 类似物时的懵懂尝试——那时候觉得有个图形面板管理 Docker 很酷。后来它越来越让我难受：

1. **侵入性很强**：明明只是系统里的一个程序，却在主机上装了 7-8 个 systemd 服务（网关、消息总线、用户服务、本地存储、应用管理，还有 rclone 和 devmon）
2. **不是它商店装的容器，一律显示为"旧应用程序"**——每次打开 UI 都像在看一个不欢迎你的房东
3. **在 UI 里卸载单个应用，默认勾选删除用户数据**——一个手滑就是数据灾难

决定卸载。但卸载不是删个程序那么简单——**先评估，再动手**。

## 评估：卸载前必须想清楚的事

### 影响面盘点

CasaOS 虽然烦人，但它管着 9 个容器（Grafana、Nextcloud、Plex、qBittorrent、Syncthing、UptimeKuma、PostgreSQL 等）。卸载前必须确认：**这些容器会不会陪葬？**

查下来全是好消息：

- **容器由 Docker 守护进程管理**，restart policy 全是 `always`/`unless-stopped`，CasaOS 只是"编排 UI"，卸载后容器照常运行
- **数据都在 bind mount**（`/DATA/AppData/`），在根文件系统上，没有独立挂载，卸载脚本默认不碰
- **SMB 共享在 mac 本机**（smbd 监听 445），和 VM 里的 CasaOS 毫无关系
- 公网隧道（cloudflared）、Prometheus、Miniflux、Glance 全是独立 systemd 服务

### 官方卸载脚本的三个问题

CasaOS 自带官方卸载器（`casaos-uninstall`），但它会交互式问你三个问题：

1. `Do you want delete all containers?` → **N**（删了全完）
2. `Do you want delete all images?` → **N**
3. `Do you want delete all AppData of CasaOS?` → **N**（这条答 Y，`/DATA/AppData` 整体删除——数据库、Nextcloud 全没）

> **结论**：三个问题全答 N，卸载就是安全的。备份（compose 目录 + 数据库 + 配置，双份）之后再执行。

## 执行：一次"有惊无险"的卸载

卸载脚本从 `/dev/tty` 读输入，非交互环境会卡住，我写了个 expect 脚本自动应答 N N N。过程中还踩了个小坑：**pkill 会匹配到执行命令的 shell 自身**，把自己杀了——换成精确 PID 才搞定。

卸载完成后的验证清单：

| 验证项                         | 结果                  |
| ------------------------------ | --------------------- |
| 9 个 Docker 容器               | ✅ 全部运行中，无重启 |
| `/DATA/AppData` 数据           | ✅ 完好               |
| 公网域名（next/miniflux/home） | ✅ 全部 200           |
| 23333 端口（CasaOS UI）        | ✅ 已释放             |

善后：rclone 是 CasaOS 的组件（不是我自己装的），二进制 47MB 一起清掉。**"旧应用程序"的烦恼随着 UI 一起消失了。**

## 延伸：顺手做的一串正名与升级

### cloudflared：升级 + 月度自动更新

Cloudflare 提示我本地的 cloudflared（2025.7.0）落后超过一年不再受支持。升级到 2026.8.2（dpkg 平滑升级，旧版二进制备份留作回滚），然后配了一个 **systemd timer 月度自动更新**：

```
每月 1 日 03:30 检查 GitHub 最新版
├─ 版本号逐段比较（避开 2026.10.1 < 2026.9.1 的字符串陷阱）
└─ 有新版 → 下载 deb → dpkg 安装 → 重启隧道
```

### VM 改名：CasaOS → orb-debian

机器名还叫 CasaOS，看着就烦。`orbctl rename`（OrbStack 官方支持）+ `hostnamectl` 双管齐下，所有 `orb -m CasaOS` 命令变成 `-m orb-debian`。

### 数据库正名：casaos 库其实是 Nextcloud 的

盘点 PostgreSQL 时发现一个"历史误会"：那个叫 `casaos` 的 69MB 数据库，里面全是 `oc_` 前缀的表——**它是 Nextcloud 的数据库**（CasaOS 安装 Nextcloud 时默认把库名起成了 casaos）。

改名流程：停 Nextcloud → 断开连接 → `ALTER DATABASE casaos RENAME TO nextcloud` → 改 `config.php` 的 `dbname` → 重启验证，数据零丢失。

## 接管：Dockge 与容器大迁移

CasaOS 走了，容器管理得有个新家——**Dockge**（UptimeKuma 作者出品，纯 compose 文件管理，所见即所得）。

### 部署

Docker 容器部署，配了局域网域名 `dockge.iamalex.blue`（CF DNS A 记录直连内网 + acme.sh DNS-01 证书 + Caddy 反代，和 home.iamalex.blue 同一套模式）。

### 迁移 7 个容器

| 容器                                                 | 迁移方式                                                            | 风险                    |
| ---------------------------------------------------- | ------------------------------------------------------------------- | ----------------------- |
| grafana / nextcloud / plex / qbittorrent / syncthing | 复制 compose + 清理 CasaOS 残留 + down/up                           | 低（数据在 bind mount） |
| PostgreSQL                                           | 同上（顺手把项目名从随机名 `resilient_davide` 正名为 `postgresql`） | 低                      |
| uptimekuma                                           | docker run 逆向写 compose                                           | 低（数据在 bind mount） |

### 三个坑

1. **plex 起不来**：compose 里配了 `/dev/dri` 硬件直通，但 VM 里没有 GPU 设备——去掉 devices 配置，软件转码照样跑
2. **nextcloud 500**：CasaOS 的 compose 模板里 redis 密码是占位符，而我把脱敏显示（`[redacted]`）当成了真实值——实际密码是 `nextcloud`。改对重建后恢复
3. **dockge 账号差点丢了**：Dockge 数据在匿名卷里，容器重建会丢账号——先迁移到命名卷再改容器名，数据完好

### 两个"不迁"的决策

- **redis**：纯基础设施（nextcloud 的缓存），Dockge 里管理它没有收益，迁移还要动网络拓扑（`nextcloud_redis`），风险大于收益
- **dpanel**：和 Dockge 功能重叠的 Docker 面板——**留着反而有价值**，万一 Dockge 出问题它还能兜底

> **结论**：不是所有容器都要归 Dockge 管。基础设施保持稳定，管理工具留个冗余，比"看起来统一"更重要。

## 自愈：让路由器告别每天重启

### 痛点

iStoreOS 路由器长时间不重启网络就会挂掉，所以我之前设置了**每天凌晨 5 点定时重启**。代价是：**每天收一封 uptimekuma 的宕机报警邮件**，烦不胜烦。

### 方案：按需重启

思路很简单：**网络正常就不动，网络挂了才重启**。在 VM 上跑一个检测脚本（systemd timer 每 3 分钟触发）：

```
每 3 分钟：ping 阿里/腾讯/114 三个国内 DNS（任一可达即正常）
├─ 正常 → 什么都不做，零打扰
└─ 连续 2 次失败（6 分钟）→ 全面确认
    ├─ 确认网络恢复 → 取消，重置计数
    └─ 确认真挂了 → SSH 重启路由器 → 10 分钟冷却防连环重启
```

| 场景           | 之前                             | 现在               |
| -------------- | -------------------------------- | ------------------ |
| 网络正常       | 每天 5 点照常重启 → 每天一封报警 | 零操作、零报警     |
| 网络真挂了     | 等到第二天 5 点才重启            | ~7 分钟内自动恢复  |
| 路由器完全卡死 | 无解                             | 记日志提示人工断电 |

> **优雅的运维是"平时安静，故障才动作"**——报警邮件应该是真正的信号，而不是每天例行的噪音。

### 配套：DHCP 主备切换

顺手看了下路由器上原本就有的 `check_surge.sh`：它每分钟探测 mac mini 的 Surge，在线时关闭路由器 DHCP（由 Surge 接管分配）、离线时开启（备份模式）——**一套现成的 DHCP 主备切换**，和智能重启互补：各管各的故障域，互相兜底。

### net-stats：一键查看双守护状态

最后写了个 `net-stats` 命令：Windows PowerShell 函数 + Linux zsh 别名，一键看到智能重启的 timer 状态、失败计数、冷却状态、日志，以及 DHCP 主备切换的实时状态——**两个守护脚本的运行情况一目了然**。

## 沉淀：把一切收进 dotfiles

治理完的成果不能只活在服务器里，全部收进 dotfiles 仓库：

- `scripts/`：**网络守护三件套**（router-smart-reboot.sh / net-stats.sh / check_surge.sh）
- `sshconfig/`：`~/.ssh/config` 托管
- `.gitignore`：私钥、authorized_keys、known_hosts、1Password 全部防护在外——**配置可以入库，凭据永不入库**
- README 同步更新

## 结尾：基础设施的"整洁"是一种幸福感

回头看这一天：从"越用越难受的 CasaOS"开始，到"井井有条的 Dockge + 自愈脚本"结束。收获不只是卸载了一个面板：

- 容器有了统一的家（Dockge），数据库有了正确的名字（nextcloud）
- 路由器从"每天例行重启"变成"故障才动作"的自愈节点
- 两个守护脚本的状态一个命令就能看到
- 整套体系收进了 dotfiles，Windows 和 Linux 双端一致

**折腾的意义，大概就是让基础设施安静下来**——平时感觉不到它的存在，需要它的时候，它已经自己处理好了。
