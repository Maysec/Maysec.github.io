# Recon

这台机器仅开放标准端口的`ssh`和`web`

![](assets/images/2025-09-05-Election-Walkthrough/3c3d817b-12b4-4bad-92f3-c54d810a8338.png)

## Web

`robots.txt`暴露了一些关键字，只有`election`为真实路径，另外的可能是框架名、用户名

![](assets/images/2025-09-05-Election-Walkthrough/75002123-7524-45b8-88bd-1ed0ef924e70.png)

`/election`路径似乎是一个在线投票系统

![](assets/images/2025-09-05-Election-Walkthrough/7faf857e-2d19-4649-8dc6-b1431186ad67.png)

二级目录的扫描主要得到了`admin`，有一个比较关键的路径`/election/admin/logs/system.log`

其中得到了一对凭证`love:P@$$w0rd@123`

![](assets/images/2025-09-05-Election-Walkthrough/27c9665e-d2ab-4908-9c16-a69872b3ea1c.png)

这对凭证无法登录`admin`

![](assets/images/2025-09-05-Election-Walkthrough/561528e7-db99-4d2e-a9b8-473e0f69bc84.png)

# shell as love by password leak

经过一番测试，发现泄露的凭证可以登录ssh

![](assets/images/2025-09-05-Election-Walkthrough/588deac5-5763-4c88-90d1-3768115bfc34.png)

# shell as root by Serv-U

信息收集发现有`Serv-U`，`searchsploit serv-u`找`linux/local`系列即可

![](assets/images/2025-09-05-Election-Walkthrough/d479b86e-25c7-4472-9cd3-6c780fdf912e.png)
