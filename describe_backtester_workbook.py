#!/usr/bin/env python3
"""Décrit la structure du classeur BACKTESTER - modèle format de sortie.xlsx."""

from __future__ import annotations

import argparse
import json
import numbers
from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from openpyxl.utils import get_column_letter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyse les trois premières lignes d'une feuille Excel pour "
            "déduire les sections, sous-sections et colonnes puis imprime un "
            "résumé lisible ou JSON."
        )
    )
    parser.add_argument(
        "workbook",
        type=Path,
        help="Chemin du classeur .xlsx à décrire"
    )
    parser.add_argument(
        "--sheet",
        default="Feuil1",
        help="Nom de la feuille à analyser (défaut: Feuil1)"
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Format de sortie souhaité"
    )
    return parser.parse_args()


def normalize_label(value: Any, fallback: str) -> str:
    if pd.isna(value):
        return fallback
    text = str(value).strip()
    return text or fallback


def infer_dtype(value: Any) -> str:
    if pd.isna(value):
        return "inconnu"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (datetime, date)):
        return "datetime"
    if isinstance(value, numbers.Integral):
        return "entier"
    if isinstance(value, numbers.Real):
        return "flottant" if not float(value).is_integer() else "entier"
    return "texte"


def serialize_sample(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def build_structure(df: pd.DataFrame) -> List[Dict[str, Any]]:
    level0 = df.iloc[0].ffill().fillna("Sans section")
    level1 = df.iloc[1].ffill().fillna("Sans sous-section")
    level2 = df.iloc[2].fillna("")
    data = df.iloc[3:]

    sections: "OrderedDict[str, OrderedDict[str, List[Dict[str, Any]]]]" = OrderedDict()

    for idx in range(df.shape[1]):
        section_name = normalize_label(level0.iloc[idx], "Sans section")
        subsection_name = normalize_label(level1.iloc[idx], "Sans sous-section")
        field_name = normalize_label(level2.iloc[idx], f"Colonne_{idx + 1}")

        column_letter = get_column_letter(idx + 1)
        column_series = data.iloc[:, idx].dropna()
        sample_value = column_series.iloc[0] if not column_series.empty else None
        inferred_type = infer_dtype(sample_value)

        field_info = {
            "name": field_name,
            "column_index": idx + 1,
            "excel_column": column_letter,
            "inferred_type": inferred_type,
            "sample_value": serialize_sample(sample_value),
        }

        sections.setdefault(section_name, OrderedDict())
        sections[section_name].setdefault(subsection_name, []).append(field_info)

    structured: List[Dict[str, Any]] = []
    for section_name, subsections in sections.items():
        section_entry = {
            "name": section_name,
            "field_count": 0,
            "subsections": []
        }
        for subsection_name, fields in subsections.items():
            subsection_entry = {
                "name": subsection_name,
                "field_count": len(fields),
                "fields": fields,
            }
            section_entry["subsections"].append(subsection_entry)
            section_entry["field_count"] += len(fields)
        structured.append(section_entry)
    return structured


def render_text(structure: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for section in structure:
        lines.append(f"{section['name']} ({section['field_count']} colonnes)")
        for subsection in section["subsections"]:
            lines.append(f"  - {subsection['name']} ({subsection['field_count']} colonnes)")
            for field in subsection["fields"]:
                base = (
                    f"      * {field['name']} [col {field['excel_column']}] "
                    f"→ type {field['inferred_type']}"
                )
                sample = field["sample_value"]
                if sample is not None:
                    base += f" — exemple: {sample}"
                lines.append(base)
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    df = pd.read_excel(args.workbook, sheet_name=args.sheet, header=None)
    structure = build_structure(df)

    if args.format == "json":
        print(json.dumps(structure, indent=2, ensure_ascii=False))
    else:
        print(render_text(structure))


if __name__ == "__main__":
    main()
