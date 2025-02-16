#!/bin/bash

# Run Docker Compose for the production environment
docker compose -f docker-compose.yml -f docker/compose/docker-compose.prod.yml up -d
