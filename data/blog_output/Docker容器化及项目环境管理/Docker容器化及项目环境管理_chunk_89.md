## 5. Docker搭建中间件服务
### 5.10 Docker-ElasticSearch环境搭建
#### 5.10.4 使用curl命令操作ES

**[1] 索引操作**

```shell
// 查询所有索引
$ curl -u 用户名:密码 http://ip:port/_cat/indices

// 删除索引（包含结构）
$ curl -u 用户名:密码 -XDELETE http://ip:port/索引名

// 清空索引（不包含结构，即删除所有文档）
$ curl -u 用户名:密码 -XPOST 'http://ip:port/索引名/_delete_by_query?refresh&slices=5&pretty' -H 'Content-Type: application/json' -d'{"query": {"match_all": {}}}'

// 创建索引
$ curl -u 用户名:密码 -XPUT 'http://ip:port/索引名' -H 'Content-Type: application/json' -d'
{
    "settings" : {
      "index" : {
        "number_of_shards" : "5",
        "number_of_replicas" : "1"
      }
    },
    "mappings" : {
        "properties" : {
          "post_date": {
               "type": "date"
          },
          "tags": {
               "type": "keyword"
          },
          "title" : {
               "type" : "text"
          }
        }
    }
}'

// 修改索引
$ curl -u 用户名:密码 -XPUT 'http://ip:port/索引名/_mapping' -H 'Content-Type: application/json' -d'
{
  "properties" : {
    "post_date": {
         "type": "date"
    },
    "tags_modify": {
         "type": "keyword"
    },
    "title" : {
         "type" : "text"
    },
    "content": {
         "type": "text"
    }
  }
}'

// 调整副本数量（分片数量不可调整，要修改就只能删除索引重建）
$ curl -u 用户名:密码 -XPUT 'ip:port/索引名/_settings' -H 'Content-Type: application/json' -d '
{
    "index": {
       "number_of_replicas": "0"
    }
}'

// 查看单个索引信息（可以查看到单个索引的数据量)
$ curl -u 用户名:密码 -XGET 'http://ip:port/_cat/indices/index_1?v'

health status index      uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   index_1    aado9-iGRFGN9twQb040ds   5   1   28800345            0        3gb          1.5gb

// 按照文档数量排序索引（可以查看到所有索引的数据量)
$ curl -u 用户名:密码 -XGET 'http://ip:port/_cat/indices?v&s=docs.count:desc'
```

注意事项：创建索引时，有的教程在“mappings”里嵌套了“_doc”，会报如下错误，这是因为版本 7.x 不再支持映射类型，将其删除即可。

```
{"error":{"root_cause":[{"type":"illegal_argument_exception","reason":"The mapping definition cannot be nested under a type [_doc] unless include_type_name is set to true."}],"type":"illegal_argument_exception","reason":"The mapping definition cannot be nested under a type [_doc] unless include_type_name is set to true."},"status":400}%
```

**[2] 文档操作**

```shell
// 根据_id查询文档
$ curl -u 用户名:密码 -XGET 'http://ip:port/索引名/_doc/1'

// 新增和修改文档
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XPOST 'http://ip:port/索引名/_doc/1' -d '
     {
        "msgId": "10010",
        "title": "test-title",
        "content": "test-content",
        "isDeleted": 0,
        "publishTime": "1586707200000",
        "insertTime": "1668212021000",
        "updateTime": "1678687631000"
    }'
         
// 根据_id删除文档
$ curl -u 用户名:密码 -XDELETE "http://ip:port/索引名/_doc/1"

// 查询所有数据
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"match_all":{}}}'

// 查询指定条数的数据
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"match_all":{}},"size":2}'

// 查询指定列数据
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"match_all":{}},"_source":["publishTime","updateTime"]}'

// 查询数据并排序
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"match_all":{}},"sort":{"_id":{"order":"desc"}}}'
 
// 匹配查询
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"match":{"title":"test"}}}'

// 精准查询
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"term":{"title.keyword":"test-title"}}}'

// 范围查询
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"range":{"msgId":{"gt":"1","lte":"20000"}}}}'
```
