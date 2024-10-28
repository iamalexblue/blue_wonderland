---
attributes:
  - trait_type: xlog_slug
    value: ru-he-wei-yu-ming-you-xiang-she-zhi-BIMI-qi-ye-Logo
  - trait_type: xlog_disable_ai_summary
    value: false
date_published: 2024-07-09T12:14:19.696Z
sources:
  - xlog
summary: ""
tags:
  - post
  - 邮箱收集者
  - 邮件
  - BIMI
title: 如何为域名邮箱设置 BIMI 企业 Logo？
type: note

---

# 如何为域名邮箱设置 BIMI 企业 Logo？

# 如何为域名邮箱设置 BIMI 企业 Logo？

> BIMI（Brand Indicator for Message Identification）让您的域名邮箱个性鲜明，通过在发出的邮件中添加企业Logo，加强真实性和信誉度。本文将引导您如何实现这一功能。

在数字化时代，电子邮件是企业与客户交流的重要渠道。为展示品牌形象，提升邮件识别度，一种名为BIMI的技术为域名邮箱带来了新的变革。BIMI，品牌信息识别标示，它允许您在邮件中嵌入企业Logo。这不仅可以增强企业邮件的视觉识别度，还能提升收件人的信任感。

### 一、前提准备

启动BIMI之前，请确保您的域名拥有DMARC设置，这是邮件身份验证与策略报告的基础，保护您的邮箱免受伪造发件人地址的影响。

### 二、步骤详解

1. **设置DMARC记录**：确保所有相关SPF和DKIM记录已经设置完毕。
2. **上传Logo**：选择SVG格式，遵循安全性、文件大小（推荐不超过32KB）和中心图形等要求。

### 三、重要细节

1. **按照 Google 对SVG Logo 的要求，其需要重点注意：**
- SVG必须是SVG Tiny Portable/Secure版本。
- 文件背景应为纯色，透明背景可能不显示正确。
- Logo应为正方形，图形居中。

2. **除了 BIMI 标准要求之外，Gmail 还需遵守 Gmail 对 BIMI SVG 文件的以下要求：**

- 图片大小必须至少为 96 像素高和 96 像素宽。
- 图片大小必须以绝对像素指定。示例：width=”96” height=”96”
- 请勿使用相对尺寸来指定图片尺寸。示例：width=”100%” height=”100%”

3. **除了满足这些要求以外，我们还针对 SVG 文件与 Gmail 的兼容性提供了以下建议：**

- 徽标图片应位于正方形的中心。
- 徽标图片应显示在纯色背景中。透明背景可能无法按预期显示。
- SVG 文件大小不应超过 32 KB。
- SVG 文件应包含 <desc> 元素（说明）以提供无障碍功能。

处理完成之后的 `.svg` 文件链接格式应当如下所示：
```
https://raw.githubusercontent.com/iamalexblue/fluoxetine12_pic_repo/master/Resources/Email_BIMI_Logo.svg
```

![Email_BIMI_Logo](./attachments/Email_BIMI_Logo.svg)

### 四、商标注册与VMC认证
如果您希望在Gmail等平台上展示Logo认证，您需要注册商标并获得VMC认证。

### 五、添加DNS解析记录
设置特定的DNS 'TXT'记录，指向您的Logo文件和可选的VMC认证地址。

```
v=BIMI1;l=https://raw.githubusercontent.com/iamalexblue/fluoxetine12_pic_repo/master/Resources/Email_BIMI_Logo.svg
```

### 六、结尾：
通过BIMI，您的电子邮件将更加个性化和专业，吸引收件人关注的同时，强化品牌形象。这些简单的步骤将引领您进入电子邮件识别的新时代。

> References:
- [使用 BIMI 在电子邮件中添加品牌徽标](https://support.google.com/a/answer/10911320?hl=zh-Hans&sjid=15642333964812356936-AP)
- [为 BIMI 做好准备：准备您的徽标](https://www.gworg.com/problems/1504.html)
- [ BIMI - 为域名邮箱的邮件添加企业 LOGO ](https://www.httpsmail.com/bimi.html)
- [在域名提供商处添加 BIMI TXT 记录](https://support.google.com/a/answer/10911321?hl=zh-Hans)


![](./attachments/QmQDB6tnCVhyEsEFbCtWBrdE5wdADx7oJ8tCVKUTBEiskC)