## 3. Docker环境搭建及使用
### 3.7 正式环境的前后端分离项目部署

正式环境使用Docker Network对Docker容器进行统一管理，像数据库这种提供服务的，可不对外提供端口，各容器之间通过hostname进行内部通信。

下面以一个Springboot + Vue的前后端分离项目（项目依赖于MySQL、Redis、 Elasticsearch、Emqx）为例。
