## 2. Nginx配置及项目发布
### 2.1 正向代理与反向代理
#### 2.2.2 反向代理概述

与代表客户端的正向代理不同，反向代理服务器位于后端服务器之前，将客户端请求转发至这些服务器。反向代理通常用于提高防护、速度和可靠度。反向代理从客户端获取请求，将请求传递到其他服务器，然后将其转发回相关客户端，使它看起来像是初始代理服务器在处理请求。这类代理可以确保用户不会直接访问原始服务器，因此可为这类网页服务器提供匿名性。

尽管对普通消费者和普通人不会特别有用，但反向代理服务器非常适合服务提供商和每天访问量大的网站。这些代理可以保护网页服务器，增强网站性能并帮助避免过载。反向代理也可用于负载平衡、缓存和 SSL 加密。

网站和服务提供商可能出于各种原因使用反向代理，部分用途如下：

- 负载均衡。高流量的网站有时可能需要反向代理服务器来处理传入流量。一个热门站点不会自行处理流量，而可能在多个后端服务器之间分配流量，从而提高容量以处理大量请求。如果其中一台服务器过载并出现故障，可以将流量重定向至其它在线服务器，以确保网页正常运行。网站工程师甚至可以添加更多后端服务器到此负载均衡器，以增加容量，满足不断提高的性能要求。
- 缓存。反向代理可以缓存经常请求的数据。需要存储大量图片和视频的企业也可以通过缓存这些内容，降低网站服务器的负载来提高网站性能。 
- 匿名信和安全性。由于反向代理拦截所有传入请求，它们会为后端服务器带来更高层级的保护。它可以阻止来自特定 IP 地址的可疑流量，从而有助于防止恶意访问者滥用网页服务器。
