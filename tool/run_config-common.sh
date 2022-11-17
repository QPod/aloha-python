#! /bin/sh
set -ex

export TZ=${TZ:="Asia/Shanghai"}
ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ >/etc/timezone
echo "Setup timezone, current date: $(date)"

if [ -f /etc/apt/sources.list ]; then
  echo "Found Ubuntu system, setting ubuntu mirror"
  # sed -i 's/mirrors.*.com/mirrors.*.com.cn/' /etc/apt/sources.list
  # sed -i 's/archive.ubuntu.com/mirrors.*.com.cn/' /etc/apt/sources.list
  # sed -i 's/security.ubuntu.com/mirrors.*.com.cn/' /etc/apt/sources.list
fi

if [ -f /etc/yum.repos.d/CentOS-Base.repo ]; then
  echo "Found CentOS system, setting CentOS mirror"
  # sed -i 's/mirror.centos.org/mirrors.*.com.cn/' /etc/yum.repos.d/CentOS-Base.repo
  # sed -i 's/mirrorlist=/#mirrorlist=/' /etc/yum.repos.d/CentOS-Base.repo
  # sed -i 's/#baseurl/baseurl/' /etc/yum.repos.d/CentOS-Base.repo
fi

if [ -f "$(which python)" ]; then
  echo "Found python, setting pypi source in /etc/pip.conf"
  cat >/etc/pip.conf <<EOF
[global]
progress_bar=off
root-user-action=ignore
retries=5
timeout=180
trusted-host=pypi.python.org pypi.org files.pythonhosted.org
EOF
fi

if [ -f "$(which npm)" ]; then
  echo "Found npm, setting npm mirror"
  npm config set registry https://registry.npmjs.org
fi

groupadd -g 10001 readonly && useradd readonly -u 10001 -g 10001 -m -s /bin/bash

# restrict the user to su by updating login policy:
# Step 1. Disallow su to root for non-wheel user, by adding the config: `auth sufficient pam_wheel.so trust use_uid`
# sed -E -i '/^#auth\s+sufficient\s+pam_wheel.so\s+trust\s+use_uid/s/#//' /etc/pam.d/su
# Step 2. Set the following to yes, then the user must be listed as a member of the first gid 0 group in /etc/group (called root on most Linux systems) to be able to su to uid 0 accounts.
# If the group doesn't exist or is empty, no one will be able to su to uid 0.
# echo "SU_WHEEL_ONLY yes" >>/etc/login.defs
