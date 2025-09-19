@echo off
echo 正在安装Jekyll和依赖...
echo.

echo 1. 安装bundler...
gem install bundler

echo.
echo 2. 安装项目依赖...
bundle install

echo.
echo 3. 构建并启动本地服务器...
echo 请在浏览器中访问: http://localhost:4000
echo 按 Ctrl+C 停止服务器
echo.
bundle exec jekyll serve --livereload

pause
