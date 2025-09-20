# Recon

这台机器开放`ssh`、`web`和`mysql`

![](../assets/images/2025-09-01-blackrose-Walkthrough/c854b697-370b-4597-bb2b-f0cf55eea6ca.png)

网页前端为登陆界面，存在注册点

![](../assets/images/2025-09-01-blackrose-Walkthrough/bb7e93b6-c3ee-45c6-a5d7-d2063d85d53c.png)

---

测试小记：

* 用户名可以xss → 未接收到admin cookie
    
* admin用户爆破无果
    
* 登录、注册输入框注入无果
    
* `Rx.php`注入无果\\
    
* `password`字段使用`strcmp`函数猜测 → 成功绕过
    

# Access admin by strcmp vul

将登陆包`password=`改为`password[]=`即可绕过登录

![](../assets/images/2025-09-01-blackrose-Walkthrough/e0e1cae1-7657-4cd0-a01e-11106f559760.png)

登陆后有一串`Signature`，还有一个命令执行，但是执行会报`invalid signature`，可能这串`sign`与特定命令进行了绑定，所以没有权限执行其它命令

![](../assets/images/2025-09-01-blackrose-Walkthrough/9422ad36-5e8c-4a04-bdef-00d7f3b69e48.png)

尝试爆破，得到`whoami`，说明这个位置可以执行`whoami`命令

![](../assets/images/2025-09-01-blackrose-Walkthrough/7ce9d263-5d61-416e-9a1c-8c73b6a488b9.png)

# shell as www-data by signature command

现在知道命令执行与`sign`值挂钩，这串看起来像`bcrypt`加密

尝试手动加密`sign`值执行命令，发现思路可行

![](../assets/images/2025-09-01-blackrose-Walkthrough/29f1f8f2-dbdd-42de-ada9-7a84f33ad0b3.png)

那么生成python反弹shell命令后加密替换`sign`，命令执行后获得shell

![](../assets/images/2025-09-01-blackrose-Walkthrough/cbb09fe2-1a94-4f20-ac47-4946ab5cb1e7.png)

![](../assets/images/2025-09-01-blackrose-Walkthrough/70228d73-4bb7-4076-bb90-ee4fa6af4bed.png)

# shell as delx by ld.so

例行检查，发现能以`delx`用户权限执行`/bin/ld.so`

![](../assets/images/2025-09-01-blackrose-Walkthrough/f1408b11-2af7-4520-adaa-7f54981b26dd.png)

![](../assets/images/2025-09-01-blackrose-Walkthrough/c25734ac-d264-447e-b7c1-d0c70ff3644c.png)

# shell as yourname by misc

例行检查发现一个有意思的文件

![](../assets/images/2025-09-01-blackrose-Walkthrough/9934d570-83be-48d2-a480-e42490e744b4.png)

这个文件执行后看起来拥有了`root`权限，实际上无法执行命令

![](../assets/images/2025-09-01-blackrose-Walkthrough/8afcaf96-1c0c-4062-a145-fb8bcfa2a99d.png)

通过`ida`分析这个程序 整体来说是一个密钥验证的程序 通过逆向得到`gqSFGqAJ`

![](../assets/images/2025-09-01-blackrose-Walkthrough/5db2c5c1-9fa2-40ef-ac85-cdc4e4b3e1a6.png)

通过验证，但无事发生

![](../assets/images/2025-09-01-blackrose-Walkthrough/aeaa59e5-b2f5-4edc-a0a8-7f7579c68af2.png)

在`strings`中看到一串像`base64`的字符，解密无果，那么就是`aes`了

![](../assets/images/2025-09-01-blackrose-Walkthrough/8935c8ae-a657-4616-903a-98a43bf424db.png)

解密得到`RkZiPVkvxykJVOmxBmitBPeJXqFuxM`

![](../assets/images/2025-09-01-blackrose-Walkthrough/02edde4a-04a1-4ffb-a8dd-1e98f8f2d254.png)

这串密文是web首页`background-image.jpg`的隐写密码 得到一个`password`文件 看起来没有规律

![](../assets/images/2025-09-01-blackrose-Walkthrough/7145975b-2425-4e86-9418-b17cae1e09ae.png)

交给随波逐流一键解码得到`DX|g+lfMg^U**\Kzd{S]Hb$FV"o?v#`

![](../assets/images/2025-09-01-blackrose-Walkthrough/27026c91-3fd8-440f-830b-d17cf3f142eb.png)

例行检查时发现存在`yourname`用户，尝试登录

![](../assets/images/2025-09-01-blackrose-Walkthrough/e49a1153-aae8-454b-b50a-6b810a691478.png)

# shell as root by /usr/bin/blackrose

例行检查 发现能以root权限执行`/usr/bin/blackrose`

![](../assets/images/2025-09-01-blackrose-Walkthrough/d6fa275d-dafb-4878-b2d2-4934573bd883.png)

经过测试 发现可以执行php文件 但是危险函数被禁用

![](../assets/images/2025-09-01-blackrose-Walkthrough/e7a3d6d2-833b-4cd0-ba1f-072dfa9f7670.png)

不出意料`php-reverse-shell.php`也无法执行

![](../assets/images/2025-09-01-blackrose-Walkthrough/b699db94-22d4-4caa-a2a9-1a44462c29bb.png)

php反弹shell文件太大了不好bypass，用简短的方式执行`/bin/sh`即可

![](../assets/images/2025-09-01-blackrose-Walkthrough/d793e2ed-f456-4ffb-aeec-fd9632d300d9.png)

![](../assets/images/2025-09-01-blackrose-Walkthrough/4c59fc32-20ba-4ed2-ae91-0b7c6d561f24.png)
