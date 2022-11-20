# Introduction

Aloha! Thanks for your interesting in this python package.

[![License](https://img.shields.io/github/license/QPod/aloha)](https://github.com/QPod/aloha/blob/main/LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/QPod/aloha/build)](https://github.com/QPod/aloha/actions)
[![Join the Gitter Chat](https://img.shields.io/gitter/room/nwjs/nw.js.svg)](https://gitter.im/QPod/)
[![PyPI version](https://img.shields.io/pypi/v/aloha)](https://pypi.python.org/pypi/aloha/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/aloha)](https://pepy.tech/badge/aloha/)
[![Code Activity](https://img.shields.io/github/commit-activity/m/QPod/aloha)](https://github.com/QPod/aloha/pulse)
[![Recent Code Update](https://img.shields.io/github/last-commit/QPod/docker-images.svg)](https://github.com/QPod/aloha/stargazers)

Please generously STAR★ our project or donate to us!  [![GitHub Starts](https://img.shields.io/github/stars/QPod/aloha.svg?label=Stars&style=social)](https://github.com/QPod/aloha/stargazers)
[![Donate-PayPal](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://paypal.me/haobibo)
[![Donate-AliPay](https://img.shields.io/badge/Donate-Alipay-blue.svg)](https://raw.githubusercontent.com/wiki/haobibo/resources/img/Donate-AliPay.png)
[![Donate-WeChat](https://img.shields.io/badge/Donate-WeChat-green.svg)](https://raw.githubusercontent.com/wiki/haobibo/resources/img/Donate-WeChat.png)

## What is it?
The python package `aloha` is a cute and versatile to build python microservices.
The package encapsulates commonly used components and features, such as:


=== "English"
    - Rapidly create RESTful APIs and start services
    - Logging utils
    - Manage different environments,configuration files, and resource files
    - Connect to popular databases
    - Detect and monitor application runtime environment

=== "中文"
    `aloha`是一个用来快速构建微服务的Python包，它包含了创建微服务常用的组件和功能：

    - 快速创建微服务的RESTful API并启动服务
    - 环境管理、配置文件管理、资源文件管理；
    - 日志组件
    - 连接数据库
    - 对运行环境进行监测；

## Installation

``` title="It's easy to install aloha using the following command"
pip install aloha[all]
```

Notice the `[all]` after the package is a set of (one or more) extra requirements, which enables additional features.

=== "English"
    These extra requirements can include:

    - `all`: everything below are included.
    - `service`: components/packages used to build RESTful APIs -- aloha use tornado to support services.
    - `build`: used to build python code into binary files, which is particularly useful to protect source code.
    - `db`: connect to popular databases, like MySQL / PostgreSQL / Redis.
    - `stream`: processing steram data using confluent_kafka. 
    - `data`: processing data or doing data science tasks using packages like pandas.
    - `report`: utilites to export data and report to Excel files.
    - `test`: unit test utilites.
    - `docs`: utilites used to build documentations.



=== "中文"
    请留意，上述安装命令中包名后的`[all]`是额外的安装依赖，这些额外的安装内容在使用某些模块的时候会用到。 
 
    - `all`: 包含了下面的所有的依赖包
    - `service`: 用于创建RESTful APIs的依赖，aloha基于torndao来构建服务；
    - `build`: 用于将Python代码编译为二进制包或类库，这对于需要进行源代码保护的场景十分有用；
    - `db`: 连接到常用的数据库，如MySQL、PostgreSQL、Redis等；
    - `stream`: 基于confluent_kafka进行流数据处理； 
    - `data`: 使用pandas等package进行数据处理；
    - `report`: 将数据导出为Excel格式的报告；
    - `test`: 进行单元测试的功能；
    - `docs`: 用于进行文档构建的功能模块。
