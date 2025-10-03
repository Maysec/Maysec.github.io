---
title: DC9 Walkthrough
date: 2025-10-03
categories: ['walkthrough','vulnhub']
tags: ['fuzz']
description: sqli->fuzz打点，sudo提权
author: may
image:
  path: ./../assets/images/2025-10-03-DC9-Walkthrough%20/cover%20(4).png
---

# Recon

这台机器仅开放标准端口`http`

![image-20251003154536728](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003154536728.png)

## http

目录扫描类似于一个`cms`，逐个功能点看一看

![image-20251003154653122](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003154653122.png)

`manage.php`有一个登录入口

![image-20251003194358270](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003194358270.png)

`display.php`显示了几条数据

![image-20251003162825797](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003162825797.png)

`search.php`存在sqli

![image-20251003163923081](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003163923081.png)

在`Staff.Users`表得到用户名和密码hash

![image-20251003185539416](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003185539416.png)

`crackstation`得到`transorbitall`

![image-20251003185610457](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003185610457.png)

登录后回显`File does not exist`，猜测此处可能存在文件包含

![image-20251003194447708](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003194447708.png)

fuzz得到`?file`参数

![image-20251003194519735](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003194519735.png)

使用`/usr/share/wordlists/seclists/Fuzzing/LFI/LFI-etc-files-of-all-linux-packages.txt`fuzz目录，发现`/etc/knockd.conf`

![image-20251003200343980](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003200343980.png)

发现可以`Port knocking`打开`ssh`

![image-20251003200559478](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003200559478.png)

![image-20251003201657332](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003201657332.png)

sqlmap导出`users.UserDetails`表`username`和`password`字段

![image-20251003201741940](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003201741940.png)

通过`awk`处理得到账号和密码本

![image-20251003202211388](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003202211388.png)

得到三对有效凭证

![image-20251003202321300](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003202321300.png)

分别登录这三个用户，`sudo -l`发现都没有权限

在`/home/janitor/.secrets-for-putin`中发现`passwords-found-on-post-it-notes.txt`

![image-20251003203433147](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003203433147.png)

查看发现是几个密码，将其添加到密码本中

![image-20251003203526790](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003203526790.png)

得到新用户`fredf:B4-Tru3-001`

![image-20251003203700911](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003203700911.png)

登录后发现其有root权限执行`/opt/devstuff/dist/test/test`的能力

![image-20251003204036383](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003204036383.png)

查找`test.py`查看代码，其接收两个值且都为文件，将值1对应的文件内容append到值2所指的文件路径

比如`sudo /opt/devstuff/dist/test/test  /etc/shadow /tmp/shadow.txt`，执行后`/tmp/shadow.txt`就被写入了`/etc/shadow`文件内容

![image-20251003210639805](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003210639805.png)

通过生成密码hash，编写passwd格式的字符串写入/etc/passwd提权

![image-20251003215000113](./../assets/images/2025-10-03-DC9-Walkthrough%20/image-20251003215000113.png)