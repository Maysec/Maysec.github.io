---
title: dpwwn:1 Walkthrough
date: 2025-08-27
categories: ['walkthrough','vulnhub']
tags: ['crontab-pe']
author: may
description: mysql空密码登录，凭证泄露打点，crontab提权
image:
  path: ./../assets/images/2025-08-27-dpwwn-1-Walkthrough/cover%20(30).png
---

# Recon

机器开放了ssh、web和mysql，除了web似乎没有其它初始攻击向量

![](../assets/images/2025-08-27-dpwwn-1-Walkthrough/c8a65fe8-3c13-4150-8266-817f94c6d91f.png)

网页前端是一个`apache default page`,源代码中也没有有效信息

![](../assets/images/2025-08-27-dpwwn-1-Walkthrough/1b08b047-9474-4aa9-b3ad-1306e11ff6a9.png)

`feroxbuster`目录扫描得到`info.php`

![](../assets/images/2025-08-27-dpwwn-1-Walkthrough/31ab0daf-a8d8-45f6-a034-9ac6ae22314d.png)

`info.php`是`phpinfo`，没有发现有效信息

# shell as mistic by mysql

把目标给`yakit`弱口令爆破，发现`mysql`密码为空，登录一定要使用`--skip-ssl`忽略证书问题

![](../assets/images/2025-08-27-dpwwn-1-Walkthrough/9e874049-5280-4eca-9cd9-0fc4cc4ea341.png)

在`ssh`库`users`表得到一个用户名

![](../assets/images/2025-08-27-dpwwn-1-Walkthrough/a34ee89d-e3d4-4244-8deb-0b0a4046c0cd.png)

ssh登录得到`mistic`用户权限

![](../assets/images/2025-08-27-dpwwn-1-Walkthrough/c36cf639-834b-4d29-90d4-519011354443.png)

# shell as root by crontab

例行检查，发现存在`root`权限运行的计划任务

![](../assets/images/2025-08-27-dpwwn-1-Walkthrough/9e876b29-c36f-4924-b9ce-e7764ff52b37.png)

`crontab`执行脚本`reverse shell`的场景要尽量避免多层引号及特殊字符

把python的`payload`base64编码

![](../assets/images/2025-08-27-dpwwn-1-Walkthrough/03d44c97-2e09-479b-a6b6-77f737cd3745.png)

然后通过`echo "echo {payload}|base64 -d|bash" > logrot.sh`写入脚本

![](../assets/images/2025-08-27-dpwwn-1-Walkthrough/13285f02-11a3-4e8e-bc75-666500781ab1.png)