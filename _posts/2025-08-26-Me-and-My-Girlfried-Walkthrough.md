---
title: Me-and-My-Girlfriend Walkthrough
date: 2025-08-26
categories: ['walkthrough','vulnhub']
tags: [' ']
author: may
description: ip限源XFF绕过、用户枚举ssh登录打点，sudo提权
image:
  path: ./../assets/images/2025-08-26-Me-and-My-Girlfried-Walkthrough/cover%20(32).png
---

# Recon

这台机器只开放ssh和web

![](../assets/images/2025-08-26-Me-and-My-Girlfried-Walkthrough/0d829f3a-c291-4659-aaae-7ed3a4edb087.png)

看看`feroxbuster`结果，有一些攻击向量

![](../assets/images/2025-08-26-Me-and-My-Girlfried-Walkthrough/6644188d-ae22-4087-a9ba-84208c1027ed.png)

`robots.txt`泄露`heyhoo.txt`路径

`heyhoo.txt`回显`Great! What you need now is reconn, attack and got the shell`

`config/`目录遍历存在`config.php`文件，打开后被解析无回显

`misc/`目录遍历存在`process.php`文件，打开后被解析无回显

# shell as alice by user\_id enum

网页前端回显`Who are you? Hacker? Sorry This Site Can Only Be Accessed local!`，似乎在指示`XFF`伪造

![](../assets/images/2025-08-26-Me-and-My-Girlfried-Walkthrough/f70eeaab-eee0-45e7-a155-afa49d24933e.png)

携带一系列源ip伪造的header

![](../assets/images/2025-08-26-Me-and-My-Girlfried-Walkthrough/3c70014f-6941-44c5-bea7-195daa0616c5.png)

经测试，目标识别`X-Forwarded-For`

![](../assets/images/2025-08-26-Me-and-My-Girlfried-Walkthrough/0ee3094b-d7fe-4407-8ce5-4c68132e8b6e.png)

注册一个账号，登陆后发现传递了`user_id=12`，尝试遍历`user_id`

![](../assets/images/2025-08-26-Me-and-My-Girlfried-Walkthrough/a08b4a30-1f22-4d43-82af-0a0a6505b83e.png)

由于`password`控件被`auto-fill`了，可以通过源代码直接查看到明文密码，并且通过尝试使用遍历得到的用户名密码登录ssh，在尝试到`user_id=5`时，发现`alice`用户可以正常登录

![](../assets/images/2025-08-26-Me-and-My-Girlfried-Walkthrough/6568f3e8-9f3d-4376-9cd1-15344c59211f.png)

# shell as root by sudo-php

基本的信息收集发现可以免密执行`php`，那么直接`php-reverse-shell.php`就行

![](../assets/images/2025-08-26-Me-and-My-Girlfried-Walkthrough/06435e5a-0081-4ac4-84e4-9dd201e9b935.png)