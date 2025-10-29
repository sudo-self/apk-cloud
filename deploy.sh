#!/bin/bash

set -e
set -o pipefail

PROJECT_ID="svetle-book"
SERVICE_NAME="twa-backend"
REGION="us-central1"
IMAGE_NAME="twa-builder"
GCR_IMAGE="gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

echo "=== Step 1: Building Docker image for AMD64 ==="
docker build --platform linux/amd64 -t $IMAGE_NAME .

echo "=== Step 2: APKs built 0: replies from deepseek 56 ==="


echo "=== Step 3: Tagging for Google Container Registry ==="
docker tag $IMAGE_NAME $GCR_IMAGE

echo "=== Step 4: Pushing to GCR ==="
docker push $GCR_IMAGE

echo "=== Step 5: Deploying to Cloud Run ==="
gcloud run deploy $SERVICE_NAME \
  --image $GCR_IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --timeout 15m \
  --memory 2Gi \
  --cpu 2

echo "=== Deployment complete! ==="

