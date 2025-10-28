# Guía de Prompts para Copilot en GitHub Codespaces

**De 0 a despliegue en Streamlit Community Cloud**

> Use estos prompts en el chat de Copilot dentro de GitHub Codespaces. Copilot debe responder ejecutando comandos y creando/actualizando archivos. Mantenga la rama `main`.

---

## 0) Configuración inicial

**Prompt 0.1 — Crear repositorio y abrir Codespace**

```
Crea en el repositorio público llamado modelacion_predictiva_IA el archivo README y .gitignore de Python. Abre un Codespace en la rama main.
```

**Prompt 0.2 — Instalar extensión de Python y preparar terminal**

```
Instala la extensión oficial de Python en este Codespace. Abre una terminal integrada y confírmame que está activa.
```

---

## 1) Entorno virtual y versión de Python

**Prompt 1.1 — Crear y activar .venv**

```
Crea un entorno virtual Python llamado .venv, actívalo y muéstrame la versión de Python. Usa:
python -m venv .venv
source .venv/bin/activate
python --version
```

**Prompt 1.2 — Verificación de pip**

```
Actualiza pip y muéstrame la versión:
python -m pip install --upgrade pip
pip --version
```

---

## 2) Dependencias y archivos base

**Prompt 2.1 — requirements.txt**

```
Crea requirements.txt con estas líneas exactas:

streamlit
pandas
numpy
scikit-learn
matplotlib
joblib
requests
```

**Prompt 2.2 — Instalar dependencias**

```
Instala las dependencias con:
pip install -r requirements.txt
```

**Prompt 2.3 — .gitignore**

```
Crea o actualiza .gitignore con:

# Python
__pycache__/
*.pyc
.venv/

# Datos y artefactos
data/
models/
reports/
*.joblib
*.csv
*.json

# Streamlit
.streamlit/secrets.toml
```

**Prompt 2.4 — runtime.txt y .streamlit/config.toml**

```
Crea runtime.txt con "3.11" y crea la carpeta .streamlit con el archivo config.toml:

[server]
headless = true
port = 8501
enableCORS = false

[theme]
base = "light"
```

---

## 3) Estructura de proyecto

**Prompt 3.1 — Árbol de carpetas**

```
Crea la estructura de carpetas:

data/raw/
data/processed/
models/
reports/
notebooks/
```

---

## 4) Script de recolección de datos por API

**Prompt 4.1 — Crear collect_datasets.py**

```
Crea el archivo collect_datasets.py en la raíz y pega el script completo que explora y descarga datasets desde APIs (Socrata datos.gov.co, FAOSTAT, World Bank, HDX, OECD), incluyendo conectores, CLI y ejemplos de uso. Asegúrate de incluir:
- Clases: SocrataConnector, FAOSTATConnector, WorldBankConnector, HDXConnector, OECDConnector y StubConnector.
- Comandos: search, list, get.
- Descarga a data/raw/.
```

**Prompt 4.2 — Prueba de búsqueda**

```
Ejecuta:
python collect_datasets.py search --source ALL --q "agriculture" --limit 3
Guarda el JSON de resultados en data/raw/catalogo.json.
```

**Prompt 4.3 — Descarga de ejemplo**

```
Descarga un dominio de FAOSTAT (p. ej., QCL) a data/raw/:
python collect_datasets.py get --source FAOSTAT --id QCL --dest data/raw/
Muestra las primeras 5 filas con pandas y confirma ruta del archivo.
```

---

## 5) Script de análisis reproducible

**Prompt 5.1 — Crear analyze_datasets.py**

```
Crea analyze_datasets.py en la raíz con el flujo reproducible:
- EDA rápida (tamaños, tipos, NA, cardinalidad).
- Preprocesamiento (imputación num/cat, escalado, OHE) con ColumnTransformer.
- Clasificación: LogisticRegression y RandomForestClassifier con RandomizedSearchCV y StratifiedKFold.
- Regresión: Ridge y RandomForestRegressor con RandomizedSearchCV y KFold.
- Métricas: ROC AUC, PR AUC, F1, Balanced Accuracy, Brier; y RMSE, MAE, R².
- Curvas ROC/PR o Real vs Predicho.
- Importancias por permutación.
- Guardar artefactos en reports/<dataset>/ y models/<dataset>/, incluyendo REPORTE.md y metrics.json.
```

**Prompt 5.2 — Ejecución de prueba**

```
Ejecuta:
python analyze_datasets.py --input data/raw/faostat_QCL.csv --target Value --task auto
Muestra el JSON final de estado, rutas de reports y models.
```

**Prompt 5.3 — Verificar artefactos**

```
Lista el contenido de reports/faostat_QCL. Muestra metrics.json y renderiza REPORTE.md en la terminal.
```

---

## 6) Aplicación Streamlit

**Prompt 6.1 — Crear app.py**

```
Crea app.py que:
- Tenga 3 secciones en barra lateral: "1) Catálogo y descarga", "2) Análisis", "3) Reportes".
- Sección 1: ejecute collect_datasets.py search/get desde subprocess, muestre JSON y guarde catalogo.json.
- Sección 2: permita seleccionar CSV en data/raw, definir target y parámetros, ejecutar analyze_datasets.py y mostrar salida.
- Sección 3: liste subcarpetas en reports, muestre métricas (metrics.json), figuras (roc_curve.png/pr_curve.png o real_vs_predicho.png) y REPORTE.md.
Asegura compatibilidad con Streamlit Community Cloud.
```

**Prompt 6.2 — README_streamlit.md**

```
Crea README_streamlit.md con la versión corta de la portada para la app. En app.py, carga su contenido en la sección inicial con st.markdown si el archivo existe.
```

**Prompt 6.3 — Prueba local de la app**

```
Ejecuta:
streamlit run app.py
Publica el puerto y confírmame que el UI carga y lista CSV en data/raw.
```

---

## 7) Documentación del proyecto

**Prompt 7.1 — README.md principal**

```
Genera README.md con:
- Propósito del proyecto.
- Arquitectura reproducible (Codespaces → Copilot → Streamlit Cloud).
- Estructura del repo.
- Ejemplos de uso de collect_datasets.py y analyze_datasets.py.
- Guía de despliegue en Streamlit Community Cloud y manejo de secrets.
- Créditos y líneas de publicación sugeridas.
```

---

## 8) Git y sincronización

**Prompt 8.1 — Commit y push**

```
Ejecuta:
git add .
git commit -m "Versión inicial reproducible: datasets + modelado + app"
git push origin main
Muestra la URL del repositorio.
```

**Prompt 8.2 — Congelar versiones**

```
Genera requirements_versions.txt con:
pip freeze > requirements_versions.txt
Haz commit y push.
```

---

## 9) Despliegue en Streamlit Community Cloud

**Prompt 9.1 — Preparación de archivos**

```
Verifica que existan: app.py, requirements.txt, runtime.txt, .streamlit/config.toml. Confirma que data/, models/ y reports/ estén en .gitignore.
```

**Prompt 9.2 — Instrucciones de despliegue (para pegar en README)**

```
Inserta en README.md una sección "Despliegue" con pasos:
1) Ir a https://share.streamlit.io
2) New app → seleccionar repo, rama main y app.py
3) En Secrets: pegar claves (SOCRATA_APP_TOKEN, HDX_API_KEY si aplica)
4) Deploy
```

**Prompt 9.3 — Secrets (plantilla)**

```
Agrega en README.md un bloque de ejemplo para Secrets:

SOCRATA_APP_TOKEN = "xxxxx"
HDX_API_KEY = "xxxxx"
```

---

## 10) Buenas prácticas y reproducibilidad

**Prompt 10.1 — Sección de buenas prácticas**

```
Añade al README.md una sección "Buenas prácticas":
- Fijar semillas (--random-state 42)
- Evitar fuga de datos
- Documentar ejecuciones
- No subir datos sensibles
- Guardar artefactos en reports/ y models/
```

**Prompt 10.2 — Registro de corridas**

```
Crea logs/ y un script simple logs_run.md que registre fecha, dataset, tarea, mejor modelo y métricas clave. Añade un ejemplo y haz commit.
```

---

## 11) Prompts de interpretación científica

**Prompt 11.1 — Resumen ejecutivo**

```
Lee reports/<dataset>/REPORTE.md y genera un resumen ejecutivo de 150–200 palabras para paper, incluyendo métricas clave.
```

**Prompt 11.2 — Umbrales y costos**

```
Con base en roc_curve.png y pr_curve.png, propone un umbral operativo cuando el costo de FN > FP. Entrega TPR, FPR, Precision y Recall aproximados.
```

**Prompt 11.3 — Importancias y sesgos**

```
Analiza importancias_permutacion.png e importances.json. Identifica 3 variables dominantes, posibles sesgos y controles propuestos.
```

**Prompt 11.4 — Sección Métodos**

```
Redacta la sección Métodos: EDA, preprocesamiento, validación, búsqueda de hiperparámetros, métricas y criterios de selección.
```

**Prompt 11.5 — Reproducibilidad**

```
Redacta una sección de reproducibilidad: versiones, semillas, rutas de salida y comandos para re-ejecutar todo el pipeline.
```

---

## 12) QA y resolución de problemas

**Prompt 12.1 — Diagnóstico rápido**

```
Si collect_datasets.py falla, muestra el error completo y sugiere si falta token o si el endpoint requiere filtros. Prueba una búsqueda alternativa con --source WORLD_BANK y --q "population".
```

**Prompt 12.2 — Memoria y tiempo**

```
Si analyze_datasets.py demora, reduce n_iter de RandomizedSearchCV a 10 y limita filas con una muestra aleatoria de 50k si el CSV supera 1e6 filas.
```

**Prompt 12.3 — Gráficos vacíos**

```
Si no aparecen curvas, confirma que la tarea fue 'binary' y que existe clase positiva. Si es regresión, muestra real_vs_predicho.png.
```

---

## 13) Cierre del proyecto

**Prompt 13.1 — Commit final**

```
Ejecuta:
git add .
git commit -m "Proyecto listo: recolección, análisis, app y guía de despliegue"
git push origin main
```

**Prompt 13.2 — Checklist final**

```
Genera en README.md un checklist de verificación:
- [ ] Entorno .venv activo
- [ ] Dependencias instaladas
- [ ] Datos descargados en data/raw
- [ ] Reportes generados en reports/
- [ ] App Streamlit ejecuta en Codespaces
- [ ] Despliegue en Streamlit Cloud activo
- [ ] README y logs completos
```

---

### Anexo: Comandos útiles

**Actualizar dependencias**

```
pip install -U pandas numpy scikit-learn matplotlib joblib requests streamlit
```

**Ejecutar scripts**

```
python collect_datasets.py search --source ALL --q "agriculture" --limit 5
python collect_datasets.py get --source FAOSTAT --id QCL --dest data/raw/
python analyze_datasets.py --input data/raw/faostat_QCL.csv --target Value --task auto
```

**Correr la app localmente**

```
streamlit run app.py
```

**Git básico**

```
git status
git add .
git commit -m "mensaje"
git push origin main
```
