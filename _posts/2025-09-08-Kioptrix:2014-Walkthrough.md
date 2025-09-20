# Recon

这台机器开放了标准端口的两个`web`

# shell as www-data by phptax-rce

`80/tcp`显示`It works!`，源码中有一个路径`pChart2.1.3/index.php`

![](assets/images/2025-09-08-Kioptrix-2014-Walkthrough/c85e5ad1-5e2a-4007-8f7b-70a656b796ed.png)

这是一个`chart`展示的php应用

![](assets/images/2025-09-08-Kioptrix-2014-Walkthrough/f558af3b-abae-47d8-b5ef-a6906c3c511c.png)

`searchsploit`发现这个版本存在文件包含漏洞`/index.php?Action=View&Script=/usr/local/etc/apache22/httpd.conf`

包含`freeBSD`系统`apache`配置文件查看`8080/tcp`相关配置

发现其仅允许`User-Agent`中包含`Mozilla/4.0`的浏览器访问

![](assets/images/2025-09-08-Kioptrix-2014-Walkthrough/df28053c-722e-490c-820b-7f0c34d17f75.png)

携带符合要求的`User-Agent`访问`8080`端口，目录遍历存在`phptax`路径

![](assets/images/2025-09-08-Kioptrix-2014-Walkthrough/ec5578cf-6547-4088-be65-ad583e799672.png)

使用`exploit/multi/http/phptax_exec`拿shell

![](assets/images/2025-09-08-Kioptrix-2014-Walkthrough/25029713-313b-41f1-b2a4-76ec28a558d8.png)

# shell as root by kernel privilege escalation

通过`searchsploit freebsd`能发现该机器内核存在提权脚本

![](assets/images/2025-09-08-Kioptrix-2014-Walkthrough/914ebf89-df88-42e1-98cc-b7ee685190a6.png)

这台机器没有`wget`和`curl`，使用`fetch`下载提权脚本，编译运行后得到root

![](assets/images/2025-09-08-Kioptrix-2014-Walkthrough/2dd7e79f-cf6e-46c2-a8a0-ed8ecf4c0df4.png)
