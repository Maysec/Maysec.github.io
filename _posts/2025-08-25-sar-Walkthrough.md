# Recon

![](assets/images/2025-08-25-sar-Walkthrough/c817c8e1-e762-4965-bfd7-14311a5eca33.png)

机器只开放了一个web服务，有一些关键路径

![](assets/images/2025-08-25-sar-Walkthrough/4851d378-a343-443a-a5d1-f0f7c9cd7fdf.png)

`robots.txt`返回`sar2HTML`，访问后页面如下

![](assets/images/2025-08-25-sar-Walkthrough/298ab494-b636-45ca-bc32-7f47b73d52b7.png)

# shell as www-data by sar2HTMl

sar2html存在RCE漏洞

```php
http://192.168.1.63/sar2HTML/index.php?plot=;<command here>
```

通过python反弹shell，跑一下`linpeas`,没发现什么重要线索

![](assets/images/2025-08-25-sar-Walkthrough/022ed94e-7917-4204-9065-0f8323a59dc0.png)

进行一轮基本信息收集，发现存在有效普通用户`love`

![](assets/images/2025-08-25-sar-Walkthrough/76b62d2e-fc7e-49e1-9cf6-101a07e51572.png)

# shell as root by crontab

发现存在以`root`身份运行的计划任务，并且目标shell脚本可写

![](assets/images/2025-08-25-sar-Walkthrough/2c68f816-a26a-4be6-aefc-248670299d21.png)

上传`php-reverse-shell.php`，编辑`write.sh`

![](assets/images/2025-08-25-sar-Walkthrough/5e51e6e9-e5da-481e-a0d2-447c887a39d6.png)

# Some thinking

> 为什么使用php-reverse-shell.php来反弹shell？

* 在使用它之间，尝试过使用`bash -i`反弹，也试过`python`反弹，发现都不成功
    
* 这是由于这个命令注入点使用的是`php exec`，它会识别所有shell元字符（`<`、`>`、`|`、`&`、`;`、`$`）
    
* 基于以上，`bash`和`python`的方案都包含了相关shell元字符，只有最后使用的方案是不包含的