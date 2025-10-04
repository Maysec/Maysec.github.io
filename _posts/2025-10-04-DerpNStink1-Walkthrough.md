---
title: DerpNStink1 Walkthrough
date: 2025-10-04
categories: ['walkthrough','vulnhub']
tags: ['cms']
description: wordpress打点，sudo提权
author: may
image:
  path: ./../assets/images/2025-10-04-DerpNStink1-Walkthrough/cover%20(5).png
---

# Recon

这台机器开放标准端口的`ftp`、`ssh`和`http`

![image-20251004113501678](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004113501678.png)

# shell as www-data by wordpress

web前端是一个静态页面

![image-20251004113848174](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004113848174.png)

源代码中有`webnotes/notes.txt`提示，内容提示要进行host绑定

<-- @stinky, make sure to update your hosts file with local dns so the new derpnstink blog can be reached before it goes live --> 

目录扫描存在`weblog`目录

![image-20251004114108519](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004114108519.png)

访问`weblog`目录跳转`derpnstink.local`，写入`/etc/hosts`

能看出来是wordpress

![image-20251004114205091](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004114205091.png)

`nuclei`扫一下发现使用弱口令

![image-20251004114700222](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004114700222.png)

登录后台getshell

![image-20251004115258504](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004115258504.png)

![image-20251004115314959](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004115314959.png)

通过`/var/www/html/weblog/wp-config.php`得到mysql凭证`root:mysql`

发现`wp.users`表中存在`unclestinky`用户，应该对应上系统`stinky`用户

![image-20251004120105381](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004120105381.png)

使用`hashcat`破解得到`wedgie57`

`hashcat -m 400 hash.txt --wordlist /usr/share/wordlists/rockyou.txt`

![image-20251004121611450](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004121611450.png)

# shell as stinky

使用破解得到的密码登录`stinky`用户运行`linpeas.sh`

![image-20251004125836524](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004125836524.png)

例行检查，发现一些有趣的文件

![image-20251004131212603](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004131212603.png)

`derpissues.txt`内容，stinky说它需要抓包看看情况

![image-20251004131255358](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004131255358.png)

`key.txt`是一个私钥

![image-20251004131714498](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004131714498.png)

# shell as mrderp

`Documents`目录下发现`derpissues.pcap`，下载下来数据分析

![image-20251004132243232](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004132243232.png)

过滤http，查看wordpress登录包，得到`mrderp:derpderpderpderpderpderpderp"`

![image-20251004132423530](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004132423530.png)

# shell as root by sudo

登录后发现其有root权限执行`/home/mrderp/binaries/derpy*`的能力

![image-20251004132559036](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004132559036.png)

但是发现`/home/stinky/`下 并没有`binaries`目录，那么自己创建

![image-20251004133424518](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004133424518.png)

执行后获得root权限

![image-20251004133502549](./../assets/images/2025-10-04-DerpNStink1-Walkthrough/image-20251004133502549.png)
