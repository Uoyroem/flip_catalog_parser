FROM python:3.11

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:0
ENV XFCE4_DISABLE_WAYLAND=1

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update && \
    apt install -y --no-install-recommends curl supervisor xfce4 xfce4-goodies x11vnc xvfb dbus-x11 sudo gpg && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt update && \
    apt install -y --no-install-recommends google-chrome-stable

RUN useradd -m -s /bin/bash dev && \
    echo "dev ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/dev && \
    chmod 0440 /etc/sudoers.d/dev

COPY docker/development/app/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /flip_catalog_parser
RUN chown dev:dev /flip_catalog_parser

COPY requirements.txt .
RUN --mount=type=cache,mode=0755,target=/root/.cache \
    pip install --upgrade pip && pip install -r requirements.txt

COPY . .
RUN chown -R dev:dev /flip_catalog_parser

USER dev

