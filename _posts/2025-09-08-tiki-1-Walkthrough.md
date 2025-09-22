---
title: tiki:1 Walkthrough
date: 2025-09-08
categories: ['walkthrough','vulnhub']
tags: ['cms']
author: may
description: cms打点，sudo提权
image:
  path: ./../assets/images/2025-09-08-tiki-1-Walkthrough/cover%20(8).png
---

# Recon

这台机器开放标准端口的`ssh`、`web`和`samba`

![](../assets/images/2025-09-08-tiki-1-Walkthrough/d7a9cc2c-a36b-496f-a93c-358d4676c771.png)

## samba

`smbmap`查看发现`Notes`挂载

![](../assets/images/2025-09-08-tiki-1-Walkthrough/de506fbb-214e-4039-a9f4-2d45975f5c34.png)

其内容泄露了一对凭据`Silky:51lky571k1`

![](../assets/images/2025-09-08-tiki-1-Walkthrough/f7ce2037-c69c-4503-8796-50b53ad29662.png)

# shell as root by vul

`robots.txt`中泄露`/tiki`路径，访问后是一个`cms`

![](../assets/images/2025-09-08-tiki-1-Walkthrough/840bce0a-54c3-4364-8cbf-14c165bd4100.png)

使用`smbclient`收集到的凭证能直接登录`/tiki/admin`后台

![](../assets/images/2025-09-08-tiki-1-Walkthrough/ac2148c8-79e5-48d0-9a2a-a88047d04f2e.png)

`searchsploit`发现`tiki`存在登录验证绕过漏洞，使用poc，发现提示抓包将密码置为空

![](../assets/images/2025-09-08-tiki-1-Walkthrough/36669de3-3825-4339-9fa8-89bba06a9be0.png)

利用漏洞登录`admin`用户后在`Credentials`处发现一对凭证

![](../assets/images/2025-09-08-tiki-1-Walkthrough/ff3d6bc9-db38-49a3-b474-99a0070a71cd.png)

ssh登陆后`sudo su`获得了root权限

![](../assets/images/2025-09-08-tiki-1-Walkthrough/6f67004c-dcd8-44ba-aae6-fb43f51f79ee.png)
