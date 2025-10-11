#!/usr/bin/env bash
set -a
source .env
set +a
celery -A tasks.celery_app worker -Q main --concurrency=4 --loglevel=INFO -n worker_main@%h & \
celery -A tasks.celery_app worker -Q trf1 --concurrency=1 --loglevel=INFO -n worker_trf1@%h & \
celery -A tasks.celery_app worker -Q trf2 --concurrency=1 --loglevel=INFO -n worker_trf2@%h & \
celery -A tasks.celery_app worker -Q trf3 --concurrency=1 --loglevel=INFO -n worker_trf3@%h & \
celery -A tasks.celery_app worker -Q trf4 --concurrency=1 --loglevel=INFO -n worker_trf4@%h & \
celery -A tasks.celery_app worker -Q trf5 --concurrency=1 --loglevel=INFO -n worker_trf5@%h & \
celery -A tasks.celery_app worker -Q trf6 --concurrency=1 --loglevel=INFO -n worker_trf6@%h