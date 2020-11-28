CRM_API框架基于SANIC, 实现了与CRM_WEB后端框架一致的用户验证以及单据序列处理。

## 框架使用
1. Python版本： 3.6以上, 议使用3.8; 操作系统： Ubuntu Server 18.04
2. `pip install -r requirements.txt`
2. 配置数据连接系统： config/settings 填写CRM_WEB后端数据库连接信息
2. `python main.y` 运行项目

## 系统部署
两种方式：系统服务或者基于Docker的部署

### 系统服务
1. 进入 install 目录， 运行 `sudo./install.sh`
2. `sudo systemctl start kirin.service`

### 容器方式
1. 编译容器： `sudo docker build --rm -f "Dockerfile" -t crm_api:latest .`
2. 运行容器： `sudo docker run -p 8000:80 crm_api:latest `

## 容器管理

#### 登录阿里云docker registry

`docker login --username=xibaoit@91t.com registry.cn-shanghai.aliyuncs.com`

登录registry的用户名是您的阿里云，密码是您开通namespace时设置的密码

#### 从registry拉取镜像

`sudo docker pull registry.cn-shanghai.aliyuncs.com/91t/crm_api:[tag]`

其中[tag]请根据您的镜像版本信息进行填写。

#### 将镜像推送到registry

`docker login --username=xibaoit@91t.com registry.cn-shanghai.aliyuncs.com`

`sudo docker tag [ImageId] registry.cn-shanghai.aliyuncs.com/91t/crm_api:[tag]`



## 参考文档：

SANIC: https://sanic.readthedocs.io

SANIC_JWT: https://sanic-jwt.readthedocs.io

ASYNCPG: https://github.com/MagicStack/asyncpg

SANIC_OPENAPI: https://github.com/huge-success/sanic-openapi

AIOREDIS: https://github.com/aio-libs/aioredis

SANIC_CSRF: https://pypi.org/project/sanic_csrf

SANIC-CORS: https://github.com/ashleysommer/sanic-cors

aiocassandra: https://pypi.org/project/aiocassandra/

### 更多

https://sanic.readthedocs.io/en/latest/sanic/extensions.html