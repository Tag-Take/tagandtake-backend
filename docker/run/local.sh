#!/bin/bash

# Run Docker Compose for the local environment
docker compose -f docker-compose.yml -f docker/compose/docker-compose.local.yml up