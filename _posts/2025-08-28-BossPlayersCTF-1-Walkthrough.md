# Recon

机器仅开放`ssh`和`web`

![](../assets/images/2025-08-28-BossPlayersCTF-1-Walkthrough/0ecdfa64-81a3-4395-9d91-48b7b634ff72.png)

# shell as www-data by rce

网页前端有一些信息

![](../assets/images/2025-08-28-BossPlayersCTF-1-Walkthrough/9e91c512-5be0-4af2-890d-ce7f187a1778.png)

在渲染后的源代码中发现一串字符，看起来像`base64`

![](../assets/images/2025-08-28-BossPlayersCTF-1-Walkthrough/23ee5f23-c75b-4491-aa37-0fb938f2b6b3.png)

存在多层`base64`，解码3次后得到`workinginprogress.php`

![](../assets/images/2025-08-28-BossPlayersCTF-1-Walkthrough/38f762dc-42b7-4397-b39d-7d95162bb55b.png)

页面只有一些状态信息，其中`Test ping command`隐含了命令执行漏洞，通过`fuzz`参数得到`cmd`

![](../assets/images/2025-08-28-BossPlayersCTF-1-Walkthrough/e8ca9eb7-e868-40c3-94b6-c632c4ffba01.png)

通过`python`反弹shell

![](../assets/images/2025-08-28-BossPlayersCTF-1-Walkthrough/5ebfb10a-2f39-4930-94ff-09d397fcd7bc.png)

# shell as root by suid

例行检查发现`find`存在`suid`，直接提权即可

![](../assets/images/2025-08-28-BossPlayersCTF-1-Walkthrough/0156f051-eb9c-46de-a10e-d4b605a1dfd1.png)
