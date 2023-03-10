#!/usr/bin/env bash

set shell := ["bash", "-uc"]

current_dir := justfile_directory()
compose_files := "-f docker-compose.yml"
docker_compose := "docker-compose"
docker_inspect_ip := "docker inspect -f {{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}"
containers_table_format := "table {{.ID}}\t{{.Status}}\t{{.Names}}\t{{.Ports}}"


default:
    just --list

pre-commit:
	pre-commit run --all-files

build:
	docker-compose {{compose_files}} build

up:
	docker-compose {{compose_files}} up -d

down:
	docker-compose down --remove-orphans

logs *args='':
	{{docker_compose}} logs {{args}}

api-console:
	docker exec -it api sh

db-console:
	docker exec -it pgdb psql finpan user

stop-api:
    docker stop api

show-containers:
    docker ps --format "{{containers_table_format}}"

echo-postgres-ip:
    #!/usr/bin/env bash
    echo POSTGRES_SERVER=$({{docker_inspect_ip}} pgdb)
