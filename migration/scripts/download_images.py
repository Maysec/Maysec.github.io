#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片下载和处理脚本
从处理后的文章中提取图片URL并下载到本地
"""

import os
import re
import requests
import hashlib
from pathlib import Path
from urllib.parse import urlparse
import time
from datetime import datetime

class ImageDownloader:
    def __init__(self, posts_dir="_posts", assets_dir="assets/images", log_dir="migration/logs"):
        self.posts_dir = Path(posts_dir)
        self.assets_dir = Path(assets_dir)
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / "image_download.log"
        
        # 确保目录存在
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载配置
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 支持的图片格式
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'}
        
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def extract_image_urls(self, content):
        """从文章内容中提取所有图片URL"""
        urls = set()
        
        # 匹配 ![alt](url) 格式
        markdown_images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        for alt, url in markdown_images:
            if self.is_external_url(url):
                urls.add(url)
        
        # 匹配 <img src="url"> 格式
        html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        for url in html_images:
            if self.is_external_url(url):
                urls.add(url)
        
        return list(urls)
    
    def is_external_url(self, url):
        """检查是否为外部URL"""
        return url.startswith(('http://', 'https://')) and not url.startswith('../assets/')
    
    def get_safe_filename(self, url, content_type=None):
        """生成安全的文件名"""
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        # 如果URL没有文件扩展名，根据content-type推断
        if '.' not in filename and content_type:
            if 'image/jpeg' in content_type:
                filename += '.jpg'
            elif 'image/png' in content_type:
                filename += '.png'
            elif 'image/gif' in content_type:
                filename += '.gif'
            elif 'image/webp' in content_type:
                filename += '.webp'
            else:
                filename += '.png'  # 默认PNG
        
        # 如果还是没有扩展名，使用URL的hash作为文件名
        if '.' not in filename:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"{url_hash}.png"
        
        # 清理文件名
        filename = re.sub(r'[^\w\-_\.]', '_', filename)
        filename = re.sub(r'_+', '_', filename)
        
        return filename
    
    def download_image(self, url, max_retries=3):
        """下载单个图片"""
        for attempt in range(max_retries):
            try:
                self.log(f"下载图片 (尝试 {attempt + 1}/{max_retries}): {url}")
                
                response = self.session.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                # 检查content-type
                content_type = response.headers.get('content-type', '').lower()
                if not content_type.startswith('image/'):
                    self.log(f"⚠️  警告: URL返回的不是图片类型: {content_type}")
                
                # 生成文件名
                filename = self.get_safe_filename(url, content_type)
                file_path = self.assets_dir / filename
                
                # 如果文件已存在，检查大小
                if file_path.exists():
                    existing_size = file_path.stat().st_size
                    content_length = int(response.headers.get('content-length', 0))
                    if existing_size == content_length and existing_size > 0:
                        self.log(f"✅ 文件已存在，跳过: {filename}")
                        return filename
                
                # 下载文件
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # 验证文件大小
                file_size = file_path.stat().st_size
                if file_size == 0:
                    file_path.unlink()  # 删除空文件
                    raise Exception("下载的文件为空")
                
                self.log(f"✅ 下载成功: {filename} ({file_size} bytes)")
                return filename
                
            except Exception as e:
                self.log(f"❌ 下载失败 (尝试 {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                
        return None
    
    def update_article_images(self, article_path, url_mapping):
        """更新文章中的图片链接"""
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            updated = False
            
            for original_url, new_filename in url_mapping.items():
                if new_filename:
                    new_path = f"../assets/images/{new_filename}"
                    
                    # 替换 ![alt](url) 格式
                    content = re.sub(
                        rf'!\[([^\]]*)\]\({re.escape(original_url)}\)',
                        rf'![\1]({new_path})',
                        content
                    )
                    
                    # 替换 <img src="url"> 格式
                    content = re.sub(
                        rf'src=["\']({re.escape(original_url)})["\']',
                        f'src="{new_path}"',
                        content
                    )
                    
                    if original_url in original_content:
                        updated = True
                        self.log(f"🔄 更新链接: {original_url} -> {new_path}")
            
            if updated:
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"✅ 文章更新完成: {article_path.name}")
            
            return updated
            
        except Exception as e:
            self.log(f"❌ 更新文章失败 {article_path}: {str(e)}")
            return False
    
    def process_article(self, article_path):
        """处理单个文章的图片"""
        self.log(f"处理文章: {article_path.name}")
        
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取图片URL
            image_urls = self.extract_image_urls(content)
            
            if not image_urls:
                self.log("未找到外部图片链接")
                return True
            
            self.log(f"找到 {len(image_urls)} 个图片链接")
            
            # 下载图片并记录映射关系
            url_mapping = {}
            success_count = 0
            
            for url in image_urls:
                filename = self.download_image(url)
                url_mapping[url] = filename
                if filename:
                    success_count += 1
                time.sleep(1)  # 避免请求过于频繁
            
            # 更新文章中的图片链接
            if success_count > 0:
                self.update_article_images(article_path, url_mapping)
            
            self.log(f"文章处理完成: 成功下载 {success_count}/{len(image_urls)} 张图片")
            return success_count == len(image_urls)
            
        except Exception as e:
            self.log(f"处理文章失败: {str(e)}")
            return False
    
    def process_all_articles(self):
        """处理所有文章"""
        self.log("开始处理所有文章的图片...")
        
        if not self.posts_dir.exists():
            self.log(f"❌ _posts目录不存在: {self.posts_dir}")
            return
        
        markdown_files = list(self.posts_dir.glob("*.md"))
        if not markdown_files:
            self.log("❌ 没有找到Markdown文章")
            return
        
        self.log(f"找到 {len(markdown_files)} 篇文章")
        
        success_count = 0
        for article_path in markdown_files:
            if self.process_article(article_path):
                success_count += 1
            print("-" * 50)  # 分隔线
        
        self.log(f"处理完成: {success_count}/{len(markdown_files)} 篇文章处理成功")
    
    def cleanup_unused_images(self):
        """清理未使用的图片"""
        self.log("开始清理未使用的图片...")
        
        # 收集所有文章中引用的图片
        used_images = set()
        
        for article_path in self.posts_dir.glob("*.md"):
            try:
                with open(article_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取本地图片引用
                local_images = re.findall(r'!\[[^\]]*\]\(\.\./assets/images/([^)]+)\)', content)
                used_images.update(local_images)
                
                local_images = re.findall(r'src=["\']\.\.//assets/images/([^"\']+)["\']', content)
                used_images.update(local_images)
                
            except Exception as e:
                self.log(f"读取文章失败 {article_path}: {str(e)}")
        
        # 检查assets/images目录中的文件
        if not self.assets_dir.exists():
            return
        
        all_images = set(f.name for f in self.assets_dir.iterdir() if f.is_file())
        unused_images = all_images - used_images
        
        if unused_images:
            self.log(f"发现 {len(unused_images)} 个未使用的图片:")
            for img in unused_images:
                self.log(f"  - {img}")
            
            choice = input("是否删除这些未使用的图片? (y/n): ").lower()
            if choice == 'y':
                for img in unused_images:
                    try:
                        (self.assets_dir / img).unlink()
                        self.log(f"已删除: {img}")
                    except Exception as e:
                        self.log(f"删除失败 {img}: {str(e)}")
        else:
            self.log("没有发现未使用的图片")

def main():
    """主函数"""
    downloader = ImageDownloader()
    
    print("📸 图片下载和处理工具")
    print("=" * 50)
    
    # 处理所有文章
    downloader.process_all_articles()
    
    print("\n" + "=" * 50)
    choice = input("是否清理未使用的图片? (y/n): ").lower()
    
    if choice == 'y':
        downloader.cleanup_unused_images()
    
    print("\n✅ 图片处理完成!")
    print("下一步: 检查文章格式并推送到GitHub")

if __name__ == "__main__":
    main()
