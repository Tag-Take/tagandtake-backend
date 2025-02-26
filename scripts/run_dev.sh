#!/bin/bash

# Run Docker Compose for the local environment
#!/bin/bash
# Forward all arguments ($@) to the docker compose command.
# E.g. scripts/run_dev.sh exec web sh /app/ops/migrate.sh
docker compose -f docker-compose.yml -f docker/compose/docker-compose.dev.yml "$@"
