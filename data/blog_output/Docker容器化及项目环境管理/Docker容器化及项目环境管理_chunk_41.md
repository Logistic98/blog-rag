## 3. Docker环境搭建及使用
### 3.7 正式环境的前后端分离项目部署
#### 3.7.2 项目打包并准备项目配置

将Springboot项目打成jar包，Vue项目打成dist包。除此之外，需要修改Springboot项目的配置文件（把项目依赖的MySQL、Redis、 Elasticsearch、Emqx环境地址由原来的ip:port改成 docker 的 hostname），这里采用包外配置。

前端项目打包（以 Angular 为例）

```shell
$ npm install -g @angular/cli   
$ npm install   
$ ng build --base-href ./  
```

后端项目打包（以Springboot为例）

```shell
$ mvn clean
$ mvn install
$ mvn package
```
