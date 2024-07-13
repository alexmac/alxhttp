#!/bin/sh
docker rm -f  alxhttp-sql alxhttp-redis

pushd sql
docker build --progress=plain -t alxhttp-sql .
docker run -d --name alxhttp-sql -p 6432:5432 alxhttp-sql
popd
pushd redis
docker build --progress=plain -t alxhttp-redis .
docker run -d --name alxhttp-redis -p 7379:6379 alxhttp-redis