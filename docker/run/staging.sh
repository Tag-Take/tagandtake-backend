#!/bin/bash

# Run Docker Compose for the staging environment
docker compose -f docker-compose.yml -f docker/compose/docker-compose.staging.yml up -d
