---
title: Windows 与 Linux 游戏存档位置规律总结：以《How to Fish》为例
pubDate: 2026-09-06
categories:
    - tech
    - gaming
description: 以《How to Fish》为例，对比 Windows 与 Linux（Flatpak Steam）下的真实存档路径，拆解路径转换规律，并总结出通用的存档查找公式与实用技巧
---

> 在 Linux 上通过 Flatpak 安装的 Steam 玩 Windows 游戏时，存档位置常常让人困惑——它既不像原生 Linux 应用那样放在 `~/.config`，也不像在 Windows 系统中那样直观。本文以《How to Fish》为例，对比它在两个系统下的真实存档路径，总结出一个通用的查找规律，帮你快速定位任何游戏的存档。

---

## 实际路径对比

以下是《How to Fish》在两个系统上的**存档文件夹**真实路径：

| 操作系统                  | 存档路径                                                                                                                                                                |
| :------------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Windows**               | `C:\Users\reale\AppData\LocalLow\Dazed Games\How to Fish\Saves\`                                                                                                        |
| **Linux (Flatpak Steam)** | `/home/realexblue/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/4001890/pfx/drive_c/users/steamuser/AppData/LocalLow/Dazed Games/How to Fish/Saves/` |

## 规律拆解

对比两个路径，可以发现一个清晰的**路径转换规律**。Linux 下的 Flatpak Steam 路径，本质上是在模拟一个完整的 Windows 环境。

### 基础路径映射

| Windows 路径组成部分       | Linux (Flatpak Steam) 对应部分                                                                           | 说明                                                                                       |
| :------------------------- | :------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------- |
| `C:\` (系统盘)             | `/home/realexblue/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/<AppID>/pfx/drive_c/` | Flatpak 为每个游戏创建独立的"虚拟 C 盘"                                                    |
| `Users\reale` (用户文件夹) | `users\steamuser`                                                                                        | 虚拟 Windows 用户名统一为 `steamuser`                                                      |
| 后续路径                   | 后续路径                                                                                                 | **完全一致**。例如 `AppData\LocalLow\Dazed Games\How to Fish\Saves\` 在虚拟 C 盘内保持不变 |

### 关键变量

- **`<AppID>`**：每个 Steam 游戏的唯一数字 ID。例如《How to Fish》的 AppID 是 `4001890`，可以在游戏的 Steam 商店页面 URL 中找到。
- **`steamuser`**：Proton 兼容层创建的默认 Windows 用户名，用于模拟 Windows 的用户目录结构。

### 通用查找公式

基于以上规律，可以推导出**任何**通过 Flatpak Steam 游玩的 Windows 游戏的存档位置：

**Linux (Flatpak Steam) 存档路径 =**
`~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/<游戏AppID>/pfx/drive_c/users/steamuser/` + **该游戏在 Windows 上的存档相对路径**

> **关键一步**：先查游戏在 Windows 上的存档路径（[PCGamingWiki](https://www.pcgamingwiki.com/wiki/How_to_Fish) 等网站通常有记录），然后把 `C:\Users\你的用户名\` 替换成上面的虚拟路径即可。

## 补充：两个实用技巧

1.  **利用通配符查找**：不知道 AppID 时，在终端用 `find` 按游戏或开发商名称的关键词搜索：

    ```bash
    find ~/.var/app/com.valvesoftware.Steam/ -iname "*How to Fish*"
    ```

    找到的路径里就能看到 `<AppID>` 对应的目录名，套进上面的公式即可。

2.  **按修改时间倒推 AppID**：如果连关键词都不好搜（`compatdata` 下全是数字 AppID），可以按修改时间来找——每运行一次游戏，它的 `compatdata/<AppID>` 目录都会被更新，最近玩过的必然排在最前面：

    ```bash
    ls -t ~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/ | head
    ```

    从结果里挑时间最新的几个 AppID，逐个进 `pfx/drive_c/users/steamuser/AppData/` 看一眼，开发商或游戏名很快就能对号入座。

## 小结

回头看，所谓"找不到存档"，其实只是路径多了一层虚拟化：Flatpak Steam + Proton 给每个游戏建了一个独立的 Windows 前缀（`pfx`），把 `C:\`、`Users\steamuser`、`AppData` 原样装了进去。**Windows 上存档怎么放，Linux 这边就怎么找——只是前缀不同。**

通用做法只需两步：

1.  先在 [PCGamingWiki](https://www.pcgamingwiki.com/wiki/How_to_Fish) 或搜索引擎确认游戏在 Windows 下的存档路径
2.  把 `C:\Users\<用户名>\` 替换成虚拟前缀 `~/.var/app/com.valvesoftware.Steam/data/Steam/steamapps/compatdata/<AppID>/pfx/drive_c/users/steamuser/`

如果你用的是非 Flatpak 的原生 Linux Steam，去掉开头的 `.var/app/com.valvesoftware.Steam/` 即可，后面的路径完全一样。

## 参考

- [PCGamingWiki: How to Fish](https://www.pcgamingwiki.com/wiki/How_to_Fish)——本文存档路径数据来源，可按游戏名查询任意游戏的 Windows 存档位置
