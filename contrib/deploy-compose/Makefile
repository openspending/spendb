COMPOSE=docker-compose -p spendb

.PHONY: clean compose

clean:
	$(COMPOSE) down
	$(COMPOSE) kill
	docker rmi $(docker images -q -f dangling=true)

compose:
	$(COMPOSE) build
	$(COMPOSE) up -d
	$(COMPOSE) run web spendb db migrate
