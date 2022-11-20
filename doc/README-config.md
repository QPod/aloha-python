# Configurations

## OS Environment variables

### `ENV_PROFILE`

*default Value*: None (not defined).

=== "English"
    Define the environment profile the current process is running in, such as `DEV | STG | PRD`.
    This is usually used to specify which config file to use as entrypoint configuration file from the `${DIR_CONFIG}` folder.
    If this env variable is defined, `aloha` will firstly find `main-${ENV_PROFILE}` as the entry configuration file (use `main.conf` otherwise).

=== "中文"
    指定环境类型(如 `DEV | STG | PRD`)，用于指定配置文件入口等、便于程序从配置中区分环境等。
    如果指定了该变量，`aloha`读取配置文件时，会首先从`${DIR_CONFIG}`中，寻找文件`main-${ENV_PROFILE}.conf`作为入口配置文件，如果没有指定则默认查找`main.conf`。

### `ENTRYPOINT`

*default Value*: None (not defined).

=== "English"
    Define the entrypoint **Python module** when using command script `aloha start` to start a service/process.
    It's same to use `aloha start ${ENTRYPOINT}` to start the process.

    The specified **Python module MUST** contain a function named `main()`.

=== "中文"
    指定服务启动的入口模块，效果相当于 `aloha start ${ENTRYPOINT}`。
    该模块下必须有一个`main()`函数作为服务的入口函数。

### `APP_MODULE`

*default Value*: `default`.

=== "English"
    Define the application module name, which will be set to config variable `APP_MODULE` and used as the prefix for LOG files.

=== "中文"
    模块名称，该变量会在记录日志时用到——作为日志文件名前缀，该变量也可以通过配置文件中的配置项`APP_MODUEL`进行设置.

### `DIR_LOG`

*default Value*: `logs`.

=== "English"
    Define where the log files should be stored.

=== "中文"
    用于配置日志文件所在的目录.

### `DIR_RESOURCE`

*default Value*: `resource` of the current working directory.

=== "English"
    Define the resource folder, which will be used as the root folder for `aloha.config.paths.get_resource_dir()` function.

=== "中文"
    资源文件所在的文件夹路径，该目录将会被函数`aloha.config.paths.get_resource_dir()`作为根目录，便于程序访问资源文件。

### `DIR_CONFIG`

*default Value*: `${DIR_RESOURCE}/config`.

=== "English"
    Define where to find configuration files.

=== "中文"
    查找配置文件所在的文件夹路径。

### `FILES_CONFIG`

*default Value*: `None` (not defined).

=== "English"
    Optional. Define a list of config files (separated by comma) that the package will use.

=== "中文"
    用半角逗号`,`分隔的配置文件的列表，如果该变量存在，则变量`ENV_PROFILE`不起作用。
