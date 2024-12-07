## 4. 搭建Harbor私有Docker镜像仓库
### 4.1 镜像仓库及Harbor概述
#### 4.1.2 Harbor基本介绍

**[1] Harbor发展历史**

Harbor Registry 由 VMware 公司中国研发中心云原生实验室原创，并于 2016 年 3 月开源。Harbor 在 Docker Distribution的基础上增加了企业用户必需的权限控制、镜像签名、安全漏洞扫描和远程复制等重要功能，还提供了图形管理界面及面向国内用户的中文支持，开源后迅速在中国开发者和用户社区流行，成为中国云原生用户的主流容器镜像仓库。

2018年7月，VMware 捐赠 Harbor 给 CNCF，使Harbor成为社区共同维护的开源项目，也是首个源自中国的 CNCF 项目。在加入 CNCF 之后，Harbor 融合到全球的云原生社区中，众多的合作伙伴、用户和开发者都参与了Harbor项目的贡献，数以千计的用户在生产系统中部署和使用 Harbor，Harbor 每个月的下载量超过3万次。2020 年 6 月，Harbor 成为首个中国原创的 CNCF 毕业项目。

**[2] Harbor是什么**

Harbor是一个用于存储和分发Docker镜像的企业级Registry服务器，虽然Docker官方也提供了公共的镜像仓库，但是从安全和效率等方面考虑，部署企业内部的私有环境Registry是非常必要的，Harbor和docker中央仓库的关系，就类似于nexus和Maven中央仓库的关系，Harbor除了存储和分发镜像外还具有用户管理，项目管理，配置管理和日志查询，高可用部署等主要功能。

项目地址：[https://github.com/goharbor/harbor/](https://github.com/goharbor/harbor/)
