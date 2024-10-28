import frontmatter
import os
import re
from datetime import datetime

# 首先你需要手动将 directory 改为你的文件夹路径
directory = "D:/Resources/GitHub/Projects/blue_wonderland/src/content/posts"

def extract_title_and_description(content):
    # 提取第一句作为 title
    title_match = re.search(r'^.*[.!?]', content, re.MULTILINE)
    title = title_match.group(0).strip() if title_match else "默认标题"

    # 提取前几句话作为 description
    description_match = re.search(r'^.*[.!?]\s*.*[.!?]', content, re.MULTILINE)
    description = description_match.group(0).strip() if description_match else "默认描述"

    return title, description

def format_front_matter(metadata):
    # 确保 front matter 的参数顺序
    front_matter = f"""---
title: {metadata['title']}
pubDate: {metadata['pubDate']}
categories: {metadata['categories']}
description: "{metadata['description']}"
---"""
    return front_matter

for filename in os.listdir(directory):
    if filename.endswith(".md"):
        file_path = os.path.join(directory, filename)

        # 读取和解析文件
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # 提取正文内容
        content = post.content

        # 创建新的 front matter
        date_published = post.get('date_published')
        pub_date_str = date_published.strftime('%Y-%m-%d') if isinstance(date_published, datetime) else date_published.split('T')[0] if date_published else ''

        # 处理 title 和 description
        title = post.get('title', '')
        description = post.get('description', '')

        if not title:
            title, _ = extract_title_and_description(content)
        if not description:
            _, description = extract_title_and_description(content)

        # 确保 categories 的格式为 ['note']
        categories = [post.get('type', 'note')]

        new_metadata = {
            'title': title,
            'pubDate': pub_date_str,
            'categories': categories,
            'description': description,
        }

        # 创建新的 Post 对象
        new_post_content = format_front_matter(new_metadata) + '\n\n' + content

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_post_content)

        print(f"Processed file: {file_path}")