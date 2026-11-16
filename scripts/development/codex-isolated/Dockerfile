# CCPC ERPNext: dedicated clean Codex CLI image.
# No CCPC application checkout, DEV/PROD files, SSH material, API token or Docker socket
# is copied into this image. This Dockerfile is NOT the existing DEV container.
FROM node:24-bookworm-slim

RUN set -eux; \
    npm install --global --no-audit --no-fund @openai/codex@0.161.0; \
    npm cache clean --force; \
    groupadd --gid 14532 ccpcagent; \
    useradd --uid 14532 --gid 14532 --create-home --shell /usr/sbin/nologin ccpcagent; \
    mkdir -p /work /home/ccpcagent/.codex; \
    chown -R 14532:14532 /work /home/ccpcagent

USER 14532:14532
WORKDIR /work
ENV HOME=/home/ccpcagent
ENV CODEX_HOME=/home/ccpcagent/.codex
ENTRYPOINT ["/usr/local/bin/codex"]
CMD ["--version"]
