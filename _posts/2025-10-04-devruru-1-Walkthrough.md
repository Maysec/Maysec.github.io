---
title: devguru-1 Walkthrough
date: 2025-10-05
categories: ['walkthrough','vulnhub']
tags: ['cms','gitea']
description: .git泄露，cms打点、gitea提权、sudo提权
author: may
image:
  path: ./../assets/images/2025-10-04-devruru-1-Walkthrough/cover%20(6).png
---

# Recon

这台机器开放了标准端口的`ssh`、`http`和`8585/tcp`的Golang web

![image-20251004160659808](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004160659808.png)

## Web

80端口是一个官网

![image-20251004160904068](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004160904068.png)

8585端口是`Gitea`

![image-20251004160943193](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004160943193.png)

对80端口目录扫描，发现存在`.git`泄露以及`/backend`后台

![image-20251004194542504](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004194542504.png)

使用`git-dumper`转储，发现存在`adminer.php`

![image-20251004194800930](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004194800930.png)

在`conf/database.php`中得到数据库凭证

![image-20251004195025548](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004195025548.png)

登录`adminier`，查询数据得到`Frank`密码hash

![image-20251004195256667](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004195256667.png)

使用`https://www.tunnelsup.com/hash-analyzer/`判定为`bcrypt`

使用`https://bcrypt-generator.com/`生成bcrypt，修改密码hash为已知密码hash进行登录

![image-20251004200322343](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004200322343.png)

![image-20251004200511814](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004200511814.png)

# shell as www-data by october-cms

根据页面内容能发现这是`october-cms`

编辑`Home page`，在`code`中写入`onStart()`生命周期函数，写入`myVar`变量一句话木马

![image-20251004203001709](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004203001709.png)

在`markup`中添加模板标签调用`myVar`

![image-20251004204217290](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004204217290.png)

传递`?cmd`参数执行命令，使用`wget`落地`reverse.php`反弹shell

![image-20251004204231369](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251004204231369.png)

![image-20251005131904662](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005131904662.png)

# shell as frank by gitea

例行检查，发现`frank`系统用户，8585的`gitea`是以用户`frank`身份启动

那么当前的重点就是通过`gitea` getshell

![image-20251005132325945](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005132325945.png)

查看`/etc/gitea/app.ini`，没有权限

通过`find`命令发现`/var/backups/app.ini.bak`

![image-20251005132544428](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005132544428.png)

得到数据库账号密码

![image-20251005133036146](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005133036146.png)

得到`frank`密码hash，此处使用的是`pdkdf2`

![image-20251005133433719](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005133433719.png)

修改密码hash和加密算法，使用`bcrypt`

![image-20251005133719218](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005133719218.png)

登录成功

![image-20251005133751213](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005133751213.png)

`gitea`版本为`1.12.5`，存在后台RCE

在`Git Hooks`中添加反弹shell代码

![image-20251005134617669](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005134617669.png)

然后修改仓库`Readme.md`后提交，会触发`git commit`然后被`git hooks`捕获触发反弹shell代码

![image-20251005134941059](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005134941059.png)

# shell as root by sudo

例行检查发现能sudo执行`/usr/bin/sqlite3`，但是只能使用非root权限

![image-20251005135117435](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005135117435.png)

`sudo -V`查看版本，能对应上一个`bypass`漏洞`https://www.exploit-db.com/exploits/47502`

![image-20251005135226481](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005135226481.png)

使用poc getshell

![image-20251005135635899](./../assets/images/2025-10-04-devruru-1-Walkthrough/image-20251005135635899.png)
