# Recon

这台机器开放了`ssh`、`samba`和`web`，其中还有少见的`113/tcp` ident服务

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/a48a3446-04c6-4797-8b47-d64a05dc2be5.png)

## 113/tcp → ident

通过`ident-user-enum`工具枚举，得到`ident`用户名

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/a16080b8-b21f-43e7-8383-02907f2ca4db.png)

## 8080/http

网页前端能收集到一些信息

* `/html-pages`路径
    
* `patrick@goodtech@.com.sg`邮箱
    

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/a22dabf4-6e0e-4c59-a91a-0217a4ebeda0.png)

`/html_pages`目录展示了一些文件名，但未必是全面的

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/523e80b1-b1e7-45d1-acbf-96efaf43b88d.png)

目录扫描得到一个关键的`test.pcap`文件

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/c7bcf115-64d9-4537-a04e-f7d373cb25be.png)

在其中得到了两个关键路径

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/012f0ddf-5f29-4cb5-9215-ab261bd88a26.png)

`developmentsecretpage/directortestpagev1.php`在说这是用来向主任实时更新信息的页面

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/842cb258-60c9-40c9-87e4-8c2c63bc15a5.png)

在源代码注释中是主任和`patrick`的对话，主任对这种推送更新的方式表示不认可，并且说可以使用留言板来实现

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/dde80d8e-90a5-4c5e-9585-d25598a03e80.png)

# shell as intern by password leak

点击`log out`后跳转登录界面，但发现任意用户名密码多能登录成功

`development.html`源代码中发现路径`/developmentsecretpage`

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/f14e202f-ba99-4101-9e43-deb695a7ab23.png)

在登陆后的页面中都有两行报错

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/61b704d1-0e62-4f34-b555-979a9460f7f6.png)

通过搜索报错关键字找到`SiTeFiLo`组件漏洞，该组件脚本包含一个敏感的文件`slog_users.txt`，会存储用户名和密文密码

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/fa5ae9d7-e5b7-4a3e-bc08-30e82859061b.png)

在线爆破后得到两个明文，尝试ssh登录

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/d97c30ed-c9b3-41e3-9419-2251c0be7ec8.png)

`intern`登录成功

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/d1464e0f-542b-4b24-b0bf-e4bfb1457771.png)

经过检查，`intern`用户的`shell`为`lshell`，这是一个受限的shell只允许执行几个白名单命令

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/8d04f0e0-a5c4-4ff2-b995-cab30e4c2904.png)

可以通过`echo os.system('/bin/sh')`绕过`lshell`

通过`hashes.com`破解了`patrick`用户密码

`su`到`patrick`用户后`vim`提权即可

![](../assets/images/2025-09-03-digitalworld.local-DEVELOPMENT-Walkthrough/6870a492-de37-45bf-a432-4035b0b2376b.png)
