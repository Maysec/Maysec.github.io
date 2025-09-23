---
title: mhz_cxf_c1f Walkthrough
date: 2025-08-27
categories: ['walkthrough','vulnhub']
tags: ['boring']
author: may
description: 信息泄露打点，sudo提权
image:
  path: ./../assets/images/2025-08-27-mhz_cxf_c1f-Walkthrough/cover%20(29).png
---

# Recon

这台机器仅开放`ssh`和`web`

![](../assets/images/2025-08-27-mhz_cxf_c1f-Walkthrough/1e60e3f3-f085-4a88-82d3-9efb368e3022.png)

web前端是`apache default page`

![](../assets/images/2025-08-27-mhz_cxf_c1f-Walkthrough/ec4e7456-50c3-438c-b002-213c2c9cc5b5.png)

# shell as first\_stage by remb.txt

`feroxbuster`扫描得到`notes.txt`

![](../assets/images/2025-08-27-mhz_cxf_c1f-Walkthrough/cae9f0ea-30ae-401a-afb6-4aac9440642c.png)

`notes.txt`回显的内容中包含了`remb.txt`和`remb2.txt`

```php
1- i should finish my second lab 
2- i should delete the remb.txt file and remb2.txt
```

`remb.txt`回显`first_stage:flagitifyoucan1234`，`remb2.txt`访问不存在

将`remb.txt`回显内容作为登录凭证取得`first_stage`用户权限

![](../assets/images/2025-08-27-mhz_cxf_c1f-Walkthrough/6fc65d98-7277-4a67-b08d-5c3d9a4cb9f6.png)

# shell as mhz\_c1f by steghide

例行检查，发现存在`mhz_c1f`普通用户

![](../assets/images/2025-08-27-mhz_cxf_c1f-Walkthrough/723e4831-3fd1-4f53-9519-c6bc5a94a3cd.png)

在`mhz_c1f`的`home`目录下发现四张图片，打包出来分析

![](../assets/images/2025-08-27-mhz_cxf_c1f-Walkthrough/4847b626-ddf2-4f7d-b609-6371c417cdb2.png)

逐一使用`steghide extract -sf`分析，在`spinning the wool.jpeg`中提取出`remb2.txt`

![](../assets/images/2025-08-27-mhz_cxf_c1f-Walkthrough/328280f6-f991-443b-b5a1-c74a86ec9488.png)

# shell as root by sudo

其中包含`mhz_c1f`用户口令，`su`切换用户

![](../assets/images/2025-08-27-mhz_cxf_c1f-Walkthrough/6f5f6201-0e43-4095-a1b0-da6f8f5c1f23.png)

例行检查，发现可直接`sudo`提权

![](../assets/images/2025-08-27-mhz_cxf_c1f-Walkthrough/0cc54166-3f84-44bd-a5c3-ede261ca1b8e.png)
