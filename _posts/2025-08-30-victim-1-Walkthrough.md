---
title: victim:1 Walkthrough
date: 2025-08-30
categories: ['walkthrough','vulnhub']
tags: ['suid','aircrack-ng']
author: may
description: wifi通信数据包爆破打点，suid提权
image:
  path: ./../assets/images/2025-08-30-victim-1-Walkthrough/cover%20(24).png
---

# Recon

机器开放了`ssh`和4个`web`

![](../assets/images/2025-08-30-victim-1-Walkthrough/8291d57e-5ea9-4c35-87e6-6444c669fe30.png)

## 80/tcp

网页前端返回`No configuration file found and no installation code available. Exiting…`

![](../assets/images/2025-08-30-victim-1-Walkthrough/cdce7807-aeb7-4d51-89b1-bd0d76fd0292.png)

从目录扫描结果上来有一些引导性质的攻击向量，其中`file.php`存在，返回空，可能需要传参

![](../assets/images/2025-08-30-victim-1-Walkthrough/1e99c31c-d6c4-4f87-b111-b8f9eb451718.png)

从`README.txt`来看，这台服务器运行着一个`Joomla!`，而`robots.txt`暴露了一个`h@ck3rz!`的关键字，可能是密码

![](../assets/images/2025-08-30-victim-1-Walkthrough/09dd7a4d-5921-494a-bd53-62b93235041d.png)

## 8080/tcp

目录扫描同样发现一些有趣的路径，其中`passwords.txt`返回`Hahahaha...Try Harder!`

![](../assets/images/2025-08-30-victim-1-Walkthrough/7c758d8b-a2d8-4b25-8395-05248137ea41.png)

而`file.php`访问不被中间件解析而直接下载，其中是一段文件包含代码，估计可以从`80/file.php`入手

![](../assets/images/2025-08-30-victim-1-Walkthrough/30131835-c497-4a53-85df-4c0ca0909b81.png)

使用`dirb/big.txt`扫描得到了几个敏感文件

![](../assets/images/2025-08-30-victim-1-Walkthrough/929fef95-6760-4fa4-901a-a52fae513e93.png)

## 8999/tcp

这是一个使用`webfs/1.21`

![](../assets/images/2025-08-30-victim-1-Walkthrough/c82cc518-0e8f-46d2-b386-ad7b1ee56cb4.png)

## 9000/tcp

似乎是一个bolt.cms

![](../assets/images/2025-08-30-victim-1-Walkthrough/95cb796a-f988-4a25-9c03-45d6ea2bb000.png)

---

感觉这台机器业务很多：

80/tcp : joomla cms

8080/tcp : lead some interesting

8999/tcp : webfs → wordpress

9000/tcp : bolt cms

# shell as dlink by aircrack

`webfs`下有一个`WPA-01.cap`，根据名称能判断是wifi的数据包

通过`aircrack-ng -w /usr/share/wordlists/rockyou.txt WPA-01.cap`破解密码

得到`wifi ssid`为`dlink`，密码`p4ssword`

![](../assets/images/2025-08-30-victim-1-Walkthrough/910cc285-140b-4879-bcff-76d71ddb5da0.png)

尝试使用ssh登录

![](../assets/images/2025-08-30-victim-1-Walkthrough/cddcc5a6-fffa-4c1c-adb4-261f37debc12.png)

# shell as root by suid

例行检查 发现`nohup`具有suid，遂提权

![](../assets/images/2025-08-30-victim-1-Walkthrough/5c42584b-574d-48cd-9da3-ab69f125edbc.png)
