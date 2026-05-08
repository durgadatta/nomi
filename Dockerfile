#TODO: update to 3.14 or the later images 

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NOMI_PROJECT_ROOT=/workspace \
    NOMI_JUPYTER_HOST=0.0.0.0 \
    NOMI_JUPYTER_PORT=8888 \
    NOMI_JUPYTER_TOKEN=nomi

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

COPY . /workspace

RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install -e ".[jupyter]" \
    && useradd --create-home --uid 1000 nomi \
    && chown -R nomi:nomi /workspace

ENV HOME=/home/nomi

USER nomi

RUN python -m tools.jupyter.install_nomi_kernel --user

EXPOSE 8888

ENTRYPOINT ["tini", "--", "python", "-m", "tools.docker.serve_nomi_notebook"]
