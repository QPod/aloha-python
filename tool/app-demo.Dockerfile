ARG BASE_NAMESPACE="quay.io"
ARG BASE_IMG="labnow/base:latest"
ARG DIR_APP="/root/app"

# this var PROFILE_LOCALIZE will be used in /opt/utils/script-localize.sh
ARG PROFILE_LOCALIZE="aliyun-pub"

# Stage 1: compile the code
FROM ${BASE_NAMESPACE:+$BASE_NAMESPACE/}${BASE_IMG} AS builder
# To build python source code as binary .so files or not
ARG ENABLE_CODE_BUILD="true"

ARG DIR_APP
ARG PROFILE_LOCALIZE


COPY . /tmp/app
RUN set -ex && cd /tmp/app && mkdir -pv ${DIR_APP} \
 && source /opt/utils/script-localize.sh ${PROFILE_LOCALIZE} \
 && if [[ "$ENABLE_CODE_BUILD" = "true" ]] ; then \
      echo "-> Building src to binary..." && pip install -U aloha[build] && \
      aloha compile --base=./src --dist=${DIR_APP}/ ; \
    else \
      echo "-> Not building src code!" && mv src/* ${DIR_APP} ; \
    fi \
 && ls -al ${DIR_APP} ./*


# Stage 2: copy the built code and install packages
FROM ${BASE_NAMESPACE:+$BASE_NAMESPACE/}${BASE_IMG}
LABEL maintainer=haobibo@labnow.ai
ARG DIR_APP
ARG PORT_SVC

USER root
WORKDIR ${DIR_APP}
COPY --from=builder ${DIR_APP} ${DIR_APP}/

ENV PORT_SVC=${PORT_SVC:-80} \
    ENTRYPOINT="app_common.debug"

RUN set -eux && pwd && ls -alh \
 && source /opt/utils/script-localize.sh ${PROFILE_LOCALIZE} \
 && pip install -U --no-cache-dir pip \
 && ( [ -f ./requirements.txt ] && pip install -U --no-cache-dir -r ./requirements.txt || true ) && pip list  \
 && rm -rf ~/.cache && ls -al && printenv | sort

VOLUME ${DIR_APP}/logs
EXPOSE ${PORT_SVC}
HEALTHCHECK --interval=30s --timeout=5s CMD curl -fs "http://localhost:${PORT_SVC}/api/common/sys_info/mem" || exit 1
CMD ["aloha start"]
