#!/usr/bin/env python3
"""collect_datasets.py

Script minimalista con conectores "stub" para permitir pruebas offline.
Provee comandos: search, list, get

Este archivo implementa las clases solicitadas con comportamiento simulado
para poder validar el flujo sin depender de API keys ni red.
"""
import argparse
import json
import os
import csv
from pathlib import Path
from datetime import datetime


class BaseConnector:
    def __init__(self):
        pass

    def search(self, q, limit=5):
        raise NotImplementedError()

    def list(self):
        raise NotImplementedError()

    def get(self, dataset_id, dest):
        raise NotImplementedError()


class StubConnector(BaseConnector):
    """Conector simulado que devuelve resultados de ejemplo."""
    def __init__(self, source_name):
        self.source_name = source_name

    def search(self, q, limit=5):
        results = []
        for i in range(1, limit + 1):
            results.append({
                "id": f"{self.source_name.lower()}_{i}",
                "source": self.source_name,
                "title": f"{self.source_name} sample dataset {i} ({q})",
                "description": f"Ejemplo de dataset {i} relacionado con {q}.",
                "url": f"https://example.org/{self.source_name.lower()}/{i}",
            })
        return results

    def list(self):
        return [f"{self.source_name}_dataset_1", f"{self.source_name}_dataset_2"]

    def get(self, dataset_id, dest):
        # For FAOSTAT QCL produce a small CSV sample
        dest_path = Path(dest)
        dest_path.mkdir(parents=True, exist_ok=True)
        if self.source_name.upper() == "FAOSTAT" and dataset_id.upper().startswith("QCL"):
            filename = dest_path / f"faostat_{dataset_id}.csv"
            rows = [
                ["Area", "Item", "Year", "Value"],
                ["Colombia", "Maize", 2018, 12345.0],
                ["Colombia", "Maize", 2019, 13000.0],
                ["Colombia", "Maize", 2020, 12500.0],
                ["Colombia", "Maize", 2021, 14000.0],
            ]
            with open(filename, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            return str(filename)
        else:
            # Generic stub CSV
            filename = dest_path / f"{self.source_name.lower()}_{dataset_id}.csv"
            with open(filename, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["col1", "col2", "col3"])
                for i in range(5):
                    writer.writerow([f"r{i}_a", f"r{i}_b", i])
            return str(filename)


CONNECTORS = {
    "SOCRATA": StubConnector("SOCRATA"),
    "FAOSTAT": StubConnector("FAOSTAT"),
    "WORLD_BANK": StubConnector("WORLD_BANK"),
    "HDX": StubConnector("HDX"),
    "OECD": StubConnector("OECD"),
}


def run_search(source, q, limit, out_path):
    results = []
    sources = []
    if source is None or source.upper() == "ALL":
        sources = list(CONNECTORS.keys())
    else:
        sources = [source.upper()]

    for s in sources:
        connector = CONNECTORS.get(s)
        if connector:
            results.extend(connector.search(q, limit=limit))

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"query": q, "generated_at": datetime.utcnow().isoformat(), "results": results}, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(results)} results to {out_path}")
    return results


def run_get(source, dataset_id, dest):
    s = source.upper()
    connector = CONNECTORS.get(s)
    if not connector:
        raise ValueError(f"Unknown source: {source}")
    path = connector.get(dataset_id, dest)
    print(f"Downloaded dataset to: {path}")
    # Try to show first 5 rows with pandas if available
    try:
        import pandas as pd
        df = pd.read_csv(path)
        print(df.head(5).to_string(index=False))
    except Exception:
        print("pandas no disponible o fallo al leer CSV; mostrando primeras líneas del archivo:")
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i >= 6:
                    break
                print(line.strip())


def main():
    parser = argparse.ArgumentParser(description="Collect datasets from various connectors (stubbed).")
    sub = parser.add_subparsers(dest="cmd")

    p_search = sub.add_parser("search", help="Search datasets")
    p_search.add_argument("--source", default="ALL", help="Source name or ALL")
    p_search.add_argument("--q", required=True, help="Query term")
    p_search.add_argument("--limit", type=int, default=3)
    p_search.add_argument("--out", default="data/raw/catalogo.json", help="Output JSON path")

    p_list = sub.add_parser("list", help="List datasets for a source")
    p_list.add_argument("source", help="Source name")

    p_get = sub.add_parser("get", help="Download a dataset (stub)")
    p_get.add_argument("--source", required=True)
    p_get.add_argument("--id", required=True, dest="dataset_id")
    p_get.add_argument("--dest", default="data/raw/", help="Destination directory")

    args = parser.parse_args()
    if args.cmd == "search":
        run_search(args.source, args.q, args.limit, args.out)
    elif args.cmd == "list":
        s = args.source.upper()
        connector = CONNECTORS.get(s)
        if not connector:
            print(f"Unknown source {args.source}")
        else:
            for item in connector.list():
                print(item)
    elif args.cmd == "get":
        run_get(args.source, args.dataset_id, args.dest)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
