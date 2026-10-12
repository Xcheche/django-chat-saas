# Declare all targets as .PHONY so local folders (like 'config' or 'test') don't block them
.PHONY: help build up down restart logs logs-service shell clean test migrate check-migrations makemigrations createsuperuser create-app config pony static status

# Colors
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
PURPLE := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
RESET := \033[0m

help:
	@echo "$(CYAN)🐴 Django Celery Project Makefile 🐴$(RESET)"
	@echo ""
	@echo "$(YELLOW)Available commands:$(RESET)"
	@echo "  $(GREEN)build$(RESET)            - Build Docker image"
	@echo "  $(GREEN)up$(RESET)               - Start containers"
	@echo "  $(GREEN)down$(RESET)             - Stop containers"
	@echo "  $(GREEN)config$(RESET)           - Check Docker Compose configuration"
	@echo "  $(GREEN)logs$(RESET)             - Show container logs"
	@echo "  $(GREEN)shell$(RESET)            - Open Django shell"
	@echo "  $(GREEN)migrate$(RESET)          - Run database migrations"
	@echo "  $(GREEN)makemigrations$(RESET)   - Create migration files"
	@echo "  $(GREEN)clean$(RESET)            - Clean Docker resources"
	@echo "  $(GREEN)test$(RESET)             - Run tests"
	@echo "  $(GREEN)pony$(RESET)             - Show a pony!"

pony:
	@echo "$(PURPLE)"
	@echo "                 ,~~."
	@echo "                (  9 >-___"
	@echo "            _.-'  '-'  ) )"
	@echo "        __.'  _       ( ("
	@echo "      .'     ( )       | |"
	@echo "     /    .---'        | |"
	@echo "    |   (               | |"
	@echo "    |    '---.      __  | |"
	@echo "    |         '---'  |  | |"
	@echo "    |    .---.    _.'  | |"
	@echo "    |  (       )'     / /"
	@echo "    |   '---'   '---'  /"
	@echo "    |                /"
	@echo "    '---------------'$(RESET)"
	@echo "$(CYAN)🦄 Here is your magical pony! 🦄$(RESET)"

build:
	@echo "$(BLUE)🔨 Building Docker image...$(RESET)"
	@docker compose build
	@echo "$(GREEN)✅ Docker image built successfully!$(RESET)"
	@make pony

up:
	@echo "$(BLUE)🚀 Starting containers...$(RESET)"
	@docker compose up -d
	@echo "$(GREEN)✅ Containers are running!$(RESET)"
	@echo "$(YELLOW)🌐 App is available at: http://localhost:8001$(RESET)"
	@make pony

down:
	@echo "$(YELLOW)🛑 Stopping containers...$(RESET)"
	@docker compose down
	@echo "$(GREEN)✅ Containers stopped successfully!$(RESET)"

restart:
	@echo "$(YELLOW)🔄 Restarting containers...$(RESET)"
	@docker compose down
	@docker compose up -d
	@echo "$(GREEN)✅ Containers restarted successfully!$(RESET)"
	@make pony

logs:
	@echo "$(CYAN)📋 Showing container logs...$(RESET)"
	@docker compose logs -f

logs-service:
	@echo "$(CYAN)📋 Showing logs for a specific service...$(RESET)"
	@read -p "Enter the service name (e.g., web, db): " service; \
	docker compose logs -f $$service

shell:
	@echo "$(BLUE)🐚 Opening Django shell...$(RESET)"
	@docker compose exec web python manage.py shell

clean:
	@echo "$(RED)🧹 Cleaning Docker resources...$(RESET)"
	@docker compose down -v --remove-orphans
	@docker system prune -f
	@echo "$(GREEN)✅ Docker resources cleaned!$(RESET)"

test:
	@echo "$(BLUE)🧪 Running tests...$(RESET)"
	@docker compose exec web python manage.py test
	@echo "$(GREEN)✅ Tests completed!$(RESET)"

migrate:
	@echo "$(BLUE)🗄️ Running database migrations...$(RESET)"
	@docker compose exec web python manage.py migrate
	@echo "$(GREEN)✅ Migrations completed!$(RESET)"

check-migrations:
	@echo "$(BLUE)🔍 Checking for pending migrations...$(RESET)"
	@docker compose exec web python manage.py makemigrations --dry-run --check
	@echo "$(GREEN)✅ Migration check completed!$(RESET)"

makemigrations:
	@echo "$(BLUE)📝 Creating migration files...$(RESET)"
	@docker compose exec web python manage.py makemigrations
	@echo "$(GREEN)✅ Migration files created!$(RESET)"

createsuperuser:
	@echo "$(BLUE)👤 Creating superuser...$(RESET)"
	@docker compose exec web python manage.py createsuperuser
	@echo "$(GREEN)✅ Superuser creation process initiated!$(RESET)"

create-app:
	@echo "$(BLUE)📦 Creating a new Django app...$(RESET)"
	@read -p "Enter the app name: " app_name; \
	docker compose exec web python manage.py startapp $$app_name
	@echo "$(GREEN)✅ Django app '$$app_name' created successfully!$(RESET)"

config:
	@echo "$(BLUE)🔧 Checking Docker Compose configuration...$(RESET)"
	@docker compose config

status:
	@echo "$(CYAN)📊 Checking the status of containers...$(RESET)"
	@docker compose ps



static:
	@echo "$(BLUE)📦 Collecting static files...$(RESET)"
	@docker compose exec web python manage.py collectstatic --noinput
	@echo "$(GREEN)✅ Static files collected!$(RESET)"


################################Test##########################
test-general:
	docker compose exec web pytest -v
test-functional:
	docker compose exec web pytest -m functional
test-by-name:
	@read -p "Enter the test name (e.g., test_home.py): " test_name; \
	docker compose exec web pytest -v tests/functional/$$test_name