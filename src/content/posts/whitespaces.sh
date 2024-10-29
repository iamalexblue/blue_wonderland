#!/bin/bash

# 定义文件列表
files=(
  "D:\Resources\GitHub\Projects\blue_wonderland\src\content\posts\Notion AI 🙈cool.md"
  "D:\Resources\GitHub\Projects\blue_wonderland\src\content\posts\Spotify 年度总结.md"
  "D:\Resources\GitHub\Projects\blue_wonderland\src\content\posts\嘿，这里有一条好消息需要查收！ .md"
  "D:\Resources\GitHub\Projects\blue_wonderland\src\content\posts\因为别人而爱自己.md"
  "D:\Resources\GitHub\Projects\blue_wonderland\src\content\posts\毁灭吧.md"
  "D:\Resources\GitHub\Projects\blue_wonderland\src\content\posts\王菲与我共同度过的 1,222 分钟.md"
  "D:\Resources\GitHub\Projects\blue_wonderland\src\content\posts\苹果键盘难用.md"
)

# 遍历文件列表并修复不规则空白字符
for file in "${files[@]}"; do
  sed -i 's/[[:space:]]\+/ /g' "$file"
done