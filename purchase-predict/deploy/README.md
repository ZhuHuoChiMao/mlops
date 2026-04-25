# Deployment

This project can run locally with bundled model artifacts, or in Cloud Run/GKE
with a model loaded from MLflow.

Required values for cloud deployment:

- `PROJECT_ID`: Google Cloud project ID.
- `_REGION`: Artifact Registry and Cloud Run region.
- `_ARTIFACT_REPOSITORY`: Docker Artifact Registry repository.
- `_MLFLOW_TRACKING_URI`: MLflow tracking server URL.
- `_PURCHASE_MODEL_URI`: MLflow model URI, for example `models:/purchase_predict@production`.
- `_SERVICE_ACCOUNT`: optional Cloud Run service account email.

Cloud Build example:

```bash
gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions _REGION=europe-west1,_ARTIFACT_REPOSITORY=purchase-predict,_MLFLOW_TRACKING_URI=http://MLFLOW_HOST,_PURCHASE_MODEL_URI=models:/purchase_predict@production
```

Kubernetes example:

```bash
kubectl apply -f k8s/secret.example.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```
