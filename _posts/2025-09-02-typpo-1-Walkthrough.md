# Recon

这台机器开放了标准端口的`ssh`、`http`和`nfs`

![](../assets/images/2025-09-02-typpo-1-Walkthrough/b3417c0f-3be6-429a-b149-19be579d1a85.png)

测试优先级放在第一位的`nfs`似乎无法连接，无论是`showmount -d`的检测还是`nmap`相关`script`都没有结果

`feroxubuster`扫描得到了一些可能存在攻击向量的路径

![](../assets/images/2025-09-02-typpo-1-Walkthrough/bedeb640-b8e6-4711-8f39-864a5e621aae.png)

网页前端显示这是一个博客

![](../assets/images/2025-09-02-typpo-1-Walkthrough/f38b5474-cdcc-4583-8719-46e8d7905f7b.png)

`admin/notes.txt`中泄露了一个密码`12345ted123`，而`/admin/`目录本身是一个`index of`

![](../assets/images/2025-09-02-typpo-1-Walkthrough/bca01d00-0b06-4950-a2f9-e7c8a29bc57c.png)

# shell as ted by leak password

各种交互点都尝试了一番没有收获，回过头看泄露的密码，尝试`ted:12345ted123`登录ssh

![](../assets/images/2025-09-02-typpo-1-Walkthrough/7996d7dc-40cb-4470-abff-96f2ba046c31.png)

# shell as root by suid

嗯…极boring的一台机器

![](../assets/images/2025-09-02-typpo-1-Walkthrough/cbc1941f-d0f5-4eba-805c-ce2134996897.png)
