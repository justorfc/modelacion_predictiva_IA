#!/usr/bin/env python3
"""analyze_datasets.py

Implementación mínima para ejecutar un flujo reproducible sobre un CSV local.
- EDA básica
- Detección automática de tarea (regresión si target es numérico)
- Preprocesamiento simple (imputación numérica, OneHot para categóricas)
- Modelos: Ridge (regresión) y RandomForestRegressor
- Guardado de modelo y métricas

El script intenta importar dependencias y, si faltan, muestra instrucciones.
"""
import argparse
import json
import os
from pathlib import Path
import sys


def check_deps():
    missing = []
    try:
        import pandas as pd
        import numpy as np
        from sklearn.model_selection import train_test_split
    except Exception:
        missing = ["pandas", "numpy", "scikit-learn"]
    return missing


def simple_eda(df):
    info = {
        "shape": df.shape,
        "dtypes": df.dtypes.apply(lambda x: str(x)).to_dict(),
        "n_missing": df.isna().sum().to_dict(),
        "head": df.head(3).to_dict(orient="records"),
    }
    return info


def run_analysis(input_path, target, task, random_state=42):
    # Lazy imports
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.linear_model import Ridge
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    import joblib

    df = pd.read_csv(input_path)
    eda = simple_eda(df)

    if target not in df.columns:
        raise ValueError(f"Target {target} not found in columns")

    X = df.drop(columns=[target])
    y = df[target]

    # Determine task if auto
    if task == "auto":
        if pd.api.types.is_numeric_dtype(y):
            task = "regression"
        else:
            task = "classification"

    # For this minimal flow, only regression is implemented
    if task != "regression":
        raise NotImplementedError("Solo 'regression' está implementado en este stub.")

    # Simple preprocessing
    num_cols = X.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()

    num_pipeline = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])

    # Build OneHotEncoder in a way compatible con varias versiones de scikit-learn
    try:
        # scikit-learn >=1.2 uses sparse_output
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        # Older versions use 'sparse'
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)

    cat_pipeline = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="__missing__")),
        ("ohe", ohe),
    ])

    preproc = ColumnTransformer([
        ("num", num_pipeline, num_cols),
        ("cat", cat_pipeline, cat_cols),
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)

    # Models
    ridge = Pipeline([("pre", preproc), ("model", Ridge(random_state=random_state))])
    rf = Pipeline([("pre", preproc), ("model", RandomForestRegressor(random_state=random_state, n_jobs=1))])

    print("Entrenando Ridge...")
    ridge.fit(X_train, y_train)
    print("Entrenando RandomForest...")
    rf.fit(X_train, y_train)

    preds_ridge = ridge.predict(X_test)
    preds_rf = rf.predict(X_test)

    # Calculate metrics and ensure compatibility across sklearn versions
    import numpy as _np
    mse_ridge = mean_squared_error(y_test, preds_ridge)
    mse_rf = mean_squared_error(y_test, preds_rf)
    metrics = {
        "ridge": {
            "rmse": float(_np.sqrt(mse_ridge)),
            "mae": float(mean_absolute_error(y_test, preds_ridge)),
            "r2": float(r2_score(y_test, preds_ridge)),
        },
        "random_forest": {
            "rmse": float(_np.sqrt(mse_rf)),
            "mae": float(mean_absolute_error(y_test, preds_rf)),
            "r2": float(r2_score(y_test, preds_rf)),
        },
    }

    # Save artifacts
    dataset_name = Path(input_path).stem
    reports_dir = Path("reports") / dataset_name
    models_dir = Path("models") / dataset_name
    reports_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    # Save metrics
    with open(reports_dir / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # Save models
    joblib.dump(ridge, models_dir / "ridge.joblib")
    joblib.dump(rf, models_dir / "rf.joblib")

    # Simple report
    with open(reports_dir / "REPORTE.md", "w", encoding="utf-8") as f:
        f.write(f"# Reporte automático para {dataset_name}\n\n")
        f.write("## EDA\n")
        f.write(json.dumps({k: (v if not hasattr(v, 'to_dict') else str(v)) for k, v in eda.items()}, indent=2, ensure_ascii=False))
        f.write("\n\n## Metrics\n")
        f.write(json.dumps(metrics, indent=2, ensure_ascii=False))

    # Save a run-state summary
    state = {"dataset": dataset_name, "reports_dir": str(reports_dir), "models_dir": str(models_dir), "metrics": metrics}
    print(json.dumps(state, indent=2, ensure_ascii=False))
    return state


def main():
    parser = argparse.ArgumentParser(description="Analizar dataset CSV (stub minimal)")
    parser.add_argument("--input", required=True, help="CSV input path")
    parser.add_argument("--target", required=True, help="Target column name")
    parser.add_argument("--task", default="auto", help="auto|regression|classification")
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    missing = check_deps()
    if missing:
        print("Faltan dependencias necesarias:", ", ".join(missing))
        print("Instálalas con: pip install -r requirements.txt")
        sys.exit(2)

    run_analysis(args.input, args.target, args.task, random_state=args.random_state)


if __name__ == "__main__":
    main()
