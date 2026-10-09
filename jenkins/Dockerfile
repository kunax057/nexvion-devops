
FROM jenkins/jenkins:lts-jdk21

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates curl gnupg python3 python3-apt \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg \
       -o /etc/apt/keyrings/docker.asc \
    && chmod a+r /etc/apt/keyrings/docker.asc \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
       > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli ansible \
    && curl -fsSL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh \
       -o /tmp/install-trivy.sh \
    && sh /tmp/install-trivy.sh -b /usr/local/bin \
    && docker --version \
    && ansible-playbook --version \
    && trivy --version \
    && rm -f /tmp/install-trivy.sh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER jenkins
