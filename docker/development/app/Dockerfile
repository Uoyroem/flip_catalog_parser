FROM python:3.11

ENV DEBIAN_FRONTEND noninteractive
ENV DISPLAY :1
ENV SCREEN_GEOMETRY="1280x720x24"

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache \
    && apt-get update \
    && apt-get install -y --no-install-recommends wget curl xvfb fluxbox x11vnc \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \ 
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get -y install google-chrome-stable 

WORKDIR /flip_catalog_parser

COPY requirements.txt .
RUN --mount=type=cache,mode=0755,target=/root/.cache pip install --upgrade pip && pip install -r requirements.txt

COPY . .