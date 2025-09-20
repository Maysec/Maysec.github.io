# Recon

这台机器开放了标准端口的`web`和`ssh`

![](assets/images/2025-09-07-hackme-1-Walkthrough/f273d744-a7d9-4d63-9505-17bddca368f4.png)

# shell as www-data by file-uploads

网页前端是一个登录页面，存在注册点

![](assets/images/2025-09-07-hackme-1-Walkthrough/40e34e79-6056-4f9d-971c-793cdabd89c6.png)

注册一个用户登陆后是一个查询页面，这个页面存在注入

注入得到`superadmin`用户`hash`，通过`hashes.com`得到`Uncrackable`

![](assets/images/2025-09-07-hackme-1-Walkthrough/a6861589-4310-4f09-9786-f51a2889a29b.png)

使用`superadmin`用户登录得到一个上传点，这个上传点没有任何过滤，直接上传`php-reverse-shell`即可

![](assets/images/2025-09-07-hackme-1-Walkthrough/8166c64c-b82b-4944-9f31-0bb6fda309d0.png)

![](assets/images/2025-09-07-hackme-1-Walkthrough/741c3d66-53ea-4c64-874f-20ae6f8d832b.png)

# shell as root by suid

例行检查，发现`/home/legacy`目录下存在具有`suid`权限的`touchmenot`文件，执行直接获取root

![](assets/images/2025-09-07-hackme-1-Walkthrough/b7da2085-3715-42fd-99cd-1da2e750f0fb.png)
