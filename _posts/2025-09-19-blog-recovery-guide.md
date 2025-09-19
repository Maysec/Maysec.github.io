---
title: "博客恢复使用指南"
date: 2025-09-19 15:30:00 +0800
categories: [技术分享, 博客]
tags: [Jekyll, GitHub Pages, 博客搭建]
toc: true
description: 如何恢复并继续使用GitHub Pages博客项目
---

## 前言

今天成功恢复了我的GitHub Pages博客项目！虽然丢失了本地的原始数据，但通过克隆线上的仓库，我能够完整地恢复整个博客项目。

## 恢复过程

### 1. 项目结构确认

通过检查项目结构，确认这是一个完整的Jekyll博客项目：

- `_posts/` - 存放博客文章
- `_config.yml` - Jekyll配置文件
- `_tabs/` - 页面标签配置
- `assets/` - 静态资源文件

### 2. Git状态检查

项目已经连接到GitHub仓库：
- 远程仓库：`https://github.com/Maysec/Maysec.github.io.git`
- 当前分支：`main`
- 工作区状态：干净，与远程同步

### 3. 环境配置

为了能够本地预览和开发，需要安装：
- Ruby开发环境
- Jekyll和相关依赖包

## 使用方法

### 写作新文章

1. 在`_posts`目录下创建新文件
2. 文件命名格式：`YYYY-MM-DD-文章标题.md`
3. 文件开头添加Front Matter：

```yaml
---
title: "文章标题"
date: 2025-09-19 15:30:00 +0800
categories: [分类1, 分类2]
tags: [标签1, 标签2]
toc: true
description: 文章描述
---
```

### 发布流程

```bash
# 添加新文章到版本控制
git add .

# 提交更改
git commit -m "发布新文章：文章标题"

# 推送到GitHub
git push origin main
```

## 总结

GitHub Pages的一个优势就是即使本地数据丢失，只要线上仓库完整，就能完全恢复项目。这次经历让我更加重视代码的版本管理和备份。

现在可以继续愉快地写作了！🎉
