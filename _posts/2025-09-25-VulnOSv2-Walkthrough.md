---
title: VulnOSv2 Walkthrough
date: 2025-09-25
categories: ['walkthrough','vulnhub']
tags: ['drupal','cms','kernel-pe']
author: may
description: drupal打点，内核提权
image:
  path: ./../assets/images/2025-09-25-VulnOSv2-Walkthrough/cover%20(5).png
---

# Recon

这台机器开放标准端口的`ssh`、`http`和非标端口`6667/tcp`

![image-20250925214730757](./../assets/images/2025-09-25-VulnOSv2-Walkthrough/image-20250925214730757.png)

# shell as www-data by drupal

访问后看起来是一个`cms`

![image-20250925215607161](./../assets/images/2025-09-25-VulnOSv2-Walkthrough/image-20250925215607161.png)

目录扫描发现存在`/jabc`路径，查看源代码发现是`Drupal 7`

![image-20250925215727343](./../assets/images/2025-09-25-VulnOSv2-Walkthrough/image-20250925215727343.png)

msfconsole一把梭

![image-20250925220316402](./../assets/images/2025-09-25-VulnOSv2-Walkthrough/image-20250925220316402.png)

# shell as webmin by password

例行检查查看网页数据库配置文件，得到mysql密码`toor`，登录后在`jabcd0cs.odm_user`表中得到用户名`webmin`和密码密文

![image-20250925223412569](./../assets/images/2025-09-25-VulnOSv2-Walkthrough/image-20250925223412569.png)

`hashes.com`得到`webmin1980`

![image-20250925223528538](./../assets/images/2025-09-25-VulnOSv2-Walkthrough/image-20250925223528538.png)

ssh登录即可

![image-20250925223558768](./../assets/images/2025-09-25-VulnOSv2-Walkthrough/image-20250925223558768.png)

# shell as root by kernel privileged escape

系统环境信息收集，发现为`ubuntu 14.04`，内核版本`3.13.0-24-generic`

![image-20250925224222087](./../assets/images/2025-09-25-VulnOSv2-Walkthrough/image-20250925224222087.png)

`searchsploit`查找`exp`，认为`37392.c`合适

![image-20250925224319300](./../assets/images/2025-09-25-VulnOSv2-Walkthrough/image-20250925224319300.png)

编译后提权

![image-20250925224515198](./../assets/images/2025-09-25-VulnOSv2-Walkthrough/image-20250925224515198.png)