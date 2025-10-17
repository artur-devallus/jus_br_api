#!/usr/bin/env bash
set -a
source .env
set +a
celery -A tasks.celery_app worker -Q main --concurrency=4 --loglevel=INFO -n worker_main@%h & \
celery -A tasks.celery_app worker -Q trf --concurrency=2 --loglevel=INFO --max-memory-per-child=512000 -n worker_trf@%h