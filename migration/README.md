# Hashnode文章迁移工作流程

## 📁 目录结构
```
migration/
├── hashnode_articles/     # 从Hashnode复制的原始文章
├── processed/            # 处理后的文章
├── images/              # 下载的图片文件
├── scripts/             # 迁移脚本
└── logs/               # 处理日志
```

## 🚀 迁移步骤

### 1. 复制文章
将Hashnode的文章复制到 `hashnode_articles/` 目录

### 2. 运行迁移脚本
执行 `scripts/migrate.py` 处理文章格式

### 3. 下载图片
执行 `scripts/download_images.py` 下载并整理图片

### 4. 验证和发布
检查处理结果，然后推送到GitHub

## 📝 注意事项
- 确保图片链接都是有效的
- 检查Front Matter格式
- 验证本地构建成功后再推送
