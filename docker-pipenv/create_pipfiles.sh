#!/bin/bash

IMAGE="python"
TAG="3.7.2"
CONTAINER="pipfile_container"

# コンテナを起動
docker container run --name "$CONTAINER" --workdir "/tmp" --rm -td "$IMAGE":"$TAG"

# コンテナでPipfile.lock更新
docker container exec "$CONTAINER" pip install -U pip
docker container exec "$CONTAINER" pip install pipenv
docker container exec "$CONTAINER" pipenv install

# コンテナ -> ホストにPipfile、Pipfile.lockを取得
docker container cp "$CONTAINER":/tmp/Pipfile Pipfile
docker container cp "$CONTAINER":/tmp/Pipfile.lock Pipfile.lock

# コンテナを停止/削除
docker container stop "$CONTAINER"