#!/usr/bin/env python3
"""Génère un fichier Python listant toutes les colonnes de sortie du classeur."""

from __future__ import annotations

import argparse
import textwrap
import unicodedata
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List

import pandas as pd
from openpyxl.utils import get_column_letter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Produit les constantes de position des colonnes.")
    parser.add_argument("workbook", type=Path, help="Classeur à analyser")
    parser.add_argument("output", type=Path, help="Fichier Python de sortie")
    parser.add_argument("--sheet", default="Feuil1", help="Nom de la feuille (défaut: Feuil1)")
    parser.add_argument(
        "--source-name",
        default="REFERENCE_COLUMNS_VALIDATED.csv",
        help="Nom logique de la source utilisée (affiché dans l'entête)"
    )
    return parser.parse_args()


def normalize_label(value, fallback):
    if pd.isna(value):
        return fallback
    text = str(value).strip()
    return text or fallback


def slugify(*parts: str) -> str:
    raw = " ".join(filter(None, parts))
    raw = raw.strip()
    if not raw:
        raw = "colonne"
    normalized = unicodedata.normalize("NFKD", raw)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = ascii_text.replace("&", " and ")
    ascii_text = ascii_text.replace("%", " percent ")
    ascii_text = ascii_text.replace("@", " at ")
    slug = re.sub(r"[^0-9A-Za-z]+", "_", ascii_text)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug.upper() or "COLONNE"


def collect_entries(df: pd.DataFrame) -> List[Dict[str, str]]:
    level0 = df.iloc[0].ffill().fillna("Sans section")
    level1 = df.iloc[1].ffill().fillna("Sans sous-section")
    level2 = df.iloc[2].fillna("")

    entries: List[Dict[str, str]] = []
    slug_counts: Counter[str] = Counter()

    for idx in range(df.shape[1]):
        section = normalize_label(level0.iloc[idx], "Sans section")
        subsection = normalize_label(level1.iloc[idx], "Sans sous-section")
        field = normalize_label(level2.iloc[idx], f"Colonne_{idx + 1}")
        excel_idx = idx + 1
        excel_letter = get_column_letter(excel_idx)
        slug = slugify(subsection, field)
        slug_counts[slug] += 1
        if slug_counts[slug] > 1:
            slug = f"{slug}_{excel_letter}"
        const_name = f"COL_{slug}"
        entries.append(
            {
                "index": excel_idx,
                "python_index": idx,
                "letter": excel_letter,
                "section": section,
                "subsection": subsection,
                "field": field,
                "const_name": const_name,
            }
        )
    return entries


def group_by_subsection(entries: List[Dict[str, str]]):
    blocks: List[Dict[str, object]] = []
    current_key = None
    for entry in entries:
        key = entry["subsection"]
        if key != current_key:
            blocks.append({"name": key, "entries": []})
            current_key = key
        blocks[-1]["entries"].append(entry)
    return blocks


def format_pairs(entries: List[Dict[str, str]], subsection: str) -> List[str]:
    subset = [e for e in entries if e["subsection"] == subsection]
    pairs: List[str] = []
    for i, entry in enumerate(subset[:-1]):
        name = entry["field"].lower()
        if name.startswith("over") and subset[i + 1]["field"].lower().startswith("under"):
            pairs.append(f"{entry['letter']}/{subset[i + 1]['letter']}")
    return pairs


def render(entries: List[Dict[str, str]], source_name: str) -> str:
    total = len(entries)
    first_letter = entries[0]["letter"]
    last_letter = entries[-1]["letter"]
    last_entry = entries[-1]
    max_name = max(len(e["const_name"]) for e in entries)

    header = textwrap.dedent(
        f"""
        # ====================================================================================================
        # MAPPING POSITIONS des {total} COLONNES de sortie
        # ====================================================================================================
        # Total : {total} colonnes ({first_letter} à {last_letter})
        # Source validée : {source_name}
        # ====================================================================================================
        """
    ).strip()

    lines = [header, ""]
    for block in group_by_subsection(entries):
        block_entries = block["entries"]
        start = block_entries[0]["index"]
        end = block_entries[-1]["index"]
        heading = block["name"].upper()
        lines.append(f"# {heading} (Lignes {start}-{end})")
        for entry in block_entries:
            lines.append(
                f"{entry['const_name']:<{max_name}} = {entry['index']:>3}  "
                f"# {entry['letter']} (ligne {entry['index']}, index Python {entry['python_index']}) : "
                f"{entry['subsection']} - {entry['field']}"
            )
        lines.append("")

    live_pairs = format_pairs(entries, "Live Odds (Alert Time)")
    pre_pairs = format_pairs(entries, "Pre-Match Odds")

    notes = textwrap.dedent(
        f"""
        # ====================================================================================================
        # NOTES IMPORTANTES
        # ====================================================================================================
        # 1. Numérotation : les constantes utilisent la ligne CSV (1-{total}), pas l'index Python (0-{total - 1})
        # 2. Accès : utiliser df.iloc[COL_xxx - 1] pour cibler une colonne
        # 3. Pattern OVER/UNDER : alternance détectée
        #    - LIVE : {', '.join(live_pairs) if live_pairs else 'aucun pattern détecté'}
        #    - PRE-MATCH : {', '.join(pre_pairs) if pre_pairs else 'aucun pattern détecté'}
        # 4. Total colonnes : {total} (de {first_letter} à {last_letter})
        # 5. Dernière colonne : {last_letter} (ligne {last_entry['index']}) = {last_entry['subsection']} - {last_entry['field']}
        # 6. Sous-sections recensées : {', '.join(dict.fromkeys(e['subsection'] for e in entries))}
        # ====================================================================================================
        """
    ).strip()

    lines.append(notes)
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    df = pd.read_excel(args.workbook, sheet_name=args.sheet, header=None)
    entries = collect_entries(df)
    content = render(entries, args.source_name)
    args.output.write_text(content + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
