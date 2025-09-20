# Recon

机器开放了标准端口的`ftp`、`ssh`、`http`

![](assets/images/2025-09-03-Tr0ll-Walkthrough/209fa05d-4f1e-4f30-9adb-4b9fddc16576.png)

## ftp

`ftp`存在匿名登录，存放着一个`lol.pcap`数据包

![](assets/images/2025-09-03-Tr0ll-Walkthrough/1750f74e-4619-4d41-9193-94efa3f3ff3c.png)

## web

网页前端只有一张图片

![](assets/images/2025-09-03-Tr0ll-Walkthrough/30de87f0-7e26-4864-8891-064627dd7bd6.png)

目录扫描结果只有`robots.txt`，其中泄露了`/secret`路径，访问后依然是一张图片

分析流量包，主要是`ftp`流量，下载了一个`secret_stuff.txt`文件，文件内容得到了一串字符`sup3rs3cr3tdirlol`

可能是密码 也可能是路径

![](assets/images/2025-09-03-Tr0ll-Walkthrough/0f01861e-ca75-4e7e-8652-f665600f91ce.png)

先尝试路径，发现存在`roflmao`文件

![](assets/images/2025-09-03-Tr0ll-Walkthrough/f2778d52-9d43-4f87-ae58-36c440258b4d.png)

是一个`ELF`文件，运行给了一个16进制`0×0856BF`，通过ida看了一下这个程序与这个进制没有任何关系

![](assets/images/2025-09-03-Tr0ll-Walkthrough/6fc7e0ce-3a86-4665-b06b-ec87d955a99e.png)

测试后发现是网页路径，其中存放着一个密码和用户字典

![](assets/images/2025-09-03-Tr0ll-Walkthrough/fd71dbf5-fc37-4565-8030-f9fcfb90b7b0.png)

---

这台机器性能太差，ssh爆破会宕机

最后的解是`overflow:Pass.txt`登录后内核提权

无趣
