# Recon

这台机器只开放了ssh和web

![](assets/images/2025-08-27-Broken-Gallery-Walkthrough/98742d4b-8014-427c-b68b-882d745fcb8d.png)

网页前端是一个目录遍历

![](assets/images/2025-08-27-Broken-Gallery-Walkthrough/78c690db-1799-42e6-9c09-961669b92a83.png)

`README.md`是一些16进制，需要解码

![](assets/images/2025-08-27-Broken-Gallery-Walkthrough/74871ca0-4be7-4404-a388-bacd451ef9ad.png)

解码后似乎也不是什么有效数据

…

省略很多没有成果的步骤

…

# shell as broken by ssh brute

经过一番爆破得到`broken:broken`

![](assets/images/2025-08-27-Broken-Gallery-Walkthrough/c3302fd4-8296-454f-a775-8d45408aaf29.png)

# shell as root by sudo

例行检查，发现可以免密使用`sudo timedatectl`，这是一个`pager`命令，那么老样子提权就好了

![](assets/images/2025-08-27-Broken-Gallery-Walkthrough/0eb6eee6-9fb5-44fe-9e48-64283c6b4e59.png)