#---- VARIABLES ----#

APPDIR := $(subst /, , $(subst  ./ntnui/apps/, , $(filter-out ./ntnui/apps/,$(dir $(wildcard ./ntnui/apps/*/)))))
JSONDATA := users.json groups.json memberships.json boards.json invitations.json forms.json mainboard.json hs-memberships.json contracts.json events.json
JSONDOKKU := users.json groups.json memberships.json boards.json invitations.json forms.json mainboard.json hs-memberships.json
DATABASE := dev_database.db

#---- END VARIABLES ----#

#---- HELP COMMANDS ----#

GREEN  := $(shell tput -Txterm setaf 2)
WHITE  := $(shell tput -Txterm setaf 7)
YELLOW := $(shell tput -Txterm setaf 3)
RED := $(shell tput -Txterm setaf 5)
RESET  := $(shell tput -Txterm sgr0)

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
# A category can be added with @category
HELP_COMM = \
    %help; \
    while(<>) { \
        if(/^([a-z0-9_-]+):.*\#\#(?:@(\w+))?\s(.*)$$/) { \
            push(@{$$help{$$2}}, [$$1, $$3]); \
        } \
    }; \
    print "usage: make [target]\n\n"; \
    for ( sort keys %help ) { \
        print "${WHITE}$$_:${RESET}\n"; \
        printf("  ${YELLOW}%-30s ${GREEN}%s${RESET}\n", $$_->[0], $$_->[1]) for @{$$help{$$_}}; \
        print "\n"; \
    }

help:
	@-clear
	@perl -e '$(HELP_COMM)' $(MAKEFILE_LIST)

#---- END HELP COMMANDS ----#

#---- DOCKER INSTALL COMMANDS ----#

docker_build: ##@Docker (bld) Install requirements found in requirements.txt
	@-docker-compose build

docker_migrations: ##@Docker Set up migration files
	@-docker-compose run web python manage.py makemigrations
	@echo "Migrations completed successfully"

# Run the makemigrations command on every app in the /apps folder
docker_force_migrations: ##@Docker Forcibly perform makemigrations on the separate apps
	$(foreach app,$(filter-out __pycache__, $(APPDIR)), docker-compose run web python manage.py makemigrations $(app);)
	@echo "Migrations completed successfully"

docker_migrate: ##@Docker Perform migrations to database
	@-docker-compose run web python manage.py migrate
	@echo "Migrate completed successfully"

docker_start: ##@Docker (start) Start the webserver on http://localhost:8000
	@-docker-compose up web

docker_start_background: ##@Docker Start the webserver on http://localhost:8000 as a background process
	@-docker-compose up web -d
	@echo "Webserver running in the background on http://localhost:8000. Run docker_stop to end the process"

docker_stop: ##@Docker (stop) Stop the running containers
	@-docker-compose down

docker_superuser: ##@Docker Create a superuser (details found in settings/common.py)
	@-docker-compose run web python manage.py createsuperuser

docker_app: ##@Docker Create a new app. 
	@read -p "Enter app name: " app; \
	mkdir ntnui/apps/$$app; \
	docker-compose run web python manage.py startapp $$app ntnui/apps/$$app
	@echo "App successfully created. Make sure you add it to the LOCAL_APPS in settings/common.py"

#---- END DOCKER INSTALL COMMANDS ----#

#----- TEST ENVIRONMENT COMMANDS ----#

dev_clean: ##@TestEnv Delete the old database and re-apply testdata
	@-rm -f $(DATABASE)
	@-make docker_migrations
	@-make docker_force_migrations
	@-make docker_migrate
	@-make dev_loaddata

dev_clean_install: ##@TestEnv (dci) Perform a clean installation of the test environment
	@-make dev_clean_migrations # Delete previous migration files
	@-make dev_clean
	@echo "Installation successfull. Starting server on http://localhost:8000"
	@-make docker_start

dev_clean_migrations: ##@TestEnv Delete all migration files
	@-$(foreach file,$(wildcard ./ntnui/apps/*/migrations/*/),rm -rf $(file))

dev_loaddata:
	@-docker-compose run web python manage.py loaddata $(JSONDATA)

dev_dumpdata:
	@-docker-compose run web python manage.py dumpdata --format=json --exclude auth.permission >  ntnui/fixtures/initial_data.json

docker_test: ##@Test (test) Run all docker-tests (this does not include browser-tests)
	$(foreach app,$(filter-out __pycache__, $(APPDIR)), docker-compose run web python manage.py test $(app);)  # Run the test suite (details found in settings/common.py)
	@-make docker_stop

docker_browser_test: ##@Test (btest) Run all browser-tests in docker
	@-docker-compose up -d chrome
	@echo "Chrome instance started"
	@-docker-compose up -d firefox
	@echo "Firefox instance started"
	@-docker-compose run tester python3 manage.py test ntnui.tests.browser
	@echo "Browser test suite completed"
	@-make docker_stop

docker_clean_test: ##@Test Clean and reapply database and run test suite
	@-make docker_stop # Stop all running tests before re-installing the database
	@-make docker_clean
	@-make docker_test

docker_clean_browser_test:  ##@Test Clean and reapply databse and run browser tests
	@-make docker_stop
	@-make docker_clean
	@-make docker_browser_test

#----- END TEST ENVIRONMENT COMMANDS ----#

#----- VIRTUAL/LOCAL ENVIRONMENT COMMANDS ----#

local_browser_tests: ##@VirtualEnv Run browser tests locally
	BROWSER=local python3 manage.py test ntnui.tests.browser

#----- END VIRTUAL/LOCAL ENVIRONMENT COMMANDS ----#

#----- DEPLOYMENT COMMANDS ----#

dokku_env: ##@Deployment Set up the Dokku environment
	@-rm -f $(DATABASE)
	@-make docker_migrations
	@-make docker_force_migrations
	@-make docker_migrate
	@-docker-compose run web python manage.py loaddata $(JSONDOKKU)

#----- END DEPLOYMENT COMMANDS ----#

#---- SHORTCUTS ----#

# If you change something here, make sure to change the flavour text to accomodate it!
dci:
	@-make dev_clean_install

bld:
	@-make docker_build

test:
	@-make docker_test

btest:
	@-make docker_browser_test

start:
	@-make docker_start

stop:
	@-make docker_stop

#---- END SHORTCUTS ----#

#---- LEGACY ----#

rasmus:
	python manage.py runserver 0.0.0.0:3000

ask:
	docker-compose run web python manage.py dumpdata groups.Contract > contracts.json

envrun:
	python3 manage.py runserver 0.0.0.0:8000

envstyle:
	autopep8 --in-place --recursive --max-line-length=100 accounts forms groups ntnui hs
	prospector --uses django --max-line-length=100

#---- END LEGACY ----#