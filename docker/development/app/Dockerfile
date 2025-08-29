FROM python:3.11

ENV DEBIAN_FRONTEND noninteractive
ENV DISPLAY :1
ENV SCREEN_GEOMETRY="1280x720x24"

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update && \
    apt install -y --no-install-recommends gnupg curl wget tigervnc-standalone-server tigervnc-common && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt update && \
    apt install -y --no-install-recommends google-chrome-stable \ 
    tigervnc-standalone-server \
    xfce4 \
    xfce4-goodies \
    dbus-x11 \
    sudo && \
    useradd -m -s /bin/bash dev && \
    adduser dev sudo && \
    echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER dev

RUN mkdir -p /home/dev/.vnc /home/dev/.config/tigervnc && \
    echo "#!/bin/bash\n\
xrdb \$HOME/.Xresources\n\
startxfce4 &\n" > /home/dev/.vnc/xstartup && \
    chmod +x /home/dev/.vnc/xstartup

WORKDIR /flip_catalog_parser

COPY requirements.txt .
RUN --mount=type=cache,mode=0755,target=/root/.cache pip install --upgrade pip && pip install -r requirements.txt

COPY . .