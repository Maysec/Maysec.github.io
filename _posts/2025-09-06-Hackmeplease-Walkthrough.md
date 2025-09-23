---
title: Hackmeplease Walkthrough
date: 2025-09-06
categories: ['walkthrough','vulnhub']
tags: ['cms']
author: may
description: cms打点，mysql数据横向用户提权，sudo提权
image:
  path: ./../assets/images/2025-09-06-Hackmeplease-Walkthrough/cover%20(12).png
---

# Recon

这台机器开放标准端口的`web`和`mysql`，其次还有不常见的`33060`

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/4688a47b-2b58-43df-b766-5b1408f80f10.png)

# shell as www-data by seeddms

从前端来看像一个`cms`，从前端源代码信息没发现是什么cms

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/50c84d9a-f432-42e5-99c6-650aa896e6e6.png)

目录扫描只得到了`css`、`front`、`js`等静态资源路径，没发现有动态交互的功能点

那么只能从`js`路径作为着力点，在`/js/main.js`注释中发现一个路径`/seeddms51x/seeddms-5.1.22/`

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/2f89558e-c560-41ff-8e17-7488ea2ba1af.png)

访问后是一个登录界面，并且得到指纹为`SeedDMS` → DMS → Document Management System 文档管理系统

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/5f80b0e9-02cb-4dfb-8a83-31c5f7333799.png)

`searchsploit seeddms`寻找`exp`，有两个`RCE`，但都是登陆后的，经测试不是默认密码

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/6b97185e-df2e-4cd3-940c-7da2f28fc3a0.png)

对一级目录扫描发现存在`conf`目录

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/963e296e-63ae-4963-b934-95be7d393db4.png)

查看开源项目源代码，发现存在`settings.xml.template`

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/fea97021-2d25-4d2a-bda0-347936ca6fdf.png)

指定目录和文件后缀扫描，得到`settings.xml`

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/7c7a55c3-6157-43d8-a91d-c73ba9058682.png)

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/c4511a24-32ab-412a-933a-bac0dd1c0121.png)

在其中得到`mysql`账号密码`seeddms:seeddms`

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/f546d1af-d00f-4379-afbf-d51c5852f2ca.png)

连接`mysql`，查看`seeddms.tblUsers`表，发现`admin`用户`password` hash爆破不了

查看开源项目`/SeedDMS/blob/master/op/op.Login.php` 发现密码为标准`md5`不加盐

那么手动写入一条数据添加admin用户`may`，或者更改admin密码

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/38adf7b7-084d-462e-aa1f-d3005609d660.png)

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/7ba46d0d-3f9f-44cc-bc12-4af6cb7f5110.png)

添加文档，在本地文件处上传`php-reverse-shell.php`

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/e534b715-f78f-4a79-8a7d-9173a570063c.png)

确认添加后可能发生`http 500`报错，但文件已上传

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/672a198f-643e-40eb-a93d-e94bcb9dfb82.png)

在`searchsploit`给的poc中发现访问`/data/1048576/$document_id/1.php`即可

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/69844ac3-764f-441f-ba27-9e85b7156780.png)

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/8c65506c-b88e-4764-8255-3ee6ca3136a4.png)

# shell as saket by attack-mysql

例行检查，发现存在`saket`用户，记起上文得到mysql权限时存在`users`表，其中存放了`saket`密码`Saket@#$1337`

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/1ea19ce3-1106-4d3c-b7dd-545889c51f49.png)

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/795f1316-9673-4bd1-a029-c5315ead26d4.png)

# shell as root by sudo

`su`到`saket`用户，然后直接`sudo su`到`root`用户

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/ec784e19-97f0-4418-8ac1-8b7728e16ac6.png)

![](../assets/images/2025-09-06-Hackmeplease-Walkthrough/97ba8ce1-048d-45e8-9c49-7519fc31b1fd.png)
