# Recon

这台机器开放了标准端口的`ftp`、`ssh`、`http`、`mysql`和非标端口的`12380 - http`

![](assets/images/2025-09-11-stapler-Walkthrough/f04ff687-4140-4e6b-98df-7bcd24f79f13.png)

# ftp

存在匿名登陆

![](assets/images/2025-09-11-stapler-Walkthrough/95c61d77-fb14-4dba-9f18-3e787757d21c.png)

`note`文件内容暴露出两个用户名：`Elly,John`

`Elly, make sure you update the payload information. Leave it in your FTP account once your are done, John.`

## Web

`80/tcp`是一个`php-cli`启动的页面，目录扫描无果

![](assets/images/2025-09-11-stapler-Walkthrough/71ab09b3-ee53-4a12-a30a-5aa4a45e96be.png)

`12380/tcp`似乎是一个cms，同样目录扫描无果

# acess common user ftp privileges

对于两个`web`都没有任何进展，这时只能继续考虑`ftp`带来的信息，及`Elly`和`John`这两个用户名

通过`hydra`爆破，得到`elly:ylle`凭证

登陆后发现`ftp`目录共享的是整个`/etc`目录，但不包括`/etc/shadow`

![](assets/images/2025-09-11-stapler-Walkthrough/5ab6628a-c9ae-4bdb-a7bc-d886f3b956a0.png)

# shell as SHayslett by burp

通过`/etc/passwd`能得到这台机器的合法可登录用户

通过`cat passwd|grep bash|awk -F: '{print $1}'`筛选出用户名并写入`users`作为爆破字典

![](assets/images/2025-09-11-stapler-Walkthrough/fee4f1b6-c5cc-4075-b2b8-e34d0b984db3.png)

通过`hydra -L users -e nsr`来进行爆破,`-e nsr`参数告诉`hydra`尝试`users`字典的每个用户名空口令登录、密码与用户名一致登录、用户名反转作为密码登录

爆破得到ssh凭据`SHayslett:SHayslett`

![](assets/images/2025-09-11-stapler-Walkthrough/a5b2c291-76c6-4115-b58e-7d05130639cc.png)

例行检查，发现`/var/www/https`下存在`robots.txt`

`blogblog`目录下发现这是一个`wordpress`，随即在`wp-config.php` 中得到`mysql`用户密码

# 3 ways to gain root privileges

## kernel privileges escalation

搜索`4.4`内核版本和`ubuntu`系统关键字找找合适的

![](assets/images/2025-09-11-stapler-Walkthrough/2c52340f-30b5-4820-99a0-bf5021dfbfce.png)

决定使用`39772.txt`，这个文件并没有直接携带`exp`，其中存放了`exp`地址

`https://gitlab.com/exploit-database/exploitdb-bin-sploits/-t/raw/main/bin-sploits/39772.zip`

在攻击机下载后解压通过`python -m http.server`启动临时服务器，然后靶机上落地`exp`

![](assets/images/2025-09-11-stapler-Walkthrough/731aa7ff-4176-421b-915a-f8338a75e73e.png)

执行`compile.sh`后运行生成的`doubleput`即可提权

![](assets/images/2025-09-11-stapler-Walkthrough/933528e7-26a0-443a-8a3c-d141682968e3.png)

## crontab

在`linpeas`例行检查时发现`/usr/local/sbin/cron-logrotate.sh`，这个文件属于root，当前用户可写

![](assets/images/2025-09-11-stapler-Walkthrough/ca7e5b82-8de6-4428-9e01-d43d83530200.png)

这个脚本被每5分钟以`root`权限执行，那么直接计划任务反弹shell即可

![](assets/images/2025-09-11-stapler-Walkthrough/33f96cbb-6107-4cc8-8e87-b0eb413ef50f.png)

![](assets/images/2025-09-11-stapler-Walkthrough/f5df0758-536b-4d98-acb0-72c191d3cb6d.png)

![](assets/images/2025-09-11-stapler-Walkthrough/ab3b223c-4dd8-4eda-a8b9-d860ca3ca89c.png)

## common logic

例行检查时发现`/home/JKanode/.bash_history`泄露了两个用户名密码

![](assets/images/2025-09-11-stapler-Walkthrough/065e5c6f-9e9d-42f1-b96c-b8601ae01a6b.png)

`peter`用户存在`sudo`权限，`sudo su`即可

![](assets/images/2025-09-11-stapler-Walkthrough/5c5a8761-6e42-4611-a509-29f565b4244e.png)
