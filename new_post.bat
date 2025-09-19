@echo off
setlocal enabledelayedexpansion

echo 创建新博客文章
echo.

:: 获取当前日期
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"

set "datestamp=%YYYY%-%MM%-%DD%"
set "timestamp=%HH%:%Min%:%Sec%"

:: 获取文章标题
set /p "title=请输入文章标题: "
if "%title%"=="" (
    echo 文章标题不能为空！
    pause
    exit /b
)

:: 生成文件名（移除空格和特殊字符）
set "filename=%title: =-%"
set "filename=%filename::=-%"
set "filename=%filename:?=%"
set "filename=%filename:!=-%"

set "filepath=_posts\%datestamp%-%filename%.md"

:: 创建文章文件
echo ---
echo title: "%title%"
echo date: %datestamp% %timestamp% +0800
echo categories: [技术分享]
echo tags: [新文章]
echo toc: true
echo description: %title%
echo ---
echo.
echo ## 前言
echo.
echo 在这里开始你的文章内容...
echo.
echo ## 总结
echo.
echo 文章总结...

) > "%filepath%"

echo.
echo 文章已创建: %filepath%
echo.
echo 你可以使用以下命令编辑文章:
echo notepad "%filepath%"
echo.
echo 或使用你喜欢的编辑器打开该文件
echo.
pause
