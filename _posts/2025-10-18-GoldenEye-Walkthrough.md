---
title: GoldenEye Walkthrough
date: 2025-10-19
categories: ['walkthrough','vulnhub']
tags: ['pop3','cms','kernel-pe']
description: pop3爆破，moodle后台打点，内核提权
author: may
image:
  path: ./../assets/images/2025-10-18-GoldenEye-Walkthrough/cover%20(9).png
---

# Recon

这台机器开放`smtp`、`http`以及两个未知高位端口

![image-20251017231644763](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251017231644763.png)

## http

网页前端有一个路径`sev-home`，访问后弹出`basic`认证

![image-20251018012521652](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251018012521652.png)

网页源代码中发现`terminal.js`，其中泄露了`boris`密码，解码后得到`InvincibleHack3r`

![image-20251018012642698](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251018012642698.png)

登陆后提示这个系统做了很严格的安全配置，其中把`pop3`服务部署在了高位端口上

![image-20251018015528796](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251018015528796.png)

## pop3

侦察阶段得到的两个高位端口使用nc连接，能确定`55007`端口开放`pop3`

![image-20251018015637172](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251018015637172.png)

源代码中提示超级管理员是`natalya`和`boris`

![image-20251018015723972](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251018015723972.png)

# Blasting POP3 to get Boris's credentials

使用`hydra`爆破，得到`boris:secret1!`

![image-20251018015813914](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251018015813914.png)

共有3封邮件，但内容没什么有趣的

![image-20251018021126422](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251018021126422.png)

![image-20251018021203572](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251018021203572.png)

# Blasting POP3 to get natalya's credentials

进一步爆破`natalya`用户，得到`natalya:bird`

![image-20251018021245172](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251018021245172.png)

认证后其中有两封邮件，第二封泄露了`xenia:RCP90rulez!`凭证，并且暴露了`/gnocertdir`路径，提示需要写入`/etc/hosts`后访问

![image-20251018021711388](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251018021711388.png)

访问后是一个`Moodle`学习平台，使用`xenia`用户登录

![image-20251018021912807](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251018021912807.png)

在message中看到历史对话中`doak`教授提到可以通过他的email用户名`doak`与他联系

![image-20251019152724384](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019152724384.png)

# Blasting POP3 to get doak's credentials

爆破`doak`得到`doak:goat`

![image-20251019205551918](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019205551918.png)

有1封邮件，其中包含`dr_doak:4England!`凭证

![image-20251019205641934](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019205641934.png)

登陆后发现存在`private files`

![image-20251019210219688](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019210219688.png)

其中存在`s3cret.txt`

![image-20251019210240825](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019210240825.png)

内容说明一位特工已经获得了admin的明文凭证，通过`/dir007key/for-007.jpg`将会发现`Something juicy`

![image-20251019210401357](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019210401357.png)

下载这张图片，通过`exiftool`在`Image Description`中得到base64编码，解码得到`xWinter1995x!`

![image-20251019210903371](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019210903371.png)

# shell as www-data by moodle-admin

登录moodle后台后可以通过aspell getshell，它是moodle编辑内容时使用的editor的拼写检查器

将`path to aspell`填入反弹shell的命令

![image-20251019213331832](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019213331832.png)

然后需要在`plugins -> Text editors -> TinyMCE HTML editor`中将`Spell Engine`改为`PSpellShell`

![image-20251019214228716](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019214228716.png)

然后在editor中触发拼写检查，即可得到反弹shell

![image-20251019214330277](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019214330277.png)

![image-20251019214404173](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019214404173.png)

# shell as root by kernel privileged esclate

枚举系统信息，是`ubuntu 14.0.4.1 LTS`，内核版本为`3.13.0-32-negeric`，存在提权漏洞

![image-20251019220746039](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019220746039.png)

使用`37292.c`

![image-20251019220846067](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019220846067.png)

但发现目标机器没有`gcc`，使用`cc`代替

但编译后执行发现报错

![image-20251019220948996](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019220948996.png)

这是由于exp内编译lib还是使用的`gcc`，手动修改代码改为`cc`后重新上传编译执行即可
![image-20251019221203324](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019221203324.png)

![image-20251019221238913](./../assets/images/2025-10-18-GoldenEye-Walkthrough/image-20251019221238913.png)
