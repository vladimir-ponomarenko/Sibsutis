SHELL := /bin/bash

.PHONY: build up down restart run show all clean

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart: down up

run:
	docker compose exec -T server ansible-playbook -i /work/inventory.ini /work/site.yml

show:
	docker compose exec -T server ls -la /etc/ansible/IT-Planet
	docker compose exec -T server cat /etc/ansible/IT-Planet/client1.txt
	docker compose exec -T server cat /etc/ansible/IT-Planet/client2.txt

all: build up run show

clean:
	docker compose down -v
	@echo "Removed containers and volumes"
