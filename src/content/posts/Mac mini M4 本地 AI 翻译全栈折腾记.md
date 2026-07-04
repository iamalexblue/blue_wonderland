---
title: Mac mini M4 本地 AI 翻译全栈折腾记
pubDate: 2026-07-05
categories:
  - note
description: 从零开始在 Apple Silicon 上部署本地大模型，接入浏览器划词翻译，并一路优化到开机自愈
lastmod: 2026-07-04T17:40:12.105Z
---

> 从零开始在 Apple Silicon 上部署本地大模型，接入浏览器划词翻译，并一路优化到开机自愈。

---

## 背景

手上是一台 Mac mini M4，16GB 内存。日常翻译需求密集——中英互译为主，偶尔日韩德法。

之前一直用某云翻译 API，每月烧钱不说，网络延迟还时好时坏。刚好 MLX 生态日渐成熟，决定在本地跑一个。

## 第一天：环境铺路

### Shell 配置合并

有两份 `.zshrc`：一份是本机旧配置，一份是从别的机器带过来的新配置。后者结构更清晰（中文注释、分节明确），决定以它为基底，把本机的 macOS 专属配置（iTerm2、Google Cloud SDK、AI Workspace 路径）移植进去。

合并后的配置分九大区块：

```
1. 路径与核心加载       5. 代理管理
2. Oh My Zsh 功能开关   6. macOS 专属
3. 插件配置             7. AI Workspace
4. 用户自定义配置       8. 工具别名
                        9. Linux 专属（注释）
```

### 代理双轨

手上有两个代理：Surge（主）和 Mihomo（备）。设计了一套命令体系：

```bash
$ pon              # 默认开 Surge，自动检测 10.10.10.10:6152 是否可达
[✔] Surge Proxy Enabled (HTTP http://10.10.10.10:6152 | SOCKS socks5://10.10.10.10:6153)
[✔] Surge → 10.10.10.10:6152 可达

$ pon mihomo       # 切到 Mihomo
[✔] Mihomo Proxy Enabled (http://10.10.10.10:7890)
[✔] Mihomo → 10.10.10.10:7890 可达

$ poff             # 关闭，自动测直连是否正常
[✘] Surge Proxy Disabled
[✔] 直连正常 (Google 可达)

$ pst              # 查看当前状态
```

同时加了 `no_proxy`，让 `hf-mirror.com` 和 `modelscope.cn` 绕过代理直连——下一节会说明为什么这一步至关重要。

### Hugging Face 怎么办？

在国内访问 `huggingface.co` 极其痛苦。配置了 `HF_ENDPOINT=https://hf-mirror.com` 作为镜像，并写死到 `~/.zshrc` 的 AI Workspace 区块中，以后所有 HF 下载自动走国内 CDN。

## 第二天：模型拉锯战

### 14B 的教训

首选 `Qwen3-14B-4bit`（8.3GB），理论上翻译质量最好。

用 `uv run mlx_lm.generate` 自动下载。走了镜像、开了代理，结果 Surge 把 `hf-mirror.com` 的流量劫持到新加坡专线，策略中途切换导致连接被直接掐断。关了代理，镜像服务器本身也不稳定，速度在 0~96 MB/s 之间反复横跳。

最终用 **aria2** 16 线程硬拉下来了，平均速度 15 MB/s。7.8 GB 的模型文件，在反复的重试和续传中总算下完。

跑起来的瞬间：**内存吃满 8.4 GB**，16GB 机器的剩余空间寥寥无几，随便开个 Chrome 就开始 swap。

结论：14B 对翻译场景属于性能溢出，对 16GB 机器则是内存灾难。删了。

### 8B 甜点

`Qwen3-8B-4bit`：4.3 GB 存储，约 4.5 GB 内存。翻译质量跟 14B 差距不大，但空出一倍的 RAM。

也是 aria2 一本道下完。这次学聪明了：

- 小文件用 `curl -sL`（跟重定向）
- 大文件用 `aria2c -x 16 -s 16`（多线程）
- 同时处理，互不阻塞

## 第三天：服务化管理

### mlx CLI

裸用 `mlx_lm.server` 太原始。写了一个 `mlx` 命令：

```bash
mlx serve qwen8b     # 启动
mlx stop             # 停止
mlx status           # 状态
mlx chat "翻译成日文：你好"    # 终端直聊
mlx log              # 日志
mlx models           # 模型列表
mlx register <name> <path>    # 注册新模型
```

模型路径通过 `~/.config/mlx/models.conf` 注册表管理，按名称解析：

```
qwen8b = $HOME/AI/models/Qwen3-8B-4bit
```

### launchd 守护

不想每次重启手动启动服务。用 macOS 原生 launchd 做守护：

- `RunAtLoad: true` — 开机自启
- `KeepAlive: true` — 崩溃后 5 秒自动拉起

实现方式：一个 wrapper 脚本从 `~/.config/mlx/current` 读取当前活跃模型，launchd 调用 wrapper。`mlx serve <name>` 写入模型名并 `launchctl load`，`mlx stop` 执行 `launchctl unload`。

验证：`kill -9` 杀掉进程，6 秒后服务自动恢复。

### 预热

首次推理需要把模型从内存加载到 GPU，可能等好几秒。在服务就绪后自动发一个 `max_tokens=1` 的哑请求：

```
Warming up... ready
```

之后的第一条真实翻译请求就是秒回了。

## 第四天：接入翻译工作流

### Kiss Translator

浏览器端用的是 [Kiss Translator](https://github.com/fishjar/kiss-translator)，它支持自定义 API v2 的 Hook 模式。

坑点：Kiss Translator 的扩展引擎不兼容 `?.` 可选链语法，必须用纯 ES5 写 Hook。

**Request Hook：**

```js
async (args) => {
  const systemPrompt = args.systemPrompt || args.nobatchPrompt
    || 'You are a professional translator. Translate the following text. Output ONLY the translation.'
  let userContent = args.userPrompt || ''
  if (!userContent && args.texts && args.texts.length > 0) {
    userContent = args.texts[0]
  }
  const body = {
    model: '$HOME/AI/models/Qwen3-8B-4bit',
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userContent }
    ],
    max_tokens: 4096,
    stream: false,
    chat_template_kwargs: { enable_thinking: false }
  }
  return { url: args.url, body, headers: { 'Content-Type': 'application/json' }, method: 'POST' }
}
```

**Response Hook：**

```js
async (context) => {
  let content = ''
  try {
    const res = context.res
    if (res && res.choices && res.choices[0] && res.choices[0].message) {
      content = res.choices[0].message.content || ''
    }
  }
  catch (e) {}
  return { translations: [[content]] }
}
```

关键参数：`chat_template_kwargs: { enable_thinking: false }`。Qwen3 默认有"思考链"，会先在 `reasoning` 字段中输出推理过程，消耗 token。翻译场景不需要思考，关了之后直接出译文。

### 局域网共享

服务器绑定 `0.0.0.0:8080`，同网段设备直连 `10.10.10.10:8080`。

Kiss Translator 配置统一填 `10.10.10.10`，本机走回环零开销，配置文件同步到 Windows 后也原封不动能用。

### 翻译实测

```
[中→英] 北京是中国的首都，有三千多年的历史
→ Beijing is the capital of China and has a history of more than three thousand years.

[中→韩] 今天的天气非常好
→ 오늘의 날씨가 매우 좋습니다.

[中→法] 这道菜的做法很简单
→ La recette de ce plat est très simple.

[中→日] 人工智能正在改变我们的生活方式
→ 人工知能は私たちの生活様式を変えつつあります。
```

## 收尾：Git 备份与开源

把所有配置收集到 git 仓库，去硬编码：

```bash
# 替换所有 /Users/alexblue → $HOME
sed -i '' 's|/Users/alexblue|$HOME|g' config/*
```

提交到 GitHub 并设为公开仓库。加了中英文双向切换的 README。

```
https://github.com/iamalexblue/ai-workstation
```

## 关键数据

| 指标       | 值                                   |
| ---------- | ------------------------------------ |
| 模型       | Qwen3-8B-4bit (MLX)                  |
| 模型大小   | 4.3 GB                               |
| 运行时内存 | ~4.5 GB                              |
| 推理速度   | ~10.9 tokens/s (生成)                |
| 翻译质量   | 中英日韩德法均可用                   |
| 开机自启   | launchd `RunAtLoad` + `KeepAlive`    |
| 崩溃恢复   | 5 秒自动拉起                         |
| API 格式   | OpenAI 兼容 (`/v1/chat/completions`) |

## 教训

1. **HF 下载稳定性是最大瓶颈**。aria2 多线程 + 国内镜像 + `no_proxy` 三件套缺一不可。别指望 Python 自带下载器。
2. **不要用超出硬件能力的模型**。14B 质量高但在 16GB 机器上性价比极低，8B 是甜点。
3. **ES5 兼容性是 Web 扩展的隐藏坑**。`?.`、`??`、箭头函数、模板字符串——能在扩展里炸的全炸过一遍。
4. **launchd 比 nohup 优雅太多**。开机自启、崩溃自愈、日志管理全部原生支持，零依赖。
5. **`enable_thinking: false` 是 Qwen3 做翻译的关键开关**。不开的话思考链吃光 token，永远看不到译文。
