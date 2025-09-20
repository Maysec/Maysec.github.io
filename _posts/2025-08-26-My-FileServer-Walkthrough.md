# Recon

这台机器叫`FileServer`，从扫描结果来看开启了`ftp`、`nfs`、`samba`的确比较具象

除此以外还开放了`ssh`以及`web`

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/0c8d14d5-77be-4ed3-8cc1-d466771d366b.png)

## ftp - anonymous login - leak logs

ftp存在匿名登陆，存在`pub/log`目录，通过`mget *`指令下载所有文件

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/2364d9a2-14f8-47a7-b08b-2f7174143636.png)

存在一些没有权限下载的文件

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/69db6330-c6bb-4a5f-821d-954b82cf9b5a.png)

## nfs → smb

发现存在`smbdata`目录，但只允许`192.168.56.0/24`网段范围内IP挂载

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/4f382f68-70fb-41c3-857d-ff448814edf3.png)

根据`smbdata`命令能猜测`samba`服务可能有访问权限

使用`smbmap`扫描，并使用`smbclient`连接发现需要密码

`smbuser`应该是运行`samba`服务的用户名

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/af94aa1f-ed7c-4c3b-bc8e-395777b7cc1d.png)

## 80 → web

web前端只有一个外链`href`,目录扫描看一下

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/cd8f9bd7-6154-46a8-8db5-534ecb7afe9e.png)

`feroxbuster`发现`readme.txt`

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/80e84e16-e5d8-4e63-b358-29e3c732de1a.png)

# shell as smbuser by readme.txt

`/readme.txt`返回了密码`rootroot1`，可能是上文收集到的`smbuser`用户密码

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/3dfea7ef-f32d-40f6-86e7-3f42a10d2fad.png)

发现这个用户可以登录ftp，但无法登录ssh

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/9b3b74a0-ae4a-44e4-a0a0-1d486ecccc59.png)

因为ssh配置关闭了密码登录而只允许私钥登录

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/c287b9a6-b5c9-4249-b989-913252c334aa.png)

那么就登录ftp创建`.ssh`文件夹，然后上传公钥到`authorized_keys`实现免密登录

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/a4b88a3d-bc86-4009-bf3e-0b0dd83549b5.png)

使用`id_rsa`进行私钥登录

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/17357601-a27d-4ea6-8b5a-9304fac46451.png)

# shell as root by dirtyCow

`40616.c` 提权失败….不玩了 内核提权没意思

![](../assets/images/2025-08-26-My-FileServer-Walkthrough/5447cdbc-3749-4fa8-a756-cd8a82070ec5.png)