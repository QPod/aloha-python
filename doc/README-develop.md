# Development Docs

## Live debug on source code using docker

```bash
# Firstly, cd to the project root folder (which includes `src`) of the project, and then:  
docker run -it \
  -v $(pwd):/root/app/ \
  -w /root/app/src \
  --name="app-$(whoami)" \
  -p 8080:80 \
  docker.io/qpod/base:latest bash
  
python -m aloha.script.start app_common.debug
```

## Build docker image

```bash
source tool/tool.sh
build_image app_common latest tool/app.Dockerfile
```

## Develop docs

```bash
mkdocs serve -f mkdocs.yml -a 0.0.0.0:80
```
