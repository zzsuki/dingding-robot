# 用于推送alertmanager告警的钉钉机器人

## Prometheus告警配置

由于消息模板使用了prometheus中推送的内容，所以本项目和prometheus中的告警信息关联性较强，消息模板中的部分如下：

``` yaml
告警级别：{{ alert.labels.severity }}
告警类型：{{ alert.labels.alertname }}
故障主机：{{ alert.labels.instance }}
告警主题：{{ alert.annotations.summary }}
告警详情：{{ alert.annotations.description }}
告警时间：{{ alert.startsAt }}
```

可以看出其中用到了labels和annotations的信息，startsAt是prometheus中告警的开始时间，会自动添加; 其他信息要求prometheus中的告警配置中必须包含这些信息，否则会导致消息模板中的信息为空。以下是一则prometheus中的告警配置示例：

```yaml
groups:
- name: 主机告警规则
  rules:
  - alert: 实例存活告警     # 这个地方对应alertname字段
    expr: up{job="node-exporter"} == 0
    for: 3m
    labels:
      user: zzsuki          # 这个地方可以任意增加各种labels，给告警加上需要的标签
      severity: warning     # 这个地方对应labels.severity
    annotations:    # 对应上边主题和详情信息
      description: "实例{{ $labels.instance }} 中 {{ $labels.job }} 超过5min未上报数据, 通信可能发生异常"
      summary: "实例监控异常，目标服务器异常 (instance {{ $labels.instance }})"
```

## 使用

### 1. 配置钉钉机器人

这个在dingding中创建即可，网上教程也很多，项目需要的信息就是机器人创建时提供的secret和access_token，这两个信息需要在后续环境变量中配置（目前只支持环境变量配置，后续会支持cmd方式参数输入）

### 2. 配置环境变量

 - DINGDING_SECRET：钉钉机器人创建时提供的secret
 - DINGDING_TOKEN：钉钉机器人创建时提供的access_token

### 3. 构建容器

`docker build -t zzsuki/dingding-robot:latest .`

### 4. 启动

`docker run --name dingding-robot -e DINGDING_TOKEN=xxxxx -e DINGDING_SECRET=xxxxx -p 8000:8000 -d zzsuki/dingding-robot`


### 5. docker-compose example

```yaml
version: "3"
services:
  dingding-webhook:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: dingding-webhook
    env_file:
      - .env
    ports:
      - '8000:8000'
    restart: always
    network_mode: host
```