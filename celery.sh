#!/usr/bin/env bash
set -a
source .env
set +a
celery -A tasks.celery_app worker -Q main --concurrency=4 --loglevel=INFO -n worker_main@%h & \
celery -A tasks.celery_app worker -Q trf --concurrency=1 --loglevel=INFO -n worker_trf@%h & \