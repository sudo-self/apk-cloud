# Build the image
docker build -t twa-builder .

# Test locally
docker run -p 8080:8080 twa-builder

# Push to Google Container Registry
docker tag twa-builder gcr.io/svetle-book/twa-backend:latest
docker push gcr.io/svetle-book/twa-backend:latest

# Deploy to Cloud Run
gcloud run deploy twa-backend \
  --image gcr.io/svetle-book/twa-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --timeout 15m \
  --memory 2Gi \
  --cpu 2
