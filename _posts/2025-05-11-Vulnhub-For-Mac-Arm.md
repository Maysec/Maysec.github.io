本篇文章讨论如何在arm架构u下打vulnhub靶机，笔者硬件为Mac M1

## Prepare

vulnhub提供的靶机几乎都是vmdk格式供Vmware Workstation使用，而Vmware Workstation仅支持Intel cpu

虽然Mac Arm也可以使用Vmware fusion，但总归无法运行x86-64的虚拟机，那么思路就只有模拟了

所需要使用到的工具：

- UTM 一款基于QEMU虚拟化技术封装的虚拟机工具

  https://github.com/utmapp/UTM/releases/tag/v4.6.5

- qemu

  ```shell
  brew install qemu
  ```

## Vulnhub

Vulnhub提供的靶机似乎并没有统一的格式要求，可能是ova、ovf、vmdk甚至qcow2，但前三者底层上都是vmdk这种虚拟磁盘格式

以靶机`FourAndSix2`为例，从官方下载后得到`FourAndSix2.ova`，直接对其进行解压，得到`FourAndSix2-disk001.vmdk`

![image-20250510220841529](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510220841529.png)

## qemu-img

`qemu-img`是qemu套件提供的命令行工具，可以通过其完成`vmdk`、`qcow2`、`raw`等格式的相互转换

此处讨论情况最多的当Vulnhub提供的格式能够提取出vmdk后如何完成格式转换

```shell
qemu-img convert -p -O qcow2 FourAndSix2-disk001.vmdk FourAndSix2-disk001.qcow2
```

运行后得到FourAndSix2-disk001.qcow2后通过UTM进行模拟

![image-20250510221125054](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510221125054.png)

## UTM

新建虚拟机，选择模拟 -> 其他

<img src="https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510221319091.png" alt="image-20250510221319091" style="zoom:33%;" />

<img src="https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510221358534.png" alt="image-20250510221358534" style="zoom:33%;" />

启动设备选择无

<img src="https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510221418435.png" alt="image-20250510221418435" style="zoom:33%;" />

硬件架构选择x86_64

<img src="https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510221440969.png" alt="image-20250510221440969" style="zoom:33%;" />

存储空间无所谓，反正会删掉这块磁盘

<img src="https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510221511844.png" alt="image-20250510221511844" style="zoom:33%;" />

后面都跟着默认配置下一步就行

接下来进入虚拟机设置，删除新建虚拟机时添加的IDE驱动器

![image-20250510221631312](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510221631312.png)

导入刚刚转换得到的qcow2磁盘

![image-20250510221736606](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510221736606.png)

取消勾选QEMU中的UEFI启动

![image-20250510221828173](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510221828173.png)

最后点击存储，然后启动虚拟机

## Network

UTM虚拟机默认使用“共享模式”与物理机共享网络，使用到的物理网卡是`bridge100`，vulnhub的大部分靶机网卡都会使用dhcp，在这种情况下，可以在靶机启动后通过扫描`192.168.64.1/24`这个C端找到靶机的IP地址![image-20250510223711841](https://mayss.oss-cn-beijing.aliyuncs.com/image/image-20250510223711841.png)

```shell
fping -agq 192.168.64.0/24
192.168.64.1
192.168.64.8
```

