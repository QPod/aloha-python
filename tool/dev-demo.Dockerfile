ARG BASE_NAMESPACE="quay.io"
ARG BASE_IMG="labnow/node:latest"

# this var PROFILE_LOCALIZE will be used in /opt/utils/script-localize.sh
ARG PROFILE_LOCALIZE="aliyun-pub"

FROM ${BASE_NAMESPACE:+$BASE_NAMESPACE/}${BASE_IMG} AS dev

ARG PROFILE_LOCALIZE

# COPY src/requirements.txt /tmp/

USER root
RUN set -eux && pwd && ls -alh \
 && source /opt/utils/script-localize.sh ${PROFILE_LOCALIZE} \
 # ----------- handle frontend matters -----------
 && npm install -g pnpm \
 # ----------- handle backend matters ------------
 && pip install -U --no-cache-dir pip jupyterlab \
 # && pip install -U --no-cache-dir -r /tmp/requirements.txt \
 # ----------- install db client to connect db via terminal ------------
 && source /opt/utils/script-setup-db-clients.sh && setup_postgresql_client 17 \
 # ----------- clean up -----------
 && source /opt/utils/script-setup.sh && list_installed_packages && install__clean
