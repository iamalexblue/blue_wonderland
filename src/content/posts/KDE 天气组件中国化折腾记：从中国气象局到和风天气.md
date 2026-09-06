---
title: KDE 天气组件中国化折腾记：从中国气象局到和风天气
pubDate: 2026-09-07
categories:
  - tech
  - tools
description: KDE 桌面天气组件搜不到中国城市？用 plasma-ions-china 给 KWin 装上中国气象局和和风天气两个数据源，并修复和风 JWT 认证缺失 iss 的上游 bug
lastmod: 2026-09-06T22:41:13.820Z
date: 2026-09-06T22:41:12.359Z
---

> KDE 桌面天气组件默认只带 wetter.com、NOAA 这些国外数据源，搜中国城市几乎无果。本文记录把 [plasma-ions-china](https://github.com/arenekosreal/plasma-ions-china) 编译装上、接入中国气象局（nmccn）与和风天气（qweather）两个数据源的全过程，含编译踩坑和一个必须修的上游 bug。

---

## 起因：KDE 天气组件搜不到中国城市

Plasma 桌面的天气组件（org.kde.plasma.weather）本身挺好用，问题出在它的"数据源"上——KDE 管这玩意儿叫 Ion，默认只带国外服务：BBC、德国气象局、NOAA、wetter.com。搜索框里敲中文城市名基本一无所获，偶尔匹配到一两个，预报也糙得没法看。

社区其实早有解，就是 **plasma-ions-china**，一个专给中国用户准备的 KDE 天气数据源集合，里面有两个 Ion：

| Ion        | 数据源               | 需要 API Key | 特点                                       |
| ---------- | -------------------- | :----------: | ------------------------------------------ |
| `nmccn`    | 中国气象局（nmc.cn） |      否      | 匿名可用、覆盖全国、实况+7天+预警          |
| `qweather` | 和风天气             |      是      | 官方 API、数据维度多（实况/7天/指数/预警） |

我的 Plasma 是 6.7.4，走"modern ion"路线（KDE ≥ 6.5）。

## 编译安装：依赖比想象中多

openSUSE 没有现成包（repology 上只有 Arch/Gentoo 有），只能自己编译。项目用 CMake，依赖比想象中多，光开发包就装了一堆：

```bash
# openSUSE Tumbleweed 包名
sudo zypper install -y \
  kdeplasma6-addons-devel \    # 提供 libplasmaweatherion 头文件和库
  kf6-extra-cmake-modules \
  kf6-kcoreaddons-devel \
  kf6-kunitconversion-devel \
  kf6-ki18n-devel \
  qt6-base-devel \
  qt6-declarative-devel        # 提供 Qt6Qml（weather data 组件依赖）
```

依赖装齐，编译本身倒是很顺利：

```bash
git clone https://github.com/arenekosreal/plasma-ions-china.git
cd plasma-ions-china
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)
sudo cmake --install build
```

装完两个 `.so` 会落在 KDE 插件目录：

```bash
$ ls /usr/lib64/qt6/plugins/plasma/weather_ions/
bbcukmet.so  dwd.so  envcan.so  nmccn.so  noaa.so  qweather.so  wettercom.so
```

气象局那个（nmccn）匿名访问 nmc.cn，**零配置直接能用**，装上就能在天气组件里搜到城市。和风就没这么省心了，后面细说。

> 顺手记一个坑：一开始我图省事 `git clone --depth 1`，结果 cmake 直接报错 `Invalid tag`——项目会拿 `git describe --tags` 自动取版本号，浅克隆没有 tag 就罢工。拉个正式 tag 再构建就好：

```bash
git fetch origin tag v0.1.1
git checkout v0.1.1
```

## 接入和风：先弄明白它的认证

气象局那个装上就能用，和风这个就不太对劲了。qweather 走的是新版 **JWT + Ed25519 签名**认证，不是填个 API Key 就能用，前后要凑齐四样东西：

1. **Ed25519 密钥对**

```bash
openssl genpkey -algorithm ED25519 -out ed25519-private.pem
openssl pkey -pubout -in ed25519-private.pem > ed25519-public.pem
```

2. **去和风控制台注册**，拿到三个 ID：

| CMake 参数          | 填什么   | 去哪看                                         |
| ------------------- | -------- | ---------------------------------------------- |
| `QWEATHER_KID`      | 凭据 ID  | 控制台 → 项目管理 → 凭据                       |
| `QWEATHER_SUB`      | 项目 ID  | 控制台 → 项目管理 → 项目                       |
| `QWEATHER_API_HOST` | API Host | 控制台 → API Host（`xxxx.re.qweatherapi.com`） |

> 顺手提醒：和风的 **API Host 藏得比较深**，不在项目管理页，得去控制台设置页面的开发者信息页面找，而且每个账号是专属域名。

然后带着这些重新 cmake 配置：

```bash
cmake -B build -S . -DCMAKE_BUILD_TYPE=Release \
  -DPLASMA_IONS_CHINA_QWEATHER_PRIVATE_KEY=$HOME/.config/qweather/ed25519-private.pem \
  -DPLASMA_IONS_CHINA_QWEATHER_KID="你的凭据ID" \
  -DPLASMA_IONS_CHINA_QWEATHER_SUB="你的项目ID" \
  -DPLASMA_IONS_CHINA_QWEATHER_API_HOST="你的专属host"
cmake --build build
sudo cmake --install build
```

## 卡了半天：搜索没结果

KID、SUB、API Host 全配好了，搜索还是毫无结果，翻日志也只有一句模棱两可的网络错误，看不出个所以然。

排查到后面，我干脆拿私钥手动拼 JWT，直接打它的 API 做对比，这一测问题就藏不住了：

- payload 里带 `iss` → **HTTP 200**，城市数据正常返回
- 不带 `iss` → **HTTP 401 Unauthorized**

和风 2025 年后改过认证，JWT 的 payload 强制要三个身份字段：`iss`（开发者 ID）、`sub`（项目 ID），再加 `iat`/`exp` 两个时间戳。而 plasma-ions-china 的 `getJwtToken()` 里**只写了 `sub`、`iat`、`exp`，漏了 `iss`**。等于所有请求必然 401，搜索当然没结果；plasmashell 崩溃大概率也是 401 触发了 ion 里那段网络错误的重试逻辑，处理不干净就崩了。

这是上游的 bug，顺手打了个补丁：CMakeLists 加一个 `PLASMA_IONS_CHINA_QWEATHER_ISSUER` 选项（填开发者 ID，形如 `Q` + 10 位，控制台 → 设置里看），代码里 payload 补上 `iss` 字段：

```cpp
QJsonObject payload;
payload[QStringLiteral("iss")] = QStringLiteral(ISSUER); // 补上的
payload[QStringLiteral("sub")] = QStringLiteral(SUB);
```

重新编译安装后，天气组件搜索立刻正常，任意城市都能返回一串候选，预报也拉得到。

## 验证：怎么确认 Ion 真的被 KDE 认了

装完别急着信，两步确认 KDE 真的认了：

**1. 装 `plasma-sdk`，用 `plasmoidviewer` 直接跑天气组件**：

```bash
sudo zypper install -y plasma6-sdk
plasmoidviewer -a org.kde.plasma.weather
```

搜索城市，能出结果。

**2. 排查问题时开 ion 自己的调试日志**（比反复点组件高效太多）：

```bash
QT_LOGGING_RULES="org.kde.weather.ion.qweather.debug=true" plasmoidviewer -a org.kde.plasma.weather
```

`org.kde.weather.ion.nmccn` 同理。这次排查 401 就是靠日志确认请求被拒，再拿私钥手动构造 JWT 打 API 才定位到缺 `iss` 的。

## 小结

折腾完桌面终于有了趁手的天气组件。几点沉淀：

- **中国用户修 KDE 天气，plasma-ions-china 是标准答案**：中国气象局匿名免配置，和风天气要注册但要的是 JWT 密钥对不是 API Key
- **JWT 401 先查 payload 字段全不全**，和风 2025 认证改版后 `iss` 是硬性要求
- **Ion 插件没生效先枚举再 E2E**，KPluginMetaData 和 QPluginLoader 都能在命令行里验证，不用反复重启桌面
- 修的上游 bug（缺 `iss`）已经提了 [issue](https://github.com/arenekosreal/plasma-ions-china/issues/5)，等作者合并前先本地打补丁用着

> 后记：这 bug 属于"新用户必踩"那种——只要和风还强制 `iss`，每个新配 qweather 的人都会撞上 401。如果你的发行版打包的是旧版 plasma-ions-china，用之前记得确认有没有这个修复。
