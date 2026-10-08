FROM mcr.microsoft.com/devcontainers/base:ubuntu26.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y \
        dbus-x11 \
        libkf5service-data \
        lxqt \
        novnc \
        websockify \
        x11-utils \
        x11vnc \
        xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
