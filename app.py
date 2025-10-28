#!/usr/bin/env python3
"""Streamlit app minimal que orquesta collect_datasets.py y analyze_datasets.py

Secciones (barra lateral):
 1) Catálogo y descarga
 2) Análisis
 3) Reportes

El app usa subprocess para llamar a los scripts ya presentes en el repo.
"""
import streamlit as st
from pathlib import Path
import subprocess
import json


st.set_page_config(page_title="Modelación Predictiva App", layout="wide")

st.sidebar.title("Navegación")
section = st.sidebar.radio("Sección", ["1) Catálogo y descarga", "2) Análisis", "3) Reportes"])


def run_command(cmd):
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode, res.stdout, res.stderr
    except Exception as e:
        return 1, "", str(e)


DATA_RAW = Path("data/raw")
REPORTS = Path("reports")


if section == "1) Catálogo y descarga":
    st.header("Catálogo y descarga")

    st.subheader("Buscar datasets (collect_datasets.py)")
    src = st.selectbox("Fuente", ["ALL", "SOCRATA", "FAOSTAT", "WORLD_BANK", "HDX", "OECD"])
    q = st.text_input("Query", "agriculture")
    limit = st.number_input("Límite", value=3, min_value=1)
    if st.button("Buscar"):
        out = "data/raw/catalogo.json"
        cmd = ["python", "collect_datasets.py", "search", "--source", src, "--q", q, "--limit", str(limit), "--out", out]
        code, out_s, err = run_command(cmd)
        if code == 0:
            st.success("Búsqueda ejecutada. Resultado guardado en data/raw/catalogo.json")
            try:
                with open(out, "r", encoding="utf-8") as f:
                    j = json.load(f)
                st.json(j)
            except Exception as e:
                st.error(f"No se pudo leer {out}: {e}")
        else:
            st.error(f"Error ejecutando search: {err}\n{out_s}")

    st.subheader("Descargar dataset (get)")
    src_get = st.selectbox("Fuente (get)", ["FAOSTAT", "SOCRATA", "WORLD_BANK", "HDX", "OECD"])
    dataset_id = st.text_input("Dataset ID (ej: QCL)")
    dest = st.text_input("Destino", "data/raw/")
    if st.button("Descargar"):
        if not dataset_id:
            st.warning("Proporciona un dataset id (por ejemplo QCL)")
        else:
            cmd = ["python", "collect_datasets.py", "get", "--source", src_get, "--id", dataset_id, "--dest", dest]
            code, out_s, err = run_command(cmd)
            if code == 0:
                st.success("Descarga completada")
                st.text(out_s)
            else:
                st.error(f"Error al descargar: {err}\n{out_s}")


elif section == "2) Análisis":
    st.header("Análisis reproducible")
    st.write("Selecciona un CSV en `data/raw` y define la columna target.")
    csvs = [str(p.name) for p in DATA_RAW.glob("*.csv")]
    if not csvs:
        st.info("No hay CSV en data/raw. Usa la sección 1 para descargar uno (por ejemplo FAOSTAT QCL).")
    selected = st.selectbox("CSV", csvs)
    target = st.text_input("Target column", "Value")
    task = st.selectbox("Task", ["auto", "regression", "classification"], index=0)
    if st.button("Ejecutar análisis"):
        if not selected:
            st.warning("Selecciona un CSV")
        else:
            input_path = str(DATA_RAW / selected)
            cmd = ["python", "analyze_datasets.py", "--input", input_path, "--target", target, "--task", task]
            with st.spinner("Analizando — puede tardar..."):
                code, out_s, err = run_command(cmd)
            if code == 0:
                st.success("Análisis completado")
                st.text(out_s)
            else:
                st.error(f"Error en analyze_datasets.py:\n{err}\n{out_s}")


else:  # Reports
    st.header("Reportes")
    datasets = [p.name for p in REPORTS.iterdir() if p.is_dir()] if REPORTS.exists() else []
    if not datasets:
        st.info("No hay reportes generados todavía.")
    else:
        ds = st.selectbox("Dataset", datasets)
        rd = REPORTS / ds
        st.subheader("Métricas")
        metrics_file = rd / "metrics.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, "r", encoding="utf-8") as f:
                    m = json.load(f)
                st.json(m)
            except Exception as e:
                st.error(f"Error leyendo metrics.json: {e}")
        else:
            st.warning("metrics.json no encontrado en el reporte")

        st.subheader("REPORTE.md")
        rep = rd / "REPORTE.md"
        if rep.exists():
            try:
                txt = rep.read_text(encoding="utf-8")
                st.markdown(txt)
            except Exception as e:
                st.error(f"Error leyendo REPORTE.md: {e}")
        else:
            st.info("REPORTE.md no disponible para este dataset")

        st.subheader("Figuras")
        imgs = list(rd.glob("*.png"))
        if imgs:
            for im in imgs:
                st.image(str(im), caption=im.name)
        else:
            st.info("No se encontraron figuras en el reporte")
