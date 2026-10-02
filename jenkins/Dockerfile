FROM jenkins/jenkins:lts-jdk17

USER root

# Python para correr lint y tests dentro del pipeline
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Cliente de Docker (solo el comando "docker"; el motor es el de tu PC)
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker

# Permite a Git leer la carpeta del proyecto montada desde Windows
RUN git config --system --add safe.directory '*'
