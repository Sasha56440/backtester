#!/usr/bin/env python3
"""
Génère une description structurée du dépôt
https://github.com/Sasha56440/noms-des-colonnes.

Le script lit le fichier CSV principal, calcule des métriques
simplifiées pour chaque colonne (type détecté, nombre de valeurs
distinctes, valeurs manquantes, exemples) et restitue le tout
au format Markdown (par défaut) ou JSON.
"""
from __future__ import annotations

import argparse
import json
import csv
from collections import OrderedDict
from itertools import zip_longest
from pathlib import Path
from typing import Dict, Iterable, List


REPO_DIR = Path(__file__).resolve().parent
DEFAULT_CSV = (
    REPO_DIR
    / "noms-des-colonnes"
    / "BACKTESTER - modèle format de sortie.csv"
)


COLUMN_DESCRIPTIONS: Dict[str, str] = {
    "Date": "Horodatage de la ligne (JJ/MM/AAAA HH:MM).",
    "Home": "Nom de l'équipe à domicile.",
    "Away": "Nom de l'équipe à l'extérieur.",
    "HT_H": "Buts domicile à la mi-temps (Half-Time Home).",
    "HT_A": "Buts extérieur à la mi-temps (Half-Time Away).",
    "FT_H": "Buts domicile fin de match (Full-Time Home).",
    "FT_A": "Buts extérieur fin de match (Full-Time Away).",
    "1MT/2MT": (
        "Indice numérique comparant l'intensité entre le premier et le "
        "second segment de match ; le suffixe '+' souligne une intensité "
        "supérieure au palier annoncé."
    ),
    "1MT⇔2MT": (
        "Etiquette qualitative résumant la relation entre 1re et 2e période "
        "(>, < ou =)."
    ),
    "Fav/Und 1MT": (
        "Etat du duel Favori vs Underdog sur la 1re période "
        "(Fav>Und, Fav<Und, Fav=Und, Equilibre)."
    ),
    "Fav/Und 2MT": (
        "Etat Favori vs Underdog sur la 2e période (même codification)."
    ),
    "Fav/Und Total": (
        "Bilan Favori vs Underdog sur l'ensemble du match."
    ),
    "H/A 1MT": (
        "Comparaison Home vs Away en 1re période (H>A, H<A, H=A)."
    ),
    "H/A 2MT": (
        "Comparaison Home vs Away en 2e période."
    ),
    "H/A Total": (
        "Comparaison Home vs Away sur l'ensemble du match."
    ),
    "Dif H/A 1MT": (
        "Amplitude du différentiel Home/Away en 1re période (Dif0, Dif1, "
        "Dif2, Dif4+)."
    ),
    "Dif H/A 2MT": "Amplitude du différentiel Home/Away en 2e période.",
    "Dif H/A Total": (
        "Amplitude du différentiel Home/Away sur tout le match."
    ),
    "Dif Fav/Und 1MT": (
        "Amplitude du différentiel Favori/Underdog en 1re période."
    ),
    "Dif Fav/Und 2MT": (
        "Amplitude du différentiel Favori/Underdog en 2e période."
    ),
    "Dif Fav/Und Total": (
        "Amplitude du différentiel Favori/Underdog sur tout le match."
    ),
    "F/U@H/A": (
        "Combinaison compacte des vainqueurs 'Fav vs Und' et 'Home vs Away' "
        "(`EQ`, `F@H`, `F@A`, ...)."
    ),
    "Sum 1MT": (
        "Buts totaux inscrits durant la 1re période (HT_H + HT_A)."
    ),
    "Sum 2MT": (
        "Buts totaux inscrits durant la 2e période "
        "((FT_H - HT_H) + (FT_A - HT_A))."
    ),
    "Sum Total": (
        "Total de buts du match (FT_H + FT_A)."
    ),
}


def _detect_type(value: str) -> str:
    """Détecte grossièrement le type d'une valeur textuelle."""
    try:
        int(value)
        return "int"
    except ValueError:
        pass
    try:
        float(value)
        return "float"
    except ValueError:
        pass
    return "str"


def _format_type(types: Iterable[str]) -> str:
    """Retourne une représentation textuelle du type dominant."""
    unique_types = sorted(set(types))
    if not unique_types:
        return "vide"
    if len(unique_types) == 1:
        return unique_types[0]
    return " / ".join(unique_types)


def dataframe_summary(csv_path: Path) -> Dict[str, object]:
    """Analyse le CSV ciblé et retourne la synthèse complète."""
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Impossible de trouver le fichier CSV '{csv_path}'."
        )

    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=";")
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError("Le fichier CSV est vide.") from exc

        stats: OrderedDict[str, Dict[str, object]] = OrderedDict(
            (
                column,
                {
                    "distinct": set(),
                    "missing": 0,
                    "examples": [],
                    "types": [],
                },
            )
            for column in header
        )

        row_count = 0
        for row in reader:
            row_count += 1
            for column, raw_value in zip_longest(
                header, row, fillvalue=""
            ):
                value = (raw_value or "").strip()
                column_stats = stats[column]
                if value == "":
                    column_stats["missing"] += 1
                    continue
                column_stats["distinct"].add(value)
                if (
                    value not in column_stats["examples"]
                    and len(column_stats["examples"]) < 3
                ):
                    column_stats["examples"].append(value)
                column_stats["types"].append(_detect_type(value))

    details: List[Dict[str, object]] = []
    for idx, (column, meta) in enumerate(stats.items(), start=1):
        description = COLUMN_DESCRIPTIONS.get(
            column, "Description indisponible (colonne non documentée)."
        )
        dtype = _format_type(meta["types"])
        details.append(
            {
                "index": idx,
                "column": column,
                "description": description,
                "dtype": dtype,
                "distinct_values": len(meta["distinct"]),
                "missing_values": meta["missing"],
                "examples": meta["examples"],
            }
        )

    summary = {
        "csv_path": str(csv_path),
        "rows": row_count,
        "columns": len(header),
        "columns_detail": details,
    }
    return summary


def to_markdown(summary: Dict[str, object]) -> str:
    """Formate la synthèse en Markdown lisible."""
    header = [
        "# Description du dépôt `noms-des-colonnes`",
        "",
        f"- Fichier source : `{summary['csv_path']}`",
        f"- Lignes : {summary['rows']}",
        f"- Colonnes : {summary['columns']}",
        "",
        "| # | Colonne | Description | Type détecté | Distincts | Exemples | Manquants |",
        "|---|---------|-------------|-------------|-----------|----------|-----------|",
    ]

    body_lines: List[str] = []
    for entry in summary["columns_detail"]:
        examples = ", ".join(entry["examples"]) if entry["examples"] else "—"
        line = (
            f"| {entry['index']} | {entry['column']} | "
            f"{entry['description']} | {entry['dtype']} | "
            f"{entry['distinct_values']} | {examples} | "
            f"{entry['missing_values']} |"
        )
        body_lines.append(line)
    return "\n".join(header + body_lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Décrit précisément les colonnes du dépôt "
            "'noms-des-colonnes'."
        )
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help="Chemin vers le CSV à décrire (séparateur ';').",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Format de sortie souhaité.",
    )
    args = parser.parse_args()

    summary = dataframe_summary(args.csv)
    if args.format == "json":
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(to_markdown(summary))


if __name__ == "__main__":
    main()
