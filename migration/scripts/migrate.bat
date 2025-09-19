@echo off
chcp 65001 >nul
echo 🔄 Hashnode文章迁移工具
echo ================================

cd /d "%~dp0..\.."

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python环境，请先安装Python
    pause
    exit /b 1
)

echo 安装必要的Python包...
pip install requests pyyaml pathlib >nul 2>&1

echo.
echo 📋 开始迁移流程...
echo ================================

echo 步骤1: 转换文章格式
python migration/scripts/migrate.py

if errorlevel 1 (
    echo ❌ 文章转换失败
    pause
    exit /b 1
)

echo.
echo 步骤2: 下载图片
python migration/scripts/download_images.py

if errorlevel 1 (
    echo ❌ 图片下载失败
    pause
    exit /b 1
)

echo.
echo ✅ 迁移完成！
echo.
echo 下一步操作：
echo 1. 检查 _posts 目录中的文章格式
echo 2. 运行本地预览测试: bundle exec jekyll serve
echo 3. 推送到GitHub: git add . && git commit -m "迁移新文章" && git push

pause
