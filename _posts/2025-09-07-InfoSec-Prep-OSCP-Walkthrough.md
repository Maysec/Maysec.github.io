# Recon

机器开放了标准端口的`ssh`、`web`和`mysql x`

![](../assets/images/2025-09-07-InfoSec-Prep-OSCP-Walkthrough/de0f4bf4-e33e-4181-999e-5d9b99208a75.png)

## Web

web是一个`wordpress`

![](../assets/images/2025-09-07-InfoSec-Prep-OSCP-Walkthrough/bb99cf07-5e29-44bf-b549-7fa0d98d08bc.png)

`wpscan -e u`用户枚举只得到`admin`

![](../assets/images/2025-09-07-InfoSec-Prep-OSCP-Walkthrough/e0d0c7d8-097b-4a6c-b2e4-a6aebe6d20ad.png)

# shell as oscp by id\_rsa

在`robots.txt`下发现`/secret.txt`，其中存放了`base64`内容，解码后发现是`ssh`私钥

通过对私钥主体解码得到用户名`oscp`

![](../assets/images/2025-09-07-InfoSec-Prep-OSCP-Walkthrough/90fe7261-2032-4995-bef2-7e362436f011.png)

# shell as root by suid

例行检查，发现`bash`具有`suid`,`/bin/bash -p`即可
