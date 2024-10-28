---
attributes:
  - trait_type: xlog_slug
    value: Markdown-shi-li---ru-he-kuai-su-ru-men-Markdownmd
date_published: 2021-11-01T15:33:19.495Z
external_urls:
  - https://ifruit.club/Markdown-shi-li---ru-he-kuai-su-ru-men-Markdownmd
sources:
  - xlog
tags:
  - post
title: Markdown 示例 - 如何快速入门 Markdown
type: note

---

# Markdown 示例 - 如何快速入门 Markdown

---
title: Markdown 示例 - 如何快速入门 Markdown
date: 2021-11-01T15:33:19.495Z
draft: false
lastmod: 2022-07-22T16:33:50.231Z
slug: markdownuili-ruhekksurumf
description: 这是一篇示例文章，测试 Markdown 展示效果。
---


# Markdown 示例 - 如何快速入门 Markdown

> 这是一篇示例文章，测试 Markdown 展示效果。

---

## 一、.Markdown 标题

Markdown 支持两种标题的语法：Setext 形式和 Atx 形式

### 1. Setext 形式

Setext 形式是用底线的形式，利用 = （最高阶标题）和 - （第二阶标题）

例如：

![图片.png](./attachments/WwRJxJQYN.png)

### 2. Atx 形式

Atx 形式在行首插入 1 到 6 个 # ，对应到标题 1 到 6 阶。

例如：

```Markdown
# 一级标题
## 二级标题
### 三级标题
#### 四级标题
##### 五级标题
###### 六级标题
```

![图片.png](./attachments/CWnf7de86.png)

标题的使用在 Markdown 使用中非常频繁，一般以自己使用习惯来就行，不过大部分软件都支持第二种 `#` 类型的标题样式，第一种平常用的偏少。

## 二、区块引用

区块引用则使用 email 形式的 '>' 角括号。

    例如：
    > 引用
    > 
    > > 引用中的引用
    >
    > ## 引用中的标题

> 引用

> > 引用中的引用

### 引用中的标题


Markdown 使用星号和底线来标记需要强调的区段。单标记表示斜体，双标记表示粗体

```markdown
例如：
使用单星号： *星号斜体*
使用单下划线： _下划线斜体_
使用双星号： **星号粗体**
使用双下划线： __下划线粗体__
删除线：～～删除线～～
```

- 使用单星号： _星号斜体_  
- 使用单下划线： __下划线斜体__
- 使用双星号： **星号粗体**  
- 使用双下划线： **下划线粗体**  
- 删除线：~~删除线~~

## 三、无序列表

无序列表：使用星号（*）、加号（+）和减号（-）来做为列表的项目标记

    星号、加号、减号：
    * Candy.
    + Gum.
    - Booze.

* Candy.
* Gum.
* Booze.

## 四、有序列表

有序列表：使用一般的数字接着一个英文句点作为项目标记，数字不能省略但可无序，点号之后的空格不能少

```markdown
1. Red
2. Green
3. Blue
```

1.  Red
2.  Green
3.  Blue

## 五、嵌套列表:  

`-` 、`+` 、`*`  可循环使用，但符号之后的空格不能少，符号之前的空格也不能少

    - 嵌套列表1
    + 嵌套列表1a
    + 嵌套列表1b
    - 嵌套列表1ai
    	* 嵌套列表1aix
    	- 嵌套列表2

- 嵌套列表 1
  + 嵌套列表 1a
    + 嵌套列表 1ai
      *   嵌套列表 1aix
  + 嵌套列表 1b
- 嵌套列表 2



三个或更多 -\_\*，必须单独一行，可含空格（注意如果在文字后使用 ---，则为副标题）

> 此外有序列表和无序列表有多级的话也可以通过 `Tab` 和 `Shift` + `Tab` 缩进实现。

## 六、插入链接

在 Markdown 中，插入链接不需要其他按钮，你只需要使用`[显示文本](链接地址)` 这样的语法即可，例如：

    文字超链：[GitHub](http://www.github.com)
    索引超链：
    [Google][1] [1]:http://www.google.com
    自动链接：http://www.google.com 
    邮箱链接：<myemail@email.com>

文字超链： [GitHub](http://www.github.com/)

索引超链： [Google](http://www.google.com/)

自动链接：[http://www.google.com](http://www.google.com/)

邮箱链接：myemail@email.com



## 七、图片超链

在 Markdown 中，插入图片不需要其他按钮，你只需要使用 `![image](https://xxx.jpg]` 这样的语法即可，例如：

    ![congjinyebaiya](./attachments/srP9RSsrv.png)

![Markdown 示例](./attachments/3GT94I5Yb.png)

> 注：插入图片的语法和链接的语法很像，只是前面多了一个 ！。\*

## 八、代码块

    `字符`（简短文字添加代码框）
    `Tab`或四个空格（大段文字添加代码框，每行前添加）

`字符`  
`Tab或四个空格`

## 九、大段代码块

在你的代码块的前面和后面都加上三个反引号 \` 即可，在第一行后指定编程语言，也可以不指定

    @requires_authorization
    def somefunc(param1='', param2=0):
        '''A docstring'''
        if param1 > param2: # interesting
            print 'Greater'
        return (param2 - param1 + 1) or None
    class SomeClass:
        pass
    >>> message = '''interpreter
    ... prompt'''

## 十、特殊符号

特殊符号前可以加反斜线表示转义

    \\ 反斜杠
    \` 反引号
    \* 星号
    \_ 下划线
    \{\} 大括号
    \[\] 中括号
    \(\) 小括号
    \+ 加号
    \- 减号
    \. 英文句号
    \! 感叹号



- \\ 反斜杠
- \` 反引号
- \* 星号
- \_ 下划线
- \{\} 大括号
- \[\] 中括号
- \(\) 小括号
- \+ 加号
- \- 减号
- \. 英文句号
- \! 感叹号

## 十一、表格

* 使用 | 来分隔不同的单元格，使用 - 来分隔表头和其他行：

```Markdown    
name | age   区分单元格
---- | ---         分隔表头和其他行
LearnShare | 12
Mike | 32
```

| name       | age  |
| ---------- | ---- |
| LearnShare | 12   |
| Mike       | 32   |


*   为了美观，可以使用空格对齐不同行的单元格，并在左右两侧都使用来标记单元格边界：

```Markdown
| name       | age |
| ---------- | --- |
| LearnShare | 12  |
| Mike       | 32  |
```

| name       | age  |
| ---------- | ---- |
| LearnShare | 12   |
| Mike       | 32   |


*   在表头下方的分隔线标记中加入 :，即可标记下方单元格内容的对齐方式：

```Markdown
| left | center | right |
| :--- | :----: | ----: |
| aaaa | bbbbbb | ccccc |
| a | b | c |
```

| left | center | right |
| :--- | :----: | ----: |
| aaaa | bbbbbb | ccccc |
| a    |   b    |     c |

## 十二、分隔线
 
```markdown
---
```

---

