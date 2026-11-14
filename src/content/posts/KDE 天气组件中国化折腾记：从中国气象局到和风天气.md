---
title: KDE 天气组件中国化折腾记：从中国气象局到和风天气
pubDate: 2026-09-07
modDate: 2026-11-14
categories:
  - tech
  - tools
description: KDE 桌面天气组件搜不到中国城市？用 plasma-ions-china 给 KWin 装上中国气象局和和风天气两个数据源，并修复和风 JWT 认证缺失 iss 的上游 bug
lastmod: 2026-11-14T11:56:38.000Z
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

## 后记二：Plasma 6.8 又把它崩了

写完这篇不到两个月，Tumbleweed 例行把 Plasma 拉到 6.8.0，天气组件又挂了。这次比上回 401 惨得多：plasmashell 直接崩溃，整个桌面跟着消失，系统卡死到只能强制重启。急救手段很糙——把 `/usr/lib64/qt6/plugins/plasma/weather_ions/` 下的 `nmccn.so` 和 `qweather.so` 挪进收纳目录，组件数据源切回 BBC，桌面总算消停了。当时的打算是等上游适配 6.8 再说。

这次崩的根因跟认证没关系，是 KDE 6.8 动了 ion 的 API：`FutureDayForecast` 的默认构造和 `setMonthDay()`/`setWeekDay()` 都被删了，只剩 `explicit FutureDayForecast(const QDateTime &timestamp)` 一种构造方式。我的 `.so` 是拿 6.7 的头文件编的，装进 6.8 的 plasmashell 里属于 ABI 级不兼容，加载即崩，连发网络请求那步都走不到。上游在十月中的 v0.1.3 修掉了这个问题（[1d5b55e](https://github.com/arenekosreal/plasma-ions-china/commit/1d5b55ed72c22822db5c8a482f29022457674a00)，对应 [issue #6](https://github.com/arenekosreal/plasma-ions-china/issues/6)）：cmake 阶段检测 `PlasmaWeather_VERSION`，≥ 6.8.0 就加一个 `TIMESTAMP_USE_QDATETIME` 宏，代码里用 `#ifdef` 分叉出两种构造写法。更省心的是，上次 issue #5 提的 `iss` bug 也被官方吸收成了 `PLASMA_IONS_CHINA_QWEATHER_ISS` 选项（c6cc28f），本地补丁正式退役。

### 凭据丢了，从二进制里挖回来

重新编译本身很顺利，依赖包都还在，但撞上一个新问题：和风那套凭据丢了。当时的 cmake 命令没留档，KID、项目 ID、API Host 虽然都还在和风控制台里躺着，可重新登录翻一遍实在麻烦。盯着禁用时收起来的旧 `qweather.so`，我想起一件事：这些值全是 `QStringLiteral` 常量，会以 UTF-16 字符串的形式编进二进制。一条命令就能挖出来：

```bash
# -el = 提取 16-bit little-endian 字符串，正好是 UTF-16
strings -el -n 4 qweather.so | grep -E '^[A-Z0-9]{10}$|qweatherapi'
# XXXXXXXXXX   <- 10 位 ID，KID 和项目 ID 之一
# YYYYYYYYYY   <- 另一个 10 位 ID
# QZZZZZZZZZ   <- Q 开头的开发者 ID，也就是 iss
# https://xxxx.re.qweatherapi.com
```

API Host 和 Q 开头的开发者 ID 一眼就能认出来，麻烦的是剩下两个 ID——哪个是 KID、哪个是项目 ID（sub），看不出来。干脆实测：用 Python 的 `cryptography` 库照 ion 的同款逻辑拼 JWT（Ed25519 签名、base64url 编码、`iat`/`exp` 直接抄源码默认值），拿两个 ID 的两种排列分别打一遍 GeoAPI，返回 200 的那个排列就是答案。顺手还验证了这套凭据隔了两个多月依然活着，省得白编译一轮。

### kwriteconfig6 的新坑

装好新 `.so`，最后一步是把组件配置里的 `provider` 从 `bbcukmet` 切回 `qweather`。想着 `kwriteconfig6` 有 `--group` 参数，按老写法来：

```bash
kwriteconfig6 --file plasma-org.kde.plasma.desktop-appletsrc \
  --group "Containments][26][Applets][143][Configuration][WeatherStation" \
  --key provider qweather
```

结果 KF6 已经不认 `A][B` 这种嵌套写法了：原来的组一个字没动，反倒往文件末尾追加了一个满是 `\x5d` 转义的垃圾组。KF6 里嵌套组得一层一个 `--group` 地传。我的修法更简单粗暴：停掉 plasmashell，用 sed 或 python 直接替换文件里那两行 `provider=`，再启动。对 appletsrc 这种大嵌套 INI，直接改文件其实比 kwriteconfig6 更可控。

### 这次是备份脚本救的场

整个过程我一点不慌，因为动手前后各打了一份快照——之前写的备份小脚本会把 `plasma-org.kde.plasma.desktop-appletsrc`、`plasmashellrc`、`plasmarc`、`kwinrc`、`kglobalshortcutsrc`、`kdeglobals` 六个核心配置拷进 `~/.local/state/plasma-config-backups/<时间戳-标签>/`，还顺手记一份当时装了哪些第三方部件的清单。真出事就 `plasma-config-restore`：它会停掉 plasmashell、回填文件、再拉起来，覆盖前还会把现场另存一份 pre-restore 副本，反悔都留了后路。Plasma 大版本升级后折腾组件的风险高了一档，这种习惯这时候就显出价值了。

重启之后，面板和托盘两个天气组件都正常吐出了惠州的天气，plasmashell 一直没再崩过。回头看，这次崩溃就是"旧插件遇上新桌面"的 ABI 级不兼容，配置层面没得救，只能等上游适配后重新编译。所以如果你也装了这套 ion，记得 Plasma 大版本升级后要跟着重编——别学我，先崩一次桌面才想起来。
