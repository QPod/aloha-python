ARG BASE_NAMESPACE="docker.io"
ARG BASE_IMG="qpod/base:latest"
ARG DIR_APP="/root/app"
ARG MIRROR_PROFILE="common"

# Stage 1: compile the code
FROM ${BASE_NAMESPACE:+$BASE_NAMESPACE/}${BASE_IMG} AS builder
# To build python source code as binary .so files or not
ARG ENABLE_CODE_BUILD="true"

ARG DIR_APP
ARG MIRROR_PROFILE

COPY . /tmp/app
RUN set -ex && cd /tmp/app && mkdir -pv ${DIR_APP} \
 && sh ./tool/run_config-${MIRROR_PROFILE}.sh \
 && if [[ "$ENABLE_CODE_BUILD" = "true" ]] ; then \
      echo "-> Building src to binary..." && pip install -U aloha[build] && \
      aloha compile --base=./src --dist=${DIR_APP}/ ; \
    else \
      echo "-> Not building src code!" && mv src/* ${DIR_APP} ; \
    fi \
 && mv ./tool/run_config-${MIRROR_PROFILE}.sh ${DIR_APP}/run_config.sh && ls -al ${DIR_APP} ./*


# Stage 2: copy the built code and install packages
FROM ${BASE_NAMESPACE:+$BASE_NAMESPACE/}${BASE_IMG}
LABEL maintainer=haobibo@gmail.com
ARG DIR_APP
ARG PORT_SVC

USER root
WORKDIR ${DIR_APP}
COPY --from=builder ${DIR_APP} ${DIR_APP}/

ENV PORT_SVC=${PORT_SVC:-80} \
    ENTRYPOINT="app_common.debug"

RUN set -ex && pwd && ls -al && sh ./run_config.sh \
 && pip install -U --no-cache-dir pip \
 && ( [ -f ./requirements.txt ] && pip install -U --no-cache-dir -r ./requirements.txt || true ) && pip list  \
 && rm -rf ~/.cache && ls -al && printenv | sort

VOLUME ${DIR_APP}/logs
EXPOSE ${PORT_SVC}
HEALTHCHECK --interval=30s --timeout=5s CMD curl -fs "http://localhost:${PORT_SVC}/api/common/sys_info/mem" || exit 1
CMD ["aloha start"]
