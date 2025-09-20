> 这台机器使用静态地址`10.10.10.10`，需要保证攻击机使用同网段地址
> 
> 其次在导入机器后启动可能发生“当前硬件版本不支持设备sata。”报错
> 
> 需要右击虚拟机选择“更改硬件兼容性”，将版本设置到vmware workstation 16.\*即可解决

# Recon

机器开放了`web`、`nfs`，其中包括`https`

![](../assets/images/2025-08-30-dpwwn-2-Walkthrough/98a36441-d085-499f-b1a3-62c3c11554cd.png)

## nfs

`nfs`目录下没有任何文件，有`write`权限，后面再考虑

![](../assets/images/2025-08-30-dpwwn-2-Walkthrough/9d46cc20-c3d8-44db-9a0f-1d2dac80bbf9.png)

## web

目录扫描发现这是一个`wordpress`

![](../assets/images/2025-08-30-dpwwn-2-Walkthrough/b57ecd96-699c-41ef-8a7d-e89bd49b3aaf.png)

`wpscan`枚举得到`admin`用户，爆破无果

![](../assets/images/2025-08-30-dpwwn-2-Walkthrough/74b9750b-50ac-43ee-96c6-1c2936e9ac47.png)

# shell as www-data by wp-plugins

使用`wpscan --url http://10.10.10.10/wordpress -e p`枚举插件，发现`site-editor`

![](../assets/images/2025-08-30-dpwwn-2-Walkthrough/a8bdc095-29bf-4757-9f22-dce6b0694e18.png)

使用`searchsploit`找找有没有漏洞，发现一个文件包含漏洞

![](../assets/images/2025-08-30-dpwwn-2-Walkthrough/4aefd659-26ee-47d2-acde-a1161209e63d.png)

验证一下`poc`，漏洞存在

![](../assets/images/2025-08-30-dpwwn-2-Walkthrough/082ffafe-928a-488a-bb80-6df0efa64868.png)

![](../assets/images/2025-08-30-dpwwn-2-Walkthrough/7bba07cc-393f-4ef3-b0e2-65a902edcbef.png)

通过nfs向`/home/dpwwn02`目录写入`php-reverse-shell.php`，文件包含后反弹`shell`

![](../assets/images/2025-08-30-dpwwn-2-Walkthrough/e6302566-c81b-4776-adb7-d71ab3a2471b.png)

# shell as root by suid

例行检查，发现`find`命令存在`suid`，直接`exec`提权

![](../assets/images/2025-08-30-dpwwn-2-Walkthrough/e13072b3-99ee-4430-90d3-35954d95ac96.png)
