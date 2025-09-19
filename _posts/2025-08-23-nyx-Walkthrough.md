# Recon

只有ssh和http，那就从web入手

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1756051757426/626b2c5f-5a2e-4f85-980d-6ccdc285bf86.png align="center")

主页只有一个logo，源代码注释中的话暂时没明白是何用意

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1756051801738/6b525ab2-7815-43f2-a348-564d1a5e1ee3.png align="center")

```xml
<!-- Dont waste your time looking into source codes/robots.txt etc , focus on real stuff -->
```

目录扫描发现`key.php`

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1756052090342/70c3ec90-c751-44e1-98ef-8a9326bfd207.png align="center")

`rockyou.txt`爆破无果

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1756052183800/98b27dcc-3fe4-4a26-a220-8e54474fba68.png align="center")

# amazing nmap script！

爆破无果、注入无果、弱口令无果、目录扫描无果…

似乎常规手段都没能获取到更多信息，<s>最后看一遍wp</s>

发现有师傅使用`nmap —script=http-enum`脚本扫描得到了一个比较有意思的路径

通过`proxychins4`代理`nmap`流量，感叹了`nmap`的并发能力

但整体扫描过程并没有预期外的流量，并且`/d41d8cd98f00b204e9800998ecf8427e.php`路径是突然冒出来的，路径来源问题暂时放一放，先把机器打完

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1756052416361/ca7e2d36-dae5-4859-8be3-3312fdac8e65.png align="center")

# shell as mpampis by d41d8cd98f00b204e9800998ecf8427e

尝试访问`d41d8cd98f00b204e9800998ecf8427e.php`，发现返回了一个私钥，网页`title`提示这个私钥属于`mpampis`用户

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1756052637808/9484b7cb-eb2a-4bb3-a4e7-91521111bef0.png align="center")

保存私钥，将文件权限降低尝试登录（ssh不允许在私钥文件权限过于宽松的情况下登录）

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1756052849052/1b2e6791-ed6a-4b21-80fb-beb4c0e1f12f.png align="center")

# shell as root by gcc privileges

手动收集一些环境信息，发现可以`sudo`免密使用`gcc`，那么直接`gcc`提权即可

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1756092664823/0ffbff04-3d3a-43bb-9e98-f35377fe9eee.png align="center")

# Some thinking

> d41d8cd98f00b204e9800998ecf8427e是什么？

* 是`md5`加密空字符的结果
    
* `md5`是一种确定性加密算法，对于任何长度的输入都将得到相同长度的输出，空字符也不例外
    

当开发者认为空字符的`md5`值也为空时，可能引发一些逻辑漏洞