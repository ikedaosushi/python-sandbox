#!/bin/bash

IMAGE="pipfile_image"
TAG="latest"
CONTAINER="piplock_container"

# コンテナを起動
docker container run -e PIPENV_INSTALL_TIMEOUT=1800 --name "$CONTAINER" --rm -td "$IMAGE":"$TAG"

# ホスト -> コンテナにPipfile, PIpfile.lockを追加
docker container cp Pipfile "$CONTAINER":Pipfile
docker container cp Pipfile.lock "$CONTAINER":Pipfile.lock

# コンテナでPipfile.lock更新
docker container exec "$CONTAINER" pipenv lock

# コンテナ -> ホストにPipfile.lockを取得
docker container cp "$CONTAINER":Pipfile.lock Pipfile.lock

# コンテナを停止/削除
docker container stop "$CONTAINER"