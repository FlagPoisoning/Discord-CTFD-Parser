FROM debian:bullseye

ENV ZIPFILE discord.zip
ENV DOMAIN bot

ENV HTTP_PORT 80
ENV HTTPS_PORT 443
ENV SSH_PORT 22
ENV DISCORD_TOKEN PUT-YOUR-DISCORD-BOT-TOKEN-HERE

ENV DEBIAN_FRONTEND=noninteractive
#======================================================

ENV DOCUMENT_ROOT /var/www/${DOMAIN}

ENV DEBIAN_FRONTEND=noninteractive

COPY ${ZIPFILE} ${DOCUMENT_ROOT}/${ZIPFILE}
COPY install.sh ${DOCUMENT_ROOT}/install.sh

RUN \
    chmod +x ${DOCUMENT_ROOT}/install.sh;


VOLUME ${DOCUMENT_ROOT}
WORKDIR ${DOCUMENT_ROOT}

EXPOSE ${HTTP_PORT}
EXPOSE ${HTTPS_PORT}
EXPOSE ${SSH_PORT}

CMD ["sleep", "infinity"]