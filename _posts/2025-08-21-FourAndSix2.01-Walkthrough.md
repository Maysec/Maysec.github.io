---
categories:
- 技术分享
date: 2025-09-19 19:14:23 +0800
description: Recon
tags:
- 迁移文章
title: Recon
toc: true
---

* 通过`fping`定位靶机ip
    
* `nmap`进行全端口扫描
    

![](../assets/images/9896f237-7dbc-477d-9017-e7f8e52024a7.png_align__center_)

从扫描结果上看这台机器似乎没有Web 一眼看上去的能开展攻击动作的只有111/tcp端口

使用`nmap script`针对性的进行扫描，发现其中有一个`backup.7z`

![](../assets/images/1f78d645-9299-4858-b6f7-eb35a34b0def.png_align__center_)

# mount → crack \* 2 → shell as user

### mount

挂载nfs共享目录

![](../assets/images/1b155ead-e638-4ec9-92ba-42e40e78faeb.png_align__center_)

尝试解压，发现有一些图片以及一对公私钥，但是存在密码

![](../assets/images/1b36f510-fd02-4f49-9f2a-7517b23a67a2.png_align__center_)

### crack

使用`7z2john`将backup.7z导出hash，然后交给`hashcat`进行爆破

```bash
$> 7z2john backup.7z
$> hashcat -a 0 -m 11600 hash.txt /usr/share/wordlists/rockyou.txt
...:chocolate
```

图片暂时没看出来包含什么信息，通过ssh指定私钥进行登录发现有二次验证

![](../assets/images/c17bc72e-ef15-4b9c-999e-fecec455950f.png_align__center_)

通过`ssh2john`导出hash，然后交给john进行爆破（hashcat不知道为什么识别不到hash）

原来是弱口令，用户名在`id_rsa_pub`中能看到是`user`

![](../assets/images/ae1759ab-cb84-4bb0-b98c-c88101e52ad0.png_align__center_)

### shell as user

![](../assets/images/399fa594-a21e-4730-bf60-742b6bbc1d3e.png_align__center_)

# doas → shell as root

通过`find / -user root -perm -4000`查找suid二进制，没有发现什么特别的

![](../assets/images/defb3ffe-0203-42a9-880e-0a1c44163573.png_align__center_)

需要注意的是在前期的信息收集中，发现这台机器是`OpenBSD`，与`debian`等发行版有很大区别，比如没有`sudo`，而是`doas`

这台机器也没有`curl`和`wget`，可以通过`nfs`同步落地文件，通过`linpeas.sh`发现了一些有趣的内容

发现我们可以无密码以`root`身份读取`/var/log/authlog`，这个可读的文件本身可能没有什么可利用点，但less可以使用vi/vim的提权方式

![](../assets/images/415e9d93-5acf-4b84-b20a-d4e391b3b807.png_align__center_)

通过`doas /usr/bin/less /var/log/authlog`进行调用，然后通过`:/bin/sh`进行提权

![](../assets/images/5856f569-f5a8-462d-9ab6-316e03aeffbe.png_align__center_)

# Some extended

> 在阅读`GTFOBins`时发现很多命令都可以通过`:/bin/sh`提权，包括但不限于vi,vim,more,less,apt，这是为什么？

其实这些命令本质上叫做`pager`命令，本质上就是这些命令都有在内部调用外部命令的能力，这并非漏洞，而是一种`feature`，但不安全的配置比如`sudoers`、`doas`配置都可能导致越权