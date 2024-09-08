# tagandtake-backend

This repository contains the tagandtake.com backend application, built using Django and containerized with Docker. The backend is run in Python 3.11, using a PostgreSQL database, Redis, celery and celery-beat, all of which are also containerized. Below is a step-by-step guide to setting up the project locally.

## Prerequisites

Before setting up the project, ensure you have the following tools installed:

- \[Docker\](https://docs.docker.com/get-docker/)
- \[Docker Compose\](https://docs.docker.com/compose/install/)
- Python 3.11 (only if you intend to run the backend outside Docker)

## Getting Started

1. Clone the repository to your local machine:

```bash
git clone \<https://github.com/Tag-Take/tagandtake-backend.git\>
cd \<tagandtake-backend\>
```

2. Create a `.env` file in the root directory and add the following variables (customize the values as needed):

```bash
# Local PostgreSQL configuration
NAME=tagandtake_core
USER=postgres
PASSWORD=123456
HOST=db
PORT=5432

# AWS S3 configuration (keys will require setting up)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=tagandtake-testing
AWS_S3_REGION_NAME=eu-west-2

# Email server configuration
EMAIL_HOST_USER=test_email_user@test.com
EMAIL_HOST_PASSWORD=test_password

# Redis configuration
REDIS_URL=redis://redis:6379/0
```

## Building and Running the Docker Containers

To build and run the backend along with its dependencies (PostgreSQL and Redis), use Docker Compose:

```bash
docker-compose up --build
```

This command will:

- Build the `web` service using the `development` stage from the `Dockerfile`.
- Start the `db` service for PostgreSQL.
- Start the `redis` service.
- Start Celery workers and the Celery beat scheduler.

The backend will wait for PostgreSQL to be ready before running the initial setup (migrations, static file collection, etc.). Once everything is set up, the web server will be accessible at \[http://localhost:8000\](http://localhost:8000).

## Managing Docker Containers

- If you make changes to the code or configuration, rebuild the containers:

```bash
docker-compose up --build
```

- to simply run the backend services as of the most recent image build:

```bash
docker-compose up
```

- To stop and remove the running containers:

```bash
docker-compose down
```

- To stop and remove the running containers and delete associated db

```bash
docker-compose down -v
```

- To view logs from all services:

```bash
docker-compose logs -f
```

## Running Django Commands Inside the Container

You can run Django commands inside the `web` container by using:

```bash
docker-compose exec web poetry run python manage.py \<command\>
```

For example, to create a superuser:

```bash
docker-compose exec web poetry run python manage.py createsuperuser
```

## Project Structure

This repo caontains all backend services (containerized). Below are the services defined in the `docker-compose.yml`:

- `web`: The Django application container.
- `db`: The PostgreSQL database container.
- `redis`: The Redis container (for task queues).
- `celery_worker`: Celery worker process (for async tasks).
- `celery_beat`: Celery beat scheduler for (async) periodic tasks.

## Docker Volumes

The project uses Docker volumes to persist data:

- `postgres_data`: This volume is used to store the PostgreSQL database files.

## Additional Notes

- The backend uses \[Poetry\](https://python-poetry.org/) for dependency management. Dependencies are installed inside the container when it's built.
- The production stage in the Dockerfile uses Gunicorn for running the app in production mode, while the development stage uses Django's built-in server.

## Common Issues

- \*\*Database not ready\*\*: If the web service outputs `Waiting for PostgreSQL to be ready...`, it means the database is still starting up. Wait until you see the message `PostgreSQL is ready.`.
- \*\*Migrations not applied\*\*: If there are database issues, you can manually apply migrations using:

```bash
docker-compose exec web poetry run python manage.py migrate
```

---

For further information or assistance, feel free to reach out to the project maintainers.
