FROM python:3.11

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get install -y wget \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \ 
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get -y install google-chrome-stable

WORKDIR /flip_catalog_parser

COPY requirements.txt .
RUN --mount=type=cache,mode=0755,target=/root/.cache pip install --upgrade pip && pip install -r requirements.txt

COPY . .