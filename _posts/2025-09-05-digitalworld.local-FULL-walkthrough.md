# Recon

这台机器开放了`ssh`、`web` 、`samba`、`mysql`

![](assets/images/2025-09-05-digitalworld.local-FULL-walkthrough/1bea0eb0-e5c0-4118-9374-c80b93bc8d6a.png)

# Web

80和443应该是同一个程序，使用的是`CMS Made simple 2.2.15`

![](assets/images/2025-09-05-digitalworld.local-FULL-walkthrough/b6be7f60-cf27-4fda-82ad-d1b559a63f75.png)

9090是一个`cockpit`面板

# shell as qiu by LFI

从`cmsmadesimple`开始，已知漏洞测试均不存在，目录扫描发现`test.php`，访问后弹窗`missing get parameter`

`fuzz`参数，发现存在`file`参数任意文件包含

![](assets/images/2025-09-05-digitalworld.local-FULL-walkthrough/3db804a1-e210-432e-aeb6-74635156ceab.png)

包含`/etc/passwd`文件，发现用户`qiu`是有效用户

![](assets/images/2025-09-05-digitalworld.local-FULL-walkthrough/77da1db1-301e-4b41-a8f7-adb6ff00ce23.png)

下载私钥，免密登录

![](assets/images/2025-09-05-digitalworld.local-FULL-walkthrough/6ab8c676-be65-4d66-a982-f8993a3fd556.png)

信息收集，得到`qiu`密码为`remarkablyawesomE`

![](assets/images/2025-09-05-digitalworld.local-FULL-walkthrough/3be80741-621c-444d-b0ff-75534dde4292.png)

# shell as root by suid

`qiu`用户可以直接`sudo su`，也可以通过`capabilities`提权

![](assets/images/2025-09-05-digitalworld.local-FULL-walkthrough/05014b5a-cf9e-4d7c-a7a4-f855f07e9e0a.png)
