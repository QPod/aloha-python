# 配置项说明

## 系统环境变量

- `ENV_PROFILE` 指定环境类型(如 DEV | STG | PRD), 用于指定配置文件入口等，如果指定了该变量，入口配置文件将会被指定为`main-${ENV_PROFILE}.conf`.
- `ENTRYPOINT` 指定服务启动的入口模块,该模块下必须有一个`main`函数作为服务的入口函数.
- `APP_MODULE` 模块名称，该变量会在记录日志时用到——作为日志文件名前缀，默认为`default`, 该变量也可以通过配置文件中的配置项`APP_MODUEL`进行设置.
- `DIR_LOG` 用于配置日志文件所在的目录.
- `DIR_RESOURCE` 资源文件所在的文件夹路径.
- `DIR_CONFIG` 配置文件所在的文件夹路径，如果不设定，默认为`${DIR_RESOURCE}/config`.
- `FILES_CONFIG`: 用半角逗号`,`分隔的配置文件的列表，如果该变量存在，则变量`ENV_PROFILE`不起作用.
