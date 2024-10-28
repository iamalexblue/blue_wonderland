---
attributes:
  - trait_type: xlog_slug
    value: 2022-11-13--liang-ge--onedrive--zhang-hao-jian-wen-jian-qian-yi-zhi-bei-md
date_published: 2022-11-12T17:56:20.217Z
external_urls:
  - https://ifruit.club/2022-11-13--liang-ge--onedrive--zhang-hao-jian-wen-jian-qian-yi-zhi-bei-md
sources:
  - xlog
tags:
  - post
  - RaiDrive
  - TeraCopy
  - Windows
  - OneDrive
title: 两个 OneDrive 账号间文件迁移指北
type: note

---

# 两个 OneDrive 账号间文件迁移指北

---
title: 两个 OneDrive 账号间文件迁移指北
description: OneDrive 文件迁移指北
date: 2022-11-12T17:56:20.217Z
preview: ""
draft: false
tags:
  - RaiDrive
  - TeraCopy
  - Windows
  - OneDrive
categories:
  - 软件指南
lastmod: 2022-11-12T18:00:45.153Z
keywords:
  - RaiDrive
  - TeraCopy
  - OneDirve
slug: 两个-onedrive-账号间文件迁移指北
---

# 缘起
前几天在酷安瞎逛的时候看到有人注册成功了 MSN 邮箱，而自己作为一个邮箱收集者+半个软粉，自然是不能放过这个机会，于是在与帖主私信之后拿到了注册方法，成功注册了一个 MSN 邮箱。

注册成功之后自然就想着把现在的账号和新账号合并到一块（因为注册前想的是可以使用微软邮箱的别名功能来把两个账号合并为一个），但是在实际操作过程中发现远比自己想象中复杂，微软的别名在注销之后一个月才可以重新被注册，所以之前账号上创建的别名都得等删除完一个月之后才能再添加到新账号，于是便先作罢。

# OneDrive 间文件转移
刚好旧帐号的 Office 家庭车到了要续费的时候，就把订阅转到了新账号。但是旧帐号 OneDrive 中的数据在尝试了很多方法之后最终还是选择了挂载 RaiDrive 手动复制粘贴 。

然后就又有了一个新的问题，OneDrive 本身的下载速度在国内网络环境下是非常捉急的，刚开始是使用 Windows Explorer 复制粘贴，花了整整一天一夜才迁移了2个 G，而且 Windows Explorer 复制粘贴有一个非常恶心的问题，复制的时候，如果是包含多个文件夹，文件夹内如果有复制粘贴错误的内容（比如内容重复，文件占用无法复制的情况），它会频繁弹出窗口来问你要如何处理，但问题在于，这样的话我就需要守在电脑前等弹窗的时候手动确认，这也太不优雅了。于是便放弃了第一种方法。

然后在寻找第二种方法的时候，我发现了一个非常好用的工具，叫做 TeraCopy, 它可以在复制粘贴的时候设定文件重复、占用导致复制粘贴失败时的解决方法，你可以在复制前设置好，如果有重复文件出现就直接跳过，然后开始复制，之后的一切都是自动化的，完全不需要你自己操心，非常方便。而且在转移数据的过程中我发现：它的复制粘贴（对应 OneDrive 就是下载上传）速度还是非常快的，至少比 Windows Explorer 要快很多，你还可以设置在转移完成之后校验文件的完整性，非常贴心。

![TeraCopy](./attachments/1668274573341.png)


# 完美
至此，我的 OneDrive 中的文件已经全部转移到了新账号，接下来就等把旧帐号邮箱别名迁移到新账号，就可以把 MSN 邮箱当成主力邮箱来使用了。

如果也有 OneDrive 账号间迁移问题的朋友刚好看到这里的话，希望这些文字能对你有所帮助。