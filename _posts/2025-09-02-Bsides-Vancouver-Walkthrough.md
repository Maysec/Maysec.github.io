---
title: Bsides-Vancouver Walkthrough
date: 2025-09-02
categories: ['walkthrough','vulnhub']
tags: ['cms','crontab-pe']
author: may
description: wordpress打点，crontab提权
image:
 path: ./../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/cover%20(19).png
---

# Recon

机器开放了`ftp` 、`ssh`、`http`三个标准端口

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/d00c0f1f-0a92-4291-bad4-cfe0588ddbe7.png)

## ftp

`ftp`存在匿名登陆，`public`目录下有`users.txt.bk`文件

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/bbf55269-8aa0-447e-8e8e-613e2cd07458.png)

其内容是备份的用户名，获取用作`ssh`的爆破或`web`爆破

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/b7b41bfb-67b2-40cc-a37c-f073d893f882.png)

## Web

# shell as www-data by wordpress

`feroxbuster`目录扫描发现`robots.txt`，其中包含`backup_wordpress`路径，访问后是一个标准的`wordpress`

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/1b32a366-53d7-4e1c-9cf2-95a4ceebd04b.png)

通过`wpscan -e u`枚举用户只得到`john`和`admin`，那么先只爆破这两个用户

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/308db329-0b64-47bb-824d-75f8e13b5f47.png)

爆破得到`john / enigma`

登陆后发现有权限更改`admin`用户密码

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/ef7431ec-67fc-4ed6-8c85-08cfded40e63.png)

更改密码后用`msfconsole` `getshell`

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/8c305755-109c-4eb9-91f6-eeb9ef5febfc.png)

# shell as root by crontab

例行检查，发现存在root权限的`crontab`，并且目标文件有`写`权限

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/30346c79-ca3a-4600-89cc-52d6273259ae.png)

这个文件的`shebang`是`/bin/sh`，它可能无法解析`bash`反弹shell中的语法而导致反弹shell失败

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/b29bfec6-2fca-4db8-8829-0e44e5184aa2.png)

通过`printf`命令修改`shebang`为`/bin/bash`

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/26016369-b04a-4c52-860b-66491bd84e62.png)

反弹shell成功

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/1258e674-e99f-4eb2-8c45-bf0e81778327.png)

# Some thinking

> `shebang`的修改为什么是`printf`而不是更易用的`sed`

其实最开始就在使用`sed -i`做尝试，发现都无法执行

这是由于`sed`的工作原理是在目标目录创建一个临时文件先写入内容，写入完成后再将内容替换到目标文件

在这个过程中如果没有权限就会发生如图的报错

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/e5e4c64b-d022-4d8e-a081-b1f877dde8a5.png)

而`echo`写入文件则不会创建临时文件，它会直接对目标文件完成修改，自然也没有权限问题

所以需要一个原理与`echo`类似，又能完成内容编辑的工具，就是`printf`

![](../assets/images/2025-09-02-Bsides-Vancouver-Walkthrough/26016369-b04a-4c52-860b-66491bd84e62.png)

`print '%s\n' '...' '...'`命令会把`\n`加在后面每一行的内容后，这就很简单完成了文件的多行写入从而达到修改文件的目的
