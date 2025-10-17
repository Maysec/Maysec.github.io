---
title: Fristileaks:1.3 Walkthrough
date: 2025-10-17
categories: ['walkthrough','vulnhub']
tags: ['war-deploy','crontab-pe','crontab-pe']
description: 文件上传打点，crontab水平提权，sudo纵向提权
author: may
image:
  path: ./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/cover%20(10).png
---

# Recon

这台机器仅开放http服务

![image-20251015171937684](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251015171937684.png)

## http

目录扫描无果，尝试访问靶机名称路径`/fristi`，发现一个登录页面

![image-20251016135743996](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251016135743996.png)

源代码中有一段注释，其中`eezeepz`可能是用户名

![image-20251017204035658](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017204035658.png)

还有一段`base64`，解码发现是图片二进制

![image-20251017204105612](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017204105612.png)

解码后写入文件，打开图片得到一串字符`keKkeKKeKKeKkEkkEk`

![image-20251017204215292](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017204215292.png)

使用`eezeepz:keKkeKKeKKeKkEkkEk`登录

![image-20251017204315071](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017204315071.png)

存在文件上传功能点

![image-20251017204341808](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017204341808.png)

# shell as apache by file-upload

测试上传点，MIME与文件头都无法单独绕过上传限制，通过更改后缀名增加`.jpg`上传

![image-20251017204843300](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017204843300.png)

奇怪的是直接访问`/uploads/reverse.php.jpg`能被解析反弹到shell

![image-20251017205708494](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017205708494.png)

# shell as admin by crontab

例行检查发现`/home/eezeepz/notes.txt`，其内容表明允许当前用户以`admin`用户身份执行`/usr/bin/`目录下所有命令

![image-20251017211438029](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017211438029.png)

只需要把执行的命令写入`/tmp/runthis`，结果会在`/tmp/cronresult`显示

使用`/usr/bin/perl`反弹shell，将命令写入`/tmp/runthis`

![image-20251017211556223](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017211556223.png)

反弹shell成功，得到admin权限

![image-20251017211717947](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017211717947.png)

# shell as fristigod by crypto

例行检查在`/home/admin`下发现`cryptedpass.txt`和`cryptpass.py`

已知密文和加密方式那么很好逆

python代码能看出来通过`base64 -> reverse -> rot13`进行的加密

![image-20251017213310848](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017213310848.png)

那么反过来解密即可

`mVGZ3O3omkJLmy2pcuTq` -> `zITM3B3bzxWYzl2cphGd` -> `dGhpc2lzYWxzb3B3MTIz` -> `thisisalsopw123`

得到的密码通过`sudo -l`测试发现密码正确，但没什么用

![image-20251017213706312](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017213706312.png)

继续枚举，发现`whoisyourgodnow.txt`，其所属于`fristigod`用户创建

![image-20251017213737743](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017213737743.png)

使用同样的算法解密

`=RFn0AKnlMHMPIzpyuTI0ITG` -> `=ESa0NXayZUZCVmclhGV0VGT` -> `TGV0VGhlcmVCZUZyaXN0aSE=` -> `LetThereBeFristi!`

得到密码后`su fristigod`

![image-20251017213949164](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017213949164.png)

# shell as root by sudo

例行检查，发现能以`fristi`用户身份执行`/var/fristigod/.secret_admin_stuff/doCom`

![image-20251017214158644](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017214158644.png)

sudo执行，发现uid为0，等同于root权限

![image-20251017214401135](./../assets/images/2025-10-15-FristLeaks-1.3-Walkthrough/image-20251017214401135.png)
