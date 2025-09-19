#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hashnode文章迁移脚本
用于将Hashnode的Markdown文章转换为Jekyll格式
"""

import os
import re
import yaml
from datetime import datetime
import shutil
from pathlib import Path

class HashnodeMigrator:
    def __init__(self, source_dir="migration/hashnode_articles", 
                 output_dir="migration/processed", 
                 posts_dir="_posts"):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.posts_dir = Path(posts_dir)
        self.log_file = Path("migration/logs/migration.log")
        
        # 确保目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def extract_front_matter(self, content):
        """从Hashnode文章中提取或生成Front Matter"""
        # 检查是否已有Front Matter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    front_matter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                    return front_matter, body
                except yaml.YAMLError:
                    pass
        
        # 如果没有Front Matter，从内容中提取信息
        lines = content.split('\n')
        title = ""
        body_start = 0
        
        # 查找标题（通常是第一个# 标题）
        for i, line in enumerate(lines):
            if line.strip().startswith('# '):
                title = line.strip()[2:].strip()
                body_start = i + 1
                break
        
        if not title:
            title = "未命名文章"
        
        # 生成Front Matter
        front_matter = {
            'title': title,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S +0800"),
            'categories': ['技术分享'],
            'tags': ['迁移文章'],
            'toc': True,
            'description': title
        }
        
        body = '\n'.join(lines[body_start:]).strip()
        return front_matter, body
    
    def process_images(self, content, article_name):
        """处理图片链接"""
        # 匹配各种图片格式
        image_patterns = [
            r'!\[([^\]]*)\]\(([^)]+)\)',  # ![alt](url)
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',  # <img src="url">
        ]
        
        processed_content = content
        image_urls = []
        
        for pattern in image_patterns:
            matches = re.findall(pattern, processed_content)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:  # ![alt](url) format
                        alt_text, url = match
                        image_urls.append(url)
                        # 转换为Jekyll格式的相对路径
                        filename = self.get_image_filename(url)
                        new_path = f"../assets/images/{filename}"
                        processed_content = processed_content.replace(f"]({url})", f"]({new_path})")
                    else:  # <img> format
                        url = match[0] if isinstance(match, tuple) else match
                        image_urls.append(url)
                        filename = self.get_image_filename(url)
                        new_path = f"../assets/images/{filename}"
                        processed_content = re.sub(
                            rf'src=["\']({re.escape(url)})["\']',
                            f'src="{new_path}"',
                            processed_content
                        )
        
        return processed_content, image_urls
    
    def get_image_filename(self, url):
        """从URL生成图片文件名"""
        # 提取文件名
        filename = os.path.basename(url.split('?')[0])  # 移除查询参数
        
        # 如果没有扩展名，添加默认扩展名
        if '.' not in filename:
            filename += '.png'
        
        # 确保文件名安全
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        
        return filename
    
    def process_article(self, file_path):
        """处理单个文章"""
        self.log(f"处理文章: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取Front Matter和正文
            front_matter, body = self.extract_front_matter(content)
            
            # 处理图片
            article_name = file_path.stem
            body, image_urls = self.process_images(body, article_name)
            
            # 生成Jekyll文件名
            title = front_matter.get('title', article_name)
            date_str = front_matter.get('date', datetime.now().strftime("%Y-%m-%d"))
            if isinstance(date_str, str):
                date_part = date_str.split()[0]  # 只取日期部分
            else:
                date_part = datetime.now().strftime("%Y-%m-%d")
            
            # 生成安全的文件名
            safe_title = re.sub(r'[^\w\-]', '-', title.lower())
            safe_title = re.sub(r'-+', '-', safe_title).strip('-')
            jekyll_filename = f"{date_part}-{safe_title}.md"
            
            # 生成完整的Jekyll文章
            jekyll_content = "---\n"
            jekyll_content += yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)
            jekyll_content += "---\n\n"
            jekyll_content += body
            
            # 保存处理后的文章
            output_path = self.output_dir / jekyll_filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(jekyll_content)
            
            self.log(f"文章处理完成: {jekyll_filename}")
            
            # 返回图片URL列表用于下载
            return {
                'filename': jekyll_filename,
                'output_path': output_path,
                'image_urls': image_urls,
                'title': title
            }
            
        except Exception as e:
            self.log(f"处理文章失败 {file_path}: {str(e)}")
            return None
    
    def migrate_all(self):
        """迁移所有文章"""
        self.log("开始迁移所有文章...")
        
        if not self.source_dir.exists():
            self.log(f"源目录不存在: {self.source_dir}")
            return []
        
        markdown_files = list(self.source_dir.glob("*.md"))
        if not markdown_files:
            self.log("源目录中没有找到Markdown文件")
            return []
        
        results = []
        for md_file in markdown_files:
            result = self.process_article(md_file)
            if result:
                results.append(result)
        
        self.log(f"迁移完成，共处理 {len(results)} 篇文章")
        return results
    
    def copy_to_posts(self, dry_run=False):
        """将处理后的文章复制到_posts目录"""
        self.log("开始复制文章到_posts目录...")
        
        processed_files = list(self.output_dir.glob("*.md"))
        if not processed_files:
            self.log("没有找到处理后的文章文件")
            return
        
        for file_path in processed_files:
            dest_path = self.posts_dir / file_path.name
            
            if dry_run:
                self.log(f"[DRY RUN] 将复制: {file_path} -> {dest_path}")
            else:
                shutil.copy2(file_path, dest_path)
                self.log(f"已复制: {file_path.name}")
        
        if not dry_run:
            self.log(f"复制完成，共复制 {len(processed_files)} 个文件")

def main():
    """主函数"""
    migrator = HashnodeMigrator()
    
    print("🔄 Hashnode文章迁移工具")
    print("=" * 50)
    
    # 检查源目录
    if not migrator.source_dir.exists():
        print(f"❌ 源目录不存在: {migrator.source_dir}")
        print("请将Hashnode文章复制到 migration/hashnode_articles/ 目录")
        return
    
    # 迁移文章
    results = migrator.migrate_all()
    
    if not results:
        print("❌ 没有成功处理任何文章")
        return
    
    print("\n📊 处理结果:")
    for result in results:
        print(f"✅ {result['title']} -> {result['filename']}")
        if result['image_urls']:
            print(f"   📸 包含 {len(result['image_urls'])} 张图片")
    
    # 询问是否复制到_posts目录
    print("\n" + "=" * 50)
    choice = input("是否将处理后的文章复制到_posts目录? (y/n): ").lower()
    
    if choice == 'y':
        migrator.copy_to_posts()
        print("✅ 文章已复制到_posts目录")
        print("\n下一步: 运行图片下载脚本")
        print("python migration/scripts/download_images.py")
    else:
        print("文章已处理完成，保存在 migration/processed/ 目录")

if __name__ == "__main__":
    main()
