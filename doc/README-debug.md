# 开发调试文档

## 开发环境基于源代码调试

```bash
# Firstly, cd to the project root folder (which includes `src`) of the project, and then:  
docker run -it \
  -v $(pwd):/root/app/ \
  -w /root/app/src \
  --name="app-$(whoami)" \
  -p 80:80 \
  docker.io/qpod/base:latest bash
  
python -m aloha.script.start app_common.debug
```
