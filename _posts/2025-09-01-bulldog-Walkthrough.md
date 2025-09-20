# Recon

这台机器开放了`ssh`和两个`WSGIServer`

![](assets/images/2025-09-01-bulldog-Walkthrough/0226476f-5476-4177-9b67-e638ceed6e18.png)

# Access Web-shell by leak hash

两个`WSGIServer`前端都很简单

![](assets/images/2025-09-01-bulldog-Walkthrough/ad0ff9b3-5908-4bd7-914e-4b8330a88858.png)

目录扫描有`robots.txt`，其中不存在有效攻击向量

`/admin`目录是`django administration`

![](assets/images/2025-09-01-bulldog-Walkthrough/5d7d97c7-081d-45c4-8978-976df147dac5.png)

`/dev/shell`是一个`web-shell`，需要认证

![](assets/images/2025-09-01-bulldog-Walkthrough/54f7a8ec-747c-4abb-860f-6fe95b0b5594.png)

`/dev`目录下有一份运维团队人员联系方式名单，源代码中有密码`hashes`

![](assets/images/2025-09-01-bulldog-Walkthrough/5d788362-e43a-4e93-a38e-e6ba7deb2858.png)

![](assets/images/2025-09-01-bulldog-Walkthrough/9467ea35-96e6-4f67-bd82-84d3da719eff.png)

使用`crackstation.net`批量跑一下

![](assets/images/2025-09-01-bulldog-Walkthrough/eab07cdf-447d-4fa3-ba1f-b3d50aa65e5c.png)

那么能得到两组凭证：[`nick@bulldogindustries.com`](mailto:nick@bulldogindustries.com)`:bulldog`和[`sarah@bulldogindustries.com`](mailto:sarah@bulldogindustries.com)`:bulldoglover`

# shell as django by web-shell bypass

使用`sarah:bulldoglover`成功登录`django administrator`

![](assets/images/2025-09-01-bulldog-Walkthrough/ecd0f9b5-71ec-4b58-8502-eba02a3c51ea.png)

同时获得`Web-shell`权限

![](assets/images/2025-09-01-bulldog-Walkthrough/56e35cf7-20a3-4981-b9a6-b34c6ccafbf2.png)

这个`web-shell`只允许执行特定命令，经测试发现可以通过`&&`命令执行

![](assets/images/2025-09-01-bulldog-Walkthrough/21768b48-3476-4edb-8a22-23c6cd866736.png)

通过`echo {payload}|base64 -d|bash`的方式反弹shell即可

![](assets/images/2025-09-01-bulldog-Walkthrough/e714bd99-82b9-4d99-bad7-0629c6e08609.png)

# shell as root by crontab

例行检查，发现`/etc/cron.d`目录下存在`runAV`计划任务，目标文件`/.hiddenAVDirectory/AVApplication.py`可写

![](assets/images/2025-09-01-bulldog-Walkthrough/aa2ec1f5-b02f-4d99-8e9e-8253853a8548.png)

写入python反弹shell代码即可

![](assets/images/2025-09-01-bulldog-Walkthrough/0d98fea1-d18d-498f-bcca-fbdb4a51cda2.png)
