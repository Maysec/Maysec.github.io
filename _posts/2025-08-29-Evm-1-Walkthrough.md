---
title: Evm:1 Walkthrough
date: 2025-08-29
categories: ['walkthrough','vulnhub']
tags: ['cms']
author: may
description: wordpress打点，root密码泄露提权
image:
  path: ./../assets/images/2025-08-29-Evm-1-Walkthrough/cover%20(26).png
---

# Recon

机器开放`ssh`、`dns`、`web`、`mail`、`445`

![](../assets/images/2025-08-29-Evm-1-Walkthrough/ddae8b0a-c417-4697-97ed-458262e10326.png)

网页前端是`apache default page`，目录扫描存在`wordpress`和`info.php`

![](../assets/images/2025-08-29-Evm-1-Walkthrough/5ecc3bae-949d-4dde-8abe-9b6bfe8c2a1f.png)

`wordpress`访问发现css无法加载，因为其向`192.168.56.103`发起的静态资源请求，但这并不是我们的ip

![](../assets/images/2025-08-29-Evm-1-Walkthrough/d5020565-a2fd-4835-8d1d-b1569e1f175c.png)

# shell as www-data by wordpress

前端资源文件的加载异常不影响渗透工作的进行，直接上`wpscan`扫描

`wpscan -eu`参数可以通过对可观测前端信息进行用户枚举，得到`c0rrupt3d_brain`用户

![](../assets/images/2025-08-29-Evm-1-Walkthrough/bbdbd81d-4ad0-479d-8ca2-cfb9ff1e4533.png)

继续使用`wpscan`进行密码爆破 → `wpscan --url {} --usernames {} --password{}`

\[SUCCESS\] - c0rrupt3d\_brain / 24992499

使用`wp_admin_shell_upload`Getshell

![](../assets/images/2025-08-29-Evm-1-Walkthrough/faab4931-ae0c-4c75-aee8-59c71a78df02.png)

`meterpreter`的`shell`不好用，弹给`pwncat-cs`开展后续渗透

# shell as root by password leak

例行检查中发现`/home/root3r/.root_password_ssh.txt`文件，尝试`su`到`root`，发现密码正确

![](../assets/images/2025-08-29-Evm-1-Walkthrough/07e1f260-af57-4218-b0ba-1904306ff458.png)
