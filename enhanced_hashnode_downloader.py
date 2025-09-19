#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Hashnode图片下载器
从指定的Markdown文件中提取Hashnode图床链接，自动下载图片，并更新markdown文件中的图片引用为本地相对路径
"""

import os
import re
import requests
import hashlib
import argparse
from pathlib import Path
from urllib.parse import urlparse
import time
from datetime import datetime
import shutil

class EnhancedHashnodeImageDownloader:
    def __init__(self, output_dir="media"):
        self.base_output_dir = Path(output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置请求会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        # Hashnode图床域名模式
        self.hashnode_patterns = [
            r'https://cdn\.hashnode\.com/res/hashnode/image/upload/[^)]+',
            r'https://hashnode\.imgix\.net/[^)]+',
            r'https://[^.]+\.hashnode\.dev/[^)]+\.(?:png|jpg|jpeg|gif|webp)',
        ]

        # 通用图片URL模式
        self.image_patterns = [
            r'!\[([^\]]*)\]\(([^)]+\.(?:png|jpg|jpeg|gif|webp|svg)(?:\?[^)]*)?(?:\s+[^)]*)?)\)',  # ![alt](url) 或 ![alt](url align="center")
            r'!\[([^\]]*)\]\((https://cdn\.hashnode\.com/[^)]+)\)',  # 专门匹配Hashnode链接
            r'<img[^>]+src=["\']([^"\']+\.(?:png|jpg|jpeg|gif|webp|svg)(?:\?[^"\']*)?)["\']',  # <img src="url">
        ]

        self.downloaded_count = 0
        self.failed_count = 0
        self.url_mapping = {}  # 原URL -> 本地相对路径映射
        self.article_title = ""
        self.article_dir = None

    def log(self, message, level="INFO"):
        """打印日志信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def extract_filename_without_extension(self, file_path):
        """从文件路径提取不含扩展名的文件名"""
        file_path = Path(file_path)
        filename_without_ext = file_path.stem  # 获取不含扩展名的文件名
        self.log(f"使用文件名作为目录: {filename_without_ext}")
        return filename_without_ext

    def sanitize_filename(self, title):
        """清理标题作为文件夹名"""
        # 移除或替换不适合作为文件夹名的字符
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', title)
        sanitized = re.sub(r'[^\w\s\-_\u4e00-\u9fff]', '', sanitized)  # 保留中文字符
        sanitized = re.sub(r'\s+', '_', sanitized)  # 空格替换为下划线
        sanitized = sanitized.strip('_')
        return sanitized if sanitized else "untitled"

    def is_hashnode_url(self, url):
        """检查是否为Hashnode图床URL"""
        for pattern in self.hashnode_patterns:
            if re.match(pattern, url):
                return True
        return 'hashnode' in url.lower() or 'cdn.hashnode' in url.lower()

    def extract_image_urls(self, content):
        """从Markdown内容中提取所有图片URL"""
        urls = []

        # 提取Markdown格式的图片
        for pattern in self.image_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:  # ![alt](url) format
                        alt_text, url = match
                        # 清理URL，移除align等属性
                        url = url.split()[0] if ' ' in url else url
                        urls.append((url, alt_text))
                    else:  # <img> format or other
                        url = match[0] if match[0] else match[1] if len(match) > 1 else match
                        url = url.split()[0] if ' ' in str(url) else str(url)
                        urls.append((url, ""))
                else:
                    url = str(match).split()[0] if ' ' in str(match) else str(match)
                    urls.append((url, ""))

        # 去重
        seen = set()
        unique_urls = []
        for url, alt in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append((url, alt))

        return unique_urls

    def get_safe_filename(self, url, content_type=None):
        """生成安全的文件名"""
        parsed_url = urlparse(url)

        # 尝试从URL路径获取文件名
        path = parsed_url.path
        if path:
            filename = os.path.basename(path.split('?')[0])  # 移除查询参数
        else:
            filename = ""

        # 如果没有文件名或扩展名，生成一个
        if not filename or '.' not in filename:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]

            # 根据content-type确定扩展名
            ext = '.png'  # 默认
            if content_type:
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'webp' in content_type:
                    ext = '.webp'
                elif 'svg' in content_type:
                    ext = '.svg'

            filename = f"hashnode_{url_hash}{ext}"

        # 清理文件名，移除非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = re.sub(r'_+', '_', filename)

        return filename

    def download_image(self, url, max_retries=3):
        """下载单个图片"""
        for attempt in range(max_retries):
            try:
                self.log(f"下载图片 (尝试 {attempt + 1}/{max_retries}): {url}")

                # 发送请求
                response = self.session.get(url, timeout=30, stream=True)
                response.raise_for_status()

                # 检查content-type
                content_type = response.headers.get('content-type', '').lower()
                if not content_type.startswith('image/'):
                    self.log(f"警告: URL返回的不是图片类型: {content_type}", "WARN")

                # 生成文件名
                filename = self.get_safe_filename(url, content_type)
                file_path = self.article_dir / filename

                # 如果文件已存在且大小相同，跳过
                if file_path.exists():
                    existing_size = file_path.stat().st_size
                    content_length = int(response.headers.get('content-length', 0))
                    if existing_size == content_length and existing_size > 0:
                        self.log(f"文件已存在，跳过: {filename}")
                        relative_path = f"media/{self.article_title}/{filename}"
                        self.url_mapping[url] = relative_path
                        return filename

                # 下载文件
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

                # 验证文件
                file_size = file_path.stat().st_size
                if file_size == 0:
                    file_path.unlink()
                    raise Exception("下载的文件为空")

                self.log(f"下载成功: {filename} ({file_size:,} bytes)")
                self.downloaded_count += 1
                
                # 记录相对路径映射
                relative_path = f"media/{self.article_title}/{filename}"
                self.url_mapping[url] = relative_path
                return filename

            except Exception as e:
                self.log(f"下载失败 (尝试 {attempt + 1}): {str(e)}", "ERROR")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避

        self.failed_count += 1
        return None

    def replace_image_urls_in_content(self, content):
        """替换markdown内容中的图片URL为本地相对路径"""
        modified_content = content
        
        for original_url, relative_path in self.url_mapping.items():
            # 匹配多种可能的图片语法格式
            patterns_to_replace = [
                # ![alt](url align="center")
                rf'!\[([^\]]*)\]\({re.escape(original_url)}(\s+[^)]+)?\)',
                # ![alt](url)
                rf'!\[([^\]]*)\]\({re.escape(original_url)}\)',
                # <img src="url">
                rf'<img([^>]+)src=["\']({re.escape(original_url)})["\']([^>]*)>',
            ]
            
            for pattern in patterns_to_replace:
                def replace_func(match):
                    if '![' in match.group(0):  # Markdown 格式
                        alt_text = match.group(1)
                        return f'![{alt_text}]({relative_path})'
                    else:  # HTML img 格式
                        before_src = match.group(1)
                        after_src = match.group(3) if len(match.groups()) >= 3 else ''
                        return f'<img{before_src}src="{relative_path}"{after_src}>'
                
                modified_content = re.sub(pattern, replace_func, modified_content)
                
        return modified_content

    def process_markdown_file(self, file_path, hashnode_only=True, auto_replace=True):
        """处理Markdown文件，提取并下载图片，可选择自动替换链接"""
        file_path = Path(file_path)

        if not file_path.exists():
            self.log(f"文件不存在: {file_path}", "ERROR")
            return False

        self.log(f"处理文件: {file_path}")

        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取文件名（不含扩展名）作为目录名
            self.article_title = self.extract_filename_without_extension(file_path)
            
            # 创建文章专用目录
            self.article_dir = self.base_output_dir / self.article_title
            self.article_dir.mkdir(parents=True, exist_ok=True)
            self.log(f"创建目录: {self.article_dir}")

            # 提取图片URL
            image_urls = self.extract_image_urls(content)

            if not image_urls:
                self.log("未找到图片链接")
                return True

            self.log(f"找到 {len(image_urls)} 个图片链接")

            # 过滤URL（如果只要Hashnode图床）
            if hashnode_only:
                filtered_urls = [(url, alt) for url, alt in image_urls if self.is_hashnode_url(url)]
                self.log(f"其中 {len(filtered_urls)} 个是Hashnode图床链接")
                image_urls = filtered_urls

            if not image_urls:
                self.log("没有找到Hashnode图床链接")
                return True

            # 下载图片
            for url, alt_text in image_urls:
                filename = self.download_image(url)
                if filename:
                    self.log(f"  ✓ {url} -> {filename}")
                else:
                    self.log(f"  ✗ 下载失败: {url}", "ERROR")

                # 避免请求过于频繁
                time.sleep(1)

            # 自动替换markdown文件中的链接
            if auto_replace and self.url_mapping:
                self.log("开始替换markdown文件中的图片链接...")
                modified_content = self.replace_image_urls_in_content(content)
                
                # 创建备份
                backup_path = file_path.with_suffix('.md.backup')
                shutil.copy2(file_path, backup_path)
                self.log(f"原文件备份至: {backup_path}")
                
                # 写入修改后的内容
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                
                self.log(f"✅ 已更新markdown文件，替换了 {len(self.url_mapping)} 个图片链接")

            return True

        except Exception as e:
            self.log(f"处理文件失败: {str(e)}", "ERROR")
            return False

    def generate_mapping_file(self):
        """生成URL映射文件"""
        if not self.url_mapping:
            return

        mapping_file = self.article_dir / "url_mapping.txt"
        with open(mapping_file, 'w', encoding='utf-8') as f:
            f.write("# URL映射文件\n")
            f.write("# 格式: 原始URL -> 本地相对路径\n\n")
            for original_url, relative_path in self.url_mapping.items():
                f.write(f"{original_url} -> {relative_path}\n")

        self.log(f"URL映射文件已生成: {mapping_file}")

    def print_summary(self):
        """打印下载摘要"""
        total = self.downloaded_count + self.failed_count
        print("\n" + "="*60)
        print("处理摘要:")
        print(f"  文件名: {self.article_title}")
        print(f"  总计: {total} 个图片")
        print(f"  成功: {self.downloaded_count} 个")
        print(f"  失败: {self.failed_count} 个")
        print(f"  输出目录: {self.article_dir.absolute()}")
        if hasattr(self, 'url_mapping') and self.url_mapping:
            print(f"  替换链接: {len(self.url_mapping)} 个")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='Enhanced Hashnode图片下载器 - 下载图片并自动更新markdown链接')
    parser.add_argument('file', help='要处理的Markdown文件路径')
    parser.add_argument('-o', '--output', default='media',
                       help='输出基础目录 (默认: media)')
    parser.add_argument('--all-images', action='store_true',
                       help='下载所有图片，不只是Hashnode图床的')
    parser.add_argument('--no-replace', action='store_true',
                       help='不自动替换markdown文件中的链接')

    args = parser.parse_args()

    # 创建下载器实例
    downloader = EnhancedHashnodeImageDownloader(args.output)

    print("🚀 Enhanced Hashnode图片下载器")
    print("=" * 60)
    print("功能: 下载Hashnode图片 + 自动更新markdown链接")
    print("=" * 60)

    # 处理文件
    success = downloader.process_markdown_file(
        args.file,
        hashnode_only=not args.all_images,
        auto_replace=not args.no_replace
    )

    if success:
        # 生成映射文件
        downloader.generate_mapping_file()

        # 打印摘要
        downloader.print_summary()
    else:
        print("❌ 处理失败")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
