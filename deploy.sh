#!/bin/bash

set -e
set -o pipefail

PROJECT_ID="svetle-book"
SERVICE_NAME="twa-backend"
REGION="us-central1"
IMAGE_NAME="twa-builder"
GCR_IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

echo "=== Building Docker image ==="
docker build --platform linux/amd64 -t $IMAGE_NAME .

echo "=== Tagging for GCR ==="
docker tag $IMAGE_NAME $GCR_IMAGE

echo "=== Pushing to GCR ==="
docker push $GCR_IMAGE

echo "=== Deploying to Cloud Run ==="
gcloud run deploy $SERVICE_NAME \
  --image $GCR_IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --timeout 300s \
  --memory 512Mi \
  --cpu 1

echo "=== Deployment complete! ==="

