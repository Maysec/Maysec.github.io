@echo off
echo 发布博客到GitHub Pages
echo.

echo 正在检查Git状态...
git status

echo.
set /p "commit_msg=请输入提交信息 (直接回车使用默认信息): "
if "%commit_msg%"=="" set "commit_msg=更新博客文章"

echo.
echo 正在添加文件到Git...
git add .

echo.
echo 正在提交更改...
git commit -m "%commit_msg%"

echo.
echo 正在推送到GitHub...
git push origin main

echo.
echo 发布完成！
echo 请等待几分钟，GitHub Pages会自动构建和部署你的博客
echo 博客地址: https://maysec.github.io
echo.
pause
