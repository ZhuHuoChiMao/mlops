from __future__ import annotations

from typing import Any

import mlflow
import mlflow.sklearn


def select_model_for_deployment(  # noqa: PLR0913
    trained_model: dict[str, Any],
    metrics: dict[str, float | str],
    minimum_f1: float,
    mlflow_enabled: bool,
    mlflow_registered_model_name: str,
    mlflow_tracking_uri: str | None,
) -> dict[str, Any]:
    """Return the model artifact when it passes the deployment threshold."""
    f1 = float(metrics["f1"])
    if f1 < minimum_f1:
        raise ValueError(f"Model f1={f1:.4f} is below deployment threshold {minimum_f1:.4f}")
    if mlflow_enabled:
        _register_model(trained_model, mlflow_registered_model_name, mlflow_tracking_uri)
    return trained_model


def _register_model(
    trained_model: dict[str, Any],
    registered_model_name: str,
    tracking_uri: str | None,
) -> None:
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)

    with mlflow.start_run(run_name=f"register-{trained_model['name']}"):
        model_info = mlflow.sklearn.log_model(
            sk_model=trained_model["model"],
            artifact_path="model",
            registered_model_name=registered_model_name,
        )
        mlflow.set_tag("model_uri", model_info.model_uri)
