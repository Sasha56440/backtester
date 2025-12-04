#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PARAMETRES.PY - Version Universelle
✅ Détection automatique du type de fichier
✅ Support de TOUS les formats de datasets courants
✅ Détection automatique de la structure des colonnes
✅ Compatible avec n'importe quel dataset
"""

import pandas as pd
import numpy as np
import sys
import os
import glob
from datetime import datetime
import re
import csv
import json
import warnings
warnings.filterwarnings('ignore')

# ====================================================================================================
# DÉTECTION UNIVERSELLE DE FICHIERS
# ====================================================================================================

def detecter_type_fichier(filepath):
    """Détecte le type de fichier par extension et validation du contenu"""
    extension = os.path.splitext(filepath)[1].lower()
    
    types_supportes = {
        '.csv': 'csv',
        '.tsv': 'tsv',
        '.txt': 'text',
        '.xls': 'excel',
        '.xlsx': 'excel',
        '.xlsm': 'excel',
        '.xlsb': 'excel',
        '.json': 'json',
        '.jsonl': 'jsonlines',
        '.parquet': 'parquet',
        '.feather': 'feather',
        '.pkl': 'pickle',
        '.pickle': 'pickle',
        '.h5': 'hdf5',
        '.hdf': 'hdf5',
        '.hdf5': 'hdf5',
        '.sav': 'spss',
        '.dta': 'stata',
        '.sas7bdat': 'sas',
        '.xml': 'xml',
        '.html': 'html',
        '.orc': 'orc',
        '.msgpack': 'msgpack'
    }
    
    if extension in types_supportes:
        return types_supportes[extension]
    
    # Essayer de détecter par contenu si extension inconnue
    return detecter_par_contenu(filepath)

def detecter_par_contenu(filepath):
    """Détecte le type par analyse du contenu"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(1024)
            
        # Parquet
        if header.startswith(b'PAR1'):
            return 'parquet'
        
        # Excel
        if header.startswith(b'\xd0\xcf\x11\xe0'):
            return 'excel'
        if header.startswith(b'PK'):
            return 'excel'
        
        # JSON
        try:
            text = header.decode('utf-8', errors='ignore')
            if text.strip().startswith(('{', '[')):
                return 'json'
        except:
            pass
        
        # CSV/TSV par défaut
        return 'csv'
    except:
        return 'csv'

# ====================================================================================================
# LECTEURS UNIVERSELS
# ====================================================================================================

def lire_csv_universel(filepath):
    """Lit un CSV/TSV avec détection automatique du format"""
    
    # Vérifier d'abord si c'est un fichier LG70 avec guillemets doubles problématiques
    nom_fichier = os.path.basename(filepath).lower()
    is_lg70 = 'lg' in nom_fichier and '70' in nom_fichier
    
    # Ordre de priorité des délimiteurs
    delimiteurs_possibles = [',', ';', '\t', '|', ':', ' ']
    
    # Lire un échantillon pour analyser
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lignes = []
        for i, line in enumerate(f):
            lignes.append(line)
            if i >= 20:  # Lire les 20 premières lignes
                break
    
    if not lignes:
        raise ValueError("Fichier vide")
    
    # Si c'est un fichier LG70 et qu'on détecte des guillemets doubles bizarres
    if is_lg70 and '""' in lignes[0]:
        print("  🔧 Format LG70 avec guillemets doubles détecté - nettoyage...")
        # Nettoyer les guillemets doubles excessifs
        lignes_clean = []
        for ligne in lignes:
            # Remplacer les guillemets doubles par rien sauf en début/fin
            ligne_clean = ligne.replace('""', '').strip()
            if ligne_clean.startswith('"') and ligne_clean.endswith('"'):
                ligne_clean = ligne_clean[1:-1]
            lignes_clean.append(ligne_clean)
        lignes = lignes_clean
    
    # Détection intelligente du délimiteur
    meilleur_delim = None
    max_colonnes = 0
    consistance_max = 0
    
    for delim in delimiteurs_possibles:
        # Compter le nombre de colonnes pour chaque ligne
        nb_colonnes_par_ligne = []
        for ligne in lignes[1:min(11, len(lignes))]:  # Ignorer la première ligne (souvent header groupé)
            nb_colonnes_par_ligne.append(len(ligne.split(delim)))
        
        if nb_colonnes_par_ligne:
            # Vérifier la consistance
            mode_colonnes = max(set(nb_colonnes_par_ligne), key=nb_colonnes_par_ligne.count)
            consistance = nb_colonnes_par_ligne.count(mode_colonnes) / len(nb_colonnes_par_ligne)
            
            # Favoriser 119 colonnes pour les fichiers LG70
            if is_lg70 and mode_colonnes == 119:
                meilleur_delim = delim
                max_colonnes = mode_colonnes
                break
            
            # Sinon prendre le meilleur
            if mode_colonnes > max_colonnes or (mode_colonnes == max_colonnes and consistance > consistance_max):
                max_colonnes = mode_colonnes
                consistance_max = consistance
                meilleur_delim = delim
    
    sep = meilleur_delim or ','
    
    # Détection de l'encoding
    encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            # Traitement spécial pour LG70
            if is_lg70 and max_colonnes == 119:
                # Lire avec traitement spécial des guillemets
                df = pd.read_csv(
                    filepath,
                    sep=sep,
                    encoding=encoding,
                    skiprows=0,  # Garder la première ligne pour analyse
                    header=None,  # Pas de header automatique
                    low_memory=False,
                    quoting=csv.QUOTE_MINIMAL,
                    doublequote=True,
                    on_bad_lines='warn'
                )
                
                # Si on a bien 119 colonnes après la ligne d'en-tête
                if len(df.columns) == 119:
                    # La première ligne contient les groupes, la deuxième les noms
                    if len(df) > 1:
                        # Créer les noms de colonnes à partir de la ligne 2
                        col_names = df.iloc[1].astype(str).str.strip()
                        col_names = [col.replace('""', '').replace('"', '').strip() for col in col_names]
                        df.columns = col_names
                        # Supprimer les 2 premières lignes (groupes et noms)
                        df = df.iloc[2:].reset_index(drop=True)
                    
                    print(f"  ✅ CSV LG70 lu : {len(df)} lignes, {len(df.columns)} colonnes")
                    print(f"     • Format LG70 standard détecté")
                    print(f"     • Délimiteur: '{sep}'")
                    print(f"     • Encoding: {encoding}")
                    return df
            
            # Lecture standard pour autres fichiers
            skiprows = 0 if is_lg70 else None
            header = None if is_lg70 else 'infer'
            
            df = pd.read_csv(
                filepath, 
                sep=sep, 
                encoding=encoding,
                header=header,
                skiprows=skiprows,
                low_memory=False,
                na_values=['', 'NA', 'N/A', 'null', 'NULL', 'None'],
                keep_default_na=True,
                on_bad_lines='warn'
            )
            
            # Pour LG70, traiter les headers spéciaux
            if is_lg70 and len(df.columns) > 100:
                # Si première ligne contient des headers, l'utiliser
                if not pd.api.types.is_numeric_dtype(df.iloc[0, 0]):
                    col_names = df.iloc[0].astype(str).str.strip()
                    col_names = [col.replace('""', '').replace('"', '').strip() for col in col_names]
                    df.columns = col_names
                    df = df.iloc[1:].reset_index(drop=True)
            
            if len(df.columns) > 1:
                print(f"  ✅ CSV lu : {len(df)} lignes, {len(df.columns)} colonnes")
                print(f"     • Délimiteur: '{sep}'")
                print(f"     • Encoding: {encoding}")
                return df
                
        except Exception as e:
            continue
    
    # Dernier essai avec détection automatique
    try:
        df = pd.read_csv(filepath, sep=None, engine='python')
        print(f"  ✅ CSV lu avec détection automatique pandas")
        print(f"     • {len(df)} lignes, {len(df.columns)} colonnes")
        return df
    except:
        raise ValueError(f"Impossible de lire le CSV: {filepath}")

def lire_excel_universel(filepath):
    """Lit un fichier Excel avec détection automatique des feuilles"""
    try:
        # Lister toutes les feuilles
        xl_file = pd.ExcelFile(filepath)
        sheets = xl_file.sheet_names
        
        print(f"  📊 Fichier Excel avec {len(sheets)} feuille(s)")
        
        if len(sheets) == 1:
            df = pd.read_excel(filepath, sheet_name=0)
            print(f"  ✅ Feuille '{sheets[0]}' lue : {len(df)} lignes")
        else:
            # Si plusieurs feuilles, prendre la plus grande ou demander
            dfs = {}
            for sheet in sheets:
                try:
                    dfs[sheet] = pd.read_excel(filepath, sheet_name=sheet)
                    print(f"     • {sheet}: {len(dfs[sheet])} lignes")
                except:
                    continue
            
            # Prendre la feuille avec le plus de données
            if dfs:
                sheet_max = max(dfs.keys(), key=lambda k: len(dfs[k]) * len(dfs[k].columns))
                df = dfs[sheet_max]
                print(f"  ➜ Feuille sélectionnée: '{sheet_max}'")
            else:
                raise ValueError("Aucune feuille lisible")
        
        return df
    except Exception as e:
        raise ValueError(f"Erreur lecture Excel: {e}")

def lire_json_universel(filepath):
    """Lit un fichier JSON avec détection automatique de la structure"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Si c'est une liste de dictionnaires
        if isinstance(data, list):
            df = pd.DataFrame(data)
        # Si c'est un dictionnaire avec des listes
        elif isinstance(data, dict):
            # Essayer de créer un DataFrame
            try:
                df = pd.DataFrame(data)
            except:
                # Peut-être un format nested
                df = pd.json_normalize(data)
        else:
            raise ValueError("Format JSON non supporté")
        
        print(f"  ✅ JSON lu : {len(df)} lignes, {len(df.columns)} colonnes")
        return df
    except Exception as e:
        raise ValueError(f"Erreur lecture JSON: {e}")

def lire_jsonlines_universel(filepath):
    """Lit un fichier JSON Lines"""
    try:
        df = pd.read_json(filepath, lines=True)
        print(f"  ✅ JSON Lines lu : {len(df)} lignes")
        return df
    except Exception as e:
        raise ValueError(f"Erreur lecture JSON Lines: {e}")

def lire_parquet_universel(filepath):
    """Lit un fichier Parquet"""
    try:
        df = pd.read_parquet(filepath)
        print(f"  ✅ Parquet lu : {len(df)} lignes")
        return df
    except Exception as e:
        # Essayer avec pyarrow si disponible
        try:
            import pyarrow.parquet as pq
            table = pq.read_table(filepath)
            df = table.to_pandas()
            print(f"  ✅ Parquet lu (pyarrow) : {len(df)} lignes")
            return df
        except:
            raise ValueError(f"Erreur lecture Parquet: {e}")

def lire_pickle_universel(filepath):
    """Lit un fichier Pickle"""
    try:
        df = pd.read_pickle(filepath)
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)
        print(f"  ✅ Pickle lu : {len(df)} lignes")
        return df
    except Exception as e:
        raise ValueError(f"Erreur lecture Pickle: {e}")

def lire_feather_universel(filepath):
    """Lit un fichier Feather"""
    try:
        df = pd.read_feather(filepath)
        print(f"  ✅ Feather lu : {len(df)} lignes")
        return df
    except Exception as e:
        raise ValueError(f"Erreur lecture Feather: {e}")

def lire_hdf5_universel(filepath):
    """Lit un fichier HDF5"""
    try:
        # Essayer de lire la première clé
        with pd.HDFStore(filepath, 'r') as store:
            keys = store.keys()
            if keys:
                df = store[keys[0]]
                print(f"  ✅ HDF5 lu (clé: {keys[0]}) : {len(df)} lignes")
            else:
                raise ValueError("Fichier HDF5 vide")
        return df
    except Exception as e:
        raise ValueError(f"Erreur lecture HDF5: {e}")

def lire_stata_universel(filepath):
    """Lit un fichier Stata (.dta)"""
    try:
        df = pd.read_stata(filepath)
        print(f"  ✅ Stata lu : {len(df)} lignes")
        return df
    except Exception as e:
        raise ValueError(f"Erreur lecture Stata: {e}")

def lire_spss_universel(filepath):
    """Lit un fichier SPSS (.sav)"""
    try:
        df = pd.read_spss(filepath)
        print(f"  ✅ SPSS lu : {len(df)} lignes")
        return df
    except Exception as e:
        raise ValueError(f"Erreur lecture SPSS: {e}")

def lire_sas_universel(filepath):
    """Lit un fichier SAS (.sas7bdat)"""
    try:
        df = pd.read_sas(filepath)
        print(f"  ✅ SAS lu : {len(df)} lignes")
        return df
    except Exception as e:
        raise ValueError(f"Erreur lecture SAS: {e}")

def lire_html_universel(filepath):
    """Lit des tableaux depuis un fichier HTML"""
    try:
        dfs = pd.read_html(filepath)
        if dfs:
            # Prendre le plus grand tableau
            df = max(dfs, key=lambda x: len(x) * len(x.columns))
            print(f"  ✅ HTML lu : {len(df)} lignes (tableau principal)")
            return df
        else:
            raise ValueError("Aucun tableau trouvé dans le HTML")
    except Exception as e:
        raise ValueError(f"Erreur lecture HTML: {e}")

def lire_xml_universel(filepath):
    """Lit un fichier XML"""
    try:
        df = pd.read_xml(filepath)
        print(f"  ✅ XML lu : {len(df)} lignes")
        return df
    except Exception as e:
        raise ValueError(f"Erreur lecture XML: {e}")

def lire_orc_universel(filepath):
    """Lit un fichier ORC"""
    try:
        import pyarrow.orc as orc
        table = orc.read_table(filepath)
        df = table.to_pandas()
        print(f"  ✅ ORC lu : {len(df)} lignes")
        return df
    except Exception as e:
        raise ValueError(f"Erreur lecture ORC: {e}")


def rendre_colonnes_uniques(colonnes):
    """Assainit et déduplique les noms de colonnes"""
    occurrences = {}
    colonnes_uniques = []
    for col in colonnes:
        nom = str(col).strip()
        if nom in occurrences:
            occurrences[nom] += 1
            colonnes_uniques.append(f"{nom}.{occurrences[nom]}")
        else:
            occurrences[nom] = 0
            colonnes_uniques.append(nom)
    return colonnes_uniques

# ====================================================================================================
# LECTEUR UNIVERSEL PRINCIPAL
# ====================================================================================================

def lire_dataset_universel(filepath):
    """Fonction principale pour lire n'importe quel type de dataset"""
    
    print(f"\n📁 Lecture du fichier : {os.path.basename(filepath)}")
    
    # Détecter le type de fichier
    file_type = detecter_type_fichier(filepath)
    print(f"  🔍 Type détecté : {file_type}")
    
    # Mapper vers la fonction de lecture appropriée
    lecteurs = {
        'csv': lire_csv_universel,
        'tsv': lire_csv_universel,
        'text': lire_csv_universel,
        'excel': lire_excel_universel,
        'json': lire_json_universel,
        'jsonlines': lire_jsonlines_universel,
        'parquet': lire_parquet_universel,
        'pickle': lire_pickle_universel,
        'feather': lire_feather_universel,
        'hdf5': lire_hdf5_universel,
        'stata': lire_stata_universel,
        'spss': lire_spss_universel,
        'sas': lire_sas_universel,
        'html': lire_html_universel,
        'xml': lire_xml_universel,
        'orc': lire_orc_universel
    }
    
    if file_type in lecteurs:
        try:
            df = lecteurs[file_type](filepath)
            df = df.copy()
            df.columns = rendre_colonnes_uniques(df.columns)
            return df, file_type
        except Exception as e:
            print(f"  ⚠️ Erreur avec le lecteur {file_type}: {e}")
            # Essayer CSV par défaut
            print("  🔄 Tentative avec lecteur CSV par défaut...")
            try:
                df = lire_csv_universel(filepath)
                df = df.copy()
                df.columns = rendre_colonnes_uniques(df.columns)
                return df, 'csv'
            except:
                raise ValueError(f"Impossible de lire le fichier: {filepath}")
    else:
        # Type inconnu, essayer CSV
        print("  ℹ️ Type inconnu, tentative CSV...")
        df = lire_csv_universel(filepath)
        df = df.copy()
        df.columns = rendre_colonnes_uniques(df.columns)
        return df, 'csv'

# ====================================================================================================
# ANALYSE AUTOMATIQUE DE LA STRUCTURE
# ====================================================================================================

def analyser_structure_dataset(df):
    """Analyse la structure d'un dataset pour identifier les types de colonnes"""
    
    print("\n📊 Analyse de la structure du dataset...")
    
    structure = {
        'nb_lignes': len(df),
        'nb_colonnes': len(df.columns),
        'colonnes': {},
        'types_detectes': {
            'dates': [],
            'numeriques': [],
            'texte': [],
            'categoriques': [],
            'booleens': [],
            'mixtes': []
        }
    }
    
    for idx, col in enumerate(df.columns):
        serie = df.iloc[:, idx]
        col_info = {
            'nom': col,
            'type_pandas': str(serie.dtype),
            'valeurs_uniques': serie.nunique(dropna=False),
            'valeurs_nulles': serie.isnull().sum(),
            'taux_remplissage': (1 - serie.isnull().sum() / len(df)) * 100
        }
        
        # Détection du type réel
        if pd.api.types.is_datetime64_any_dtype(serie):
            col_info['type_reel'] = 'date'
            structure['types_detectes']['dates'].append(col)
        elif pd.api.types.is_bool_dtype(serie):
            col_info['type_reel'] = 'booleen'
            structure['types_detectes']['booleens'].append(col)
        elif pd.api.types.is_numeric_dtype(serie):
            col_info['type_reel'] = 'numerique'
            structure['types_detectes']['numeriques'].append(col)
        else:
            # Analyser plus en détail les colonnes non-numériques
            try:
                # Essayer de convertir en numérique
                pd.to_numeric(serie, errors='raise')
                col_info['type_reel'] = 'numerique_texte'
                structure['types_detectes']['numeriques'].append(col)
            except:
                # Vérifier si c'est une date
                try:
                    pd.to_datetime(serie, errors='raise')
                    col_info['type_reel'] = 'date_texte'
                    structure['types_detectes']['dates'].append(col)
                except:
                    # Catégorique si peu de valeurs uniques
                    if col_info['valeurs_uniques'] < len(df) * 0.05:  # Moins de 5% de valeurs uniques
                        col_info['type_reel'] = 'categorique'
                        structure['types_detectes']['categoriques'].append(col)
                    else:
                        col_info['type_reel'] = 'texte'
                        structure['types_detectes']['texte'].append(col)
        
        structure['colonnes'][col] = col_info
    
    # Afficher le résumé
    print(f"  • Lignes : {structure['nb_lignes']:,}")
    print(f"  • Colonnes : {structure['nb_colonnes']}")
    print(f"\n  📈 Types de colonnes détectés :")
    print(f"     • Dates : {len(structure['types_detectes']['dates'])}")
    print(f"     • Numériques : {len(structure['types_detectes']['numeriques'])}")
    print(f"     • Catégoriques : {len(structure['types_detectes']['categoriques'])}")
    print(f"     • Texte : {len(structure['types_detectes']['texte'])}")
    print(f"     • Booléens : {len(structure['types_detectes']['booleens'])}")
    
    return structure

# ====================================================================================================
# TRAITEMENT INTELLIGENT
# ====================================================================================================

def detecter_colonnes_betting(df, structure):
    """Détecte si le dataset contient des colonnes de betting/sports"""
    
    mots_cles_betting = [
        'home', 'away', 'score', 'odd', 'cote', 'bet', 'stake',
        'momentum', 'xg', 'corner', 'attack', 'card', 'penalty',
        'possession', 'shot', 'goal', 'team', 'match', 'game',
        'league', 'timer', 'strike', 'sot', 'soff', 'btts',
        'over', 'under', 'draw', '3-way', 'double chance'
    ]
    
    # Vérification spéciale pour le dataset LG70 à 119 colonnes
    if len(df.columns) == 119:
        print(f"\n  🎯 Dataset LG70 BETTING (119 colonnes) détecté")
        print(f"     • Format reconnu : InPlayGuru / Backtesting")
        return True, list(df.columns)
    
    colonnes_betting = []
    for col in df.columns:
        col_lower = str(col).lower()
        if any(mot in col_lower for mot in mots_cles_betting):
            colonnes_betting.append(col)
    
    # Si on a plus de 10% des colonnes qui matchent, c'est du betting
    if len(colonnes_betting) > len(df.columns) * 0.1:
        print(f"\n  🎯 Dataset de type BETTING/SPORTS détecté")
        print(f"     • {len(colonnes_betting)} colonnes betting sur {len(df.columns)}")
        return True, colonnes_betting
    
    return False, []

def traiter_dataset_generique(df, structure):
    """Traitement générique pour tout dataset"""
    
    print("\n🔧 Traitement du dataset...")
    
    # Nettoyer les colonnes dates
    for col_date in structure['types_detectes']['dates']:
        try:
            df[col_date] = pd.to_datetime(df[col_date], errors='coerce')
            print(f"  ✅ Colonne '{col_date}' convertie en datetime")
        except:
            pass
    
    # Nettoyer les colonnes numériques
    for col_num in structure['types_detectes']['numeriques']:
        try:
            df[col_num] = pd.to_numeric(df[col_num], errors='coerce')
        except:
            pass
    
    # Encoder les colonnes catégoriques si nécessaire
    for col_cat in structure['types_detectes']['categoriques']:
        if df[col_cat].dtype == 'object':
            df[f'{col_cat}_encoded'] = pd.Categorical(df[col_cat]).codes
            print(f"  ✅ Colonne '{col_cat}' encodée")
    
    return df

def traiter_dataset_betting(df, structure, colonnes_betting):
    """Traitement spécialisé pour les datasets de betting"""
    
    print("\n⚽ Traitement spécialisé BETTING...")
    
    # Détection du format LG70 à 119 colonnes
    if len(df.columns) == 119:
        print("  📊 Format LG70 détecté - Application du traitement spécialisé")
        
        # Renommer les colonnes selon le mapping standard si elles sont numériques
        if all(isinstance(col, (int, float)) or str(col).isdigit() for col in df.columns[:10]):
            print("  🔄 Renommage des colonnes selon le mapping LG70...")
            df = renommer_colonnes_lg70(df)
        
        # Calcul Fav/Und si on trouve les colonnes de cotes pre-match
        cotes_cols = [col for col in df.columns if 'Pre-Match' in str(col) and '3-Way' in str(col)]
        if len(cotes_cols) >= 2:
            print("  📈 Calcul des colonnes Fav/Und...")
            df = calculer_fav_und_lg70(df)
    else:
        # Chercher les colonnes de cotes pour tout autre format
        colonnes_cotes = [col for col in colonnes_betting if 'odd' in str(col).lower() or 'cote' in str(col).lower()]
        
        if len(colonnes_cotes) >= 2:
            print(f"  📊 {len(colonnes_cotes)} colonnes de cotes trouvées")
            # Possibilité d'implémenter un calcul Fav/Und générique
    
    # Conversion des colonnes numériques au format européen
    print("  🔧 Conversion au format européen (virgule décimale)...")
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # Ne pas toucher aux colonnes qui ressemblent à des IDs ou des positions
            if not any(x in str(col).lower() for x in ['id', 'pos', 'position', 'index']):
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                except:
                    pass
    
    # Traitement générique aussi
    df = traiter_dataset_generique(df, structure)
    
    return df

def renommer_colonnes_lg70(df):
    """Renomme les colonnes du format LG70 standard"""
    noms_colonnes = {
        0: 'Match Data_Date', 1: 'Match Data_Timer', 2: 'Match Data_Strike',
        3: 'Match Data_Region', 4: 'Match Data_League', 5: 'Match Data_Home',
        6: 'Match Data_Away', 7: 'Match Data_Home Pos', 8: 'Match Data_Away Pos',
        # Alert Time Stats (9-32)
        9: 'Alert Time Stats-H Score', 10: 'Alert Time Stats-A Score',
        11: 'Alert Time Stats-H Momentum', 12: 'Alert Time Stats-A Momentum',
        13: 'Alert Time Stats-H xG', 14: 'Alert Time Stats-A xG',
        15: 'Alert Time Stats-H SOT', 16: 'Alert Time Stats-A SOT',
        17: 'Alert Time Stats-H SOFF', 18: 'Alert Time Stats-A SOFF',
        19: 'Alert Time Stats-H Corners', 20: 'Alert Time Stats-A Corners',
        21: 'Alert Time Stats-H Attacks', 22: 'Alert Time Stats-A Attacks',
        23: 'Alert Time Stats-H Dn Attacks', 24: 'Alert Time Stats-A Dn Attacks',
        25: 'Alert Time Stats-H Poss %', 26: 'Alert Time Stats-A Poss %',
        27: 'Alert Time Stats-H Y Cards', 28: 'Alert Time Stats-A Y Cards',
        29: 'Alert Time Stats-H R Cards', 30: 'Alert Time Stats-A R Cards',
        31: 'Alert Time Stats-H Penalties', 32: 'Alert Time Stats-A Penalties',
        # Half Time Stats (33-56)
        33: 'Half Time Stats-H Score', 34: 'Half Time Stats-A Score',
        35: 'Half Time Stats-H Momentum', 36: 'Half Time Stats-A Momentum',
        37: 'Half Time Stats-H xG', 38: 'Half Time Stats-A xG',
        39: 'Half Time Stats-H SOT', 40: 'Half Time Stats-A SOT',
        41: 'Half Time Stats-H SOFF', 42: 'Half Time Stats-A SOFF',
        43: 'Half Time Stats-H Corners', 44: 'Half Time Stats-A Corners',
        45: 'Half Time Stats-H Attacks', 46: 'Half Time Stats-A Attacks',
        47: 'Half Time Stats-H Dn Attacks', 48: 'Half Time Stats-A Dn Attacks',
        49: 'Half Time Stats-H Poss %', 50: 'Half Time Stats-A Poss %',
        51: 'Half Time Stats-H Y Cards', 52: 'Half Time Stats-A Y Cards',
        53: 'Half Time Stats-H R Cards', 54: 'Half Time Stats-A R Cards',
        55: 'Half Time Stats-H Penalties', 56: 'Half Time Stats-A Penalties',
        # Full Time Stats (57-80)
        57: 'Full Time Stats-H Score', 58: 'Full Time Stats-A Score',
        59: 'Full Time Stats-H Momentum', 60: 'Full Time Stats-A Momentum',
        61: 'Full Time Stats-H xG', 62: 'Full Time Stats-A xG',
        63: 'Full Time Stats-H SOT', 64: 'Full Time Stats-A SOT',
        65: 'Full Time Stats-H SOFF', 66: 'Full Time Stats-A SOFF',
        67: 'Full Time Stats-H Corners', 68: 'Full Time Stats-A Corners',
        69: 'Full Time Stats-H Attacks', 70: 'Full Time Stats-A Attacks',
        71: 'Full Time Stats-H Dn Attacks', 72: 'Full Time Stats-A Dn Attacks',
        73: 'Full Time Stats-H Poss %', 74: 'Full Time Stats-A Poss %',
        75: 'Full Time Stats-H Y Cards', 76: 'Full Time Stats-A Y Cards',
        77: 'Full Time Stats-H R Cards', 78: 'Full Time Stats-A R Cards',
        79: 'Full Time Stats-H Penalties', 80: 'Full Time Stats-A Penalties',
        # Result (81)
        81: 'Result',
        # Live Odds (82-96)
        82: 'Live Odds 3-Way: Home', 83: 'Live Odds 3-Way: Draw', 84: 'Live Odds 3-Way: Away',
        85: 'Live Odds Over 0.5 Goals', 86: 'Live Odds Under 0.5 Goals',
        87: 'Live Odds Over 1.5 Goals', 88: 'Live Odds Under 1.5 Goals',
        89: 'Live Odds Over 2.5 Goals', 90: 'Live Odds Under 2.5 Goals',
        91: 'Live Odds Over 3.5 Goals', 92: 'Live Odds Under 3.5 Goals',
        93: 'Live Odds Over 4.5 Goals', 94: 'Live Odds Under 4.5 Goals',
        95: 'Live Odds BTTS: Yes', 96: 'Live Odds BTTS: No',
        # Pre-Match Odds (97-111)
        97: 'Pre-Match Odds 3-Way: Home', 98: 'Pre-Match Odds 3-Way: Draw', 99: 'Pre-Match Odds 3-Way: Away',
        100: 'Pre-Match Odds Over 0.5 Goals', 101: 'Pre-Match Odds Under 0.5 Goals',
        102: 'Pre-Match Odds Over 1.5 Goals', 103: 'Pre-Match Odds Under 1.5 Goals',
        104: 'Pre-Match Odds Over 2.5 Goals', 105: 'Pre-Match Odds Under 2.5 Goals',
        106: 'Pre-Match Odds Over 3.5 Goals', 107: 'Pre-Match Odds Under 3.5 Goals',
        108: 'Pre-Match Odds Over 4.5 Goals', 109: 'Pre-Match Odds Under 4.5 Goals',
        110: 'Pre-Match Odds BTTS: Yes', 111: 'Pre-Match Odds BTTS: No',
        # Additional columns if present
        112: 'Strike Rate', 113: 'Avg Goals', 114: 'Avg Corners',
        115: 'Avg Cards', 116: 'BTTS %', 117: 'Over 2.5 %', 118: 'Notes'
    }
    
    # Renommer seulement les colonnes qui existent
    new_columns = []
    for i, col in enumerate(df.columns):
        if i in noms_colonnes:
            new_columns.append(noms_colonnes[i])
        else:
            new_columns.append(f'Col_{i}')
    
    df.columns = new_columns
    return df

def calculer_fav_und_lg70(df):
    """Calcule les colonnes Fav/Und pour le format LG70"""
    
    # Identifier les colonnes de cotes pre-match
    try:
        col_home = 'Pre-Match Odds 3-Way: Home'
        col_away = 'Pre-Match Odds 3-Way: Away'
        
        if col_home not in df.columns or col_away not in df.columns:
            print("  ⚠️ Colonnes de cotes pre-match non trouvées")
            return df
        
        # Créer les colonnes Fav/Und pour chaque statistique
        stats_mapping = {
            'Alert Time': ['Alert Time Stats-H', 'Alert Time Stats-A'],
            'Half Time': ['Half Time Stats-H', 'Half Time Stats-A'],
            'Full Time': ['Full Time Stats-H', 'Full Time Stats-A']
        }
        
        stats = ['Score', 'Momentum', 'xG', 'SOT', 'SOFF', 'Corners', 
                'Attacks', 'Dn Attacks', 'Poss %', 'Y Cards', 'R Cards', 'Penalties']
        
        nouvelles_colonnes = []
        
        for _, row in df.iterrows():
            try:
                cote_home = pd.to_numeric(row[col_home], errors='coerce')
                cote_away = pd.to_numeric(row[col_away], errors='coerce')
                
                if pd.notna(cote_home) and pd.notna(cote_away):
                    home_favori = cote_home <= cote_away
                    
                    valeurs_fav = []
                    valeurs_und = []
                    
                    for moment, prefixes in stats_mapping.items():
                        for stat in stats:
                            col_h = f'{prefixes[0]} {stat}'
                            col_a = f'{prefixes[1]} {stat}'
                            
                            if col_h in df.columns and col_a in df.columns:
                                val_h = row[col_h]
                                val_a = row[col_a]
                                valeurs_fav.append(val_h if home_favori else val_a)
                                valeurs_und.append(val_a if home_favori else val_h)
                            else:
                                valeurs_fav.append(None)
                                valeurs_und.append(None)
                    
                    nouvelles_colonnes.append(valeurs_fav + valeurs_und)
                else:
                    nouvelles_colonnes.append([None] * 72)
            except:
                nouvelles_colonnes.append([None] * 72)
        
        # Créer les noms de colonnes
        noms_fav = [f'{moment} Stats-Fav {stat}' for moment in ['Alert Time', 'Half Time', 'Full Time'] for stat in stats]
        noms_und = [f'{moment} Stats-Und {stat}' for moment in ['Alert Time', 'Half Time', 'Full Time'] for stat in stats]
        
        # Ajouter les nouvelles colonnes au DataFrame
        df_fav_und = pd.DataFrame(nouvelles_colonnes, columns=noms_fav + noms_und)
        df = pd.concat([df, df_fav_und], axis=1)
        
        print(f"  ✅ 72 colonnes Fav/Und ajoutées")
        
    except Exception as e:
        print(f"  ⚠️ Erreur calcul Fav/Und: {e}")
    
    return df

# ====================================================================================================
# SAUVEGARDE UNIVERSELLE
# ====================================================================================================

def sauvegarder_dataset_universel(df, filepath, format_sortie='auto'):
    """Sauvegarde le dataset dans le format demandé ou le même que l'entrée"""
    
    print("\n💾 Sauvegarde du dataset traité...")
    
    nom_base = os.path.splitext(os.path.basename(filepath))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Déterminer le format de sortie
    if format_sortie == 'auto':
        # Garder le même format que l'entrée
        extension = os.path.splitext(filepath)[1].lower()
        if extension in ['.xls', '.xlsx', '.xlsm']:
            format_sortie = 'excel'
        elif extension == '.parquet':
            format_sortie = 'parquet'
        elif extension == '.json':
            format_sortie = 'json'
        else:
            format_sortie = 'csv'
    
    # Pour les datasets de betting, toujours utiliser CSV européen
    is_betting = (len(df.columns) == 119 or len(df.columns) == 191 or 
                  any('bet' in str(col).lower() or 'odd' in str(col).lower() for col in df.columns))
    
    # Sauvegarder selon le format
    if format_sortie == 'csv':
        output_file = f"{nom_base}_PROCESSED_{timestamp}.csv"
        
        if is_betting:
            # Format européen pour betting (point-virgule et virgule décimale)
            df.to_csv(
                output_file,
                sep=';',
                index=False,
                encoding='utf-8-sig',
                decimal=',',
                date_format='%d/%m/%Y %H:%M'
            )
            print(f"  ✅ Sauvegardé en CSV européen : {output_file}")
            print(f"     • Séparateur : point-virgule (;)")
            print(f"     • Décimale : virgule (,)")
        else:
            # Format standard pour autres données
            df.to_csv(
                output_file,
                index=False,
                encoding='utf-8'
            )
            print(f"  ✅ Sauvegardé en CSV standard : {output_file}")
        
    elif format_sortie == 'excel':
        output_file = f"{nom_base}_PROCESSED_{timestamp}.xlsx"
        
        # Pour Excel, formater les nombres pour le format européen si betting
        if is_betting:
            with pd.ExcelWriter(output_file, engine='openpyxl', date_format='DD/MM/YYYY HH:MM') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
                
                # Appliquer le format européen aux cellules numériques
                worksheet = writer.sheets['Data']
                for row in worksheet.iter_rows(min_row=2):  # Skip header
                    for cell in row:
                        if isinstance(cell.value, (int, float)):
                            cell.number_format = '#,##0.00'  # Format européen
            print(f"  ✅ Sauvegardé en Excel (format européen) : {output_file}")
        else:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
            print(f"  ✅ Sauvegardé en Excel : {output_file}")
        
    elif format_sortie == 'parquet':
        output_file = f"{nom_base}_PROCESSED_{timestamp}.parquet"
        df.to_parquet(output_file, compression='snappy')
        print(f"  ✅ Sauvegardé en Parquet : {output_file}")
        
    elif format_sortie == 'json':
        output_file = f"{nom_base}_PROCESSED_{timestamp}.json"
        df.to_json(output_file, orient='records', date_format='iso', indent=2, force_ascii=False)
        print(f"  ✅ Sauvegardé en JSON : {output_file}")
    
    # Statistiques finales
    print(f"\n  📊 Statistiques finales :")
    print(f"     • Lignes : {len(df):,}")
    print(f"     • Colonnes : {len(df.columns)}")
    if len(df.columns) == 191:
        print(f"     • Colonnes originales : 119")
        print(f"     • Colonnes Fav/Und ajoutées : 72")
    print(f"     • Taille mémoire : {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    return output_file

# ====================================================================================================
# PROGRAMME PRINCIPAL
# ====================================================================================================

def traiter_fichier_universel(filepath, format_sortie='auto'):
    """Traite n'importe quel fichier dataset de manière universelle"""
    
    print("\n" + "="*80)
    print(f"  🚀 TRAITEMENT UNIVERSEL")
    print("="*80)
    
    try:
        # 1. Lire le dataset (format automatique)
        df, file_type = lire_dataset_universel(filepath)
        
        # 2. Analyser la structure
        structure = analyser_structure_dataset(df)
        
        # 3. Détecter le type de dataset
        is_betting, colonnes_betting = detecter_colonnes_betting(df, structure)
        
        # 4. Appliquer le traitement approprié
        if is_betting:
            df = traiter_dataset_betting(df, structure, colonnes_betting)
        else:
            df = traiter_dataset_generique(df, structure)
        
        # 5. Sauvegarder
        output = sauvegarder_dataset_universel(df, filepath, format_sortie)
        
        print("\n" + "🎉"*20)
        print("     🎯 TRAITEMENT RÉUSSI ! 🎯")
        print("🎉"*20)
        
        return True, output
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False, None

def main():
    """Fonction principale universelle"""
    
    print("="*80)
    print("           PARAMETRES.PY - VERSION UNIVERSELLE")
    print("        🌍 Compatible avec TOUS les formats de datasets")
    print("="*80)
    print("\n✨ Formats supportés :")
    print("   • Tableurs : CSV, TSV, Excel (.xls, .xlsx, .xlsm)")
    print("   • Données : JSON, JSON Lines, Parquet, Feather, Pickle")
    print("   • Bases : HDF5, Stata, SPSS, SAS")
    print("   • Web : HTML, XML")
    print("   • Binaires : ORC, MessagePack")
    print("\n🔍 Détection automatique :")
    print("   • Type de fichier")
    print("   • Structure des colonnes")
    print("   • Encodage et délimiteurs")
    print("   • Type de dataset (betting, finance, etc.)")
    
    # Récupérer les fichiers à traiter
    if len(sys.argv) > 1:
        # Fichier spécifié en argument
        fichiers = sys.argv[1:]
    else:
        # Scanner le dossier courant
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Patterns pour tous les formats supportés
        patterns = [
            '*.csv', '*.tsv', '*.txt',
            '*.xls', '*.xlsx', '*.xlsm', '*.xlsb',
            '*.json', '*.jsonl',
            '*.parquet', '*.pq',
            '*.feather', '*.ftr',
            '*.pkl', '*.pickle',
            '*.h5', '*.hdf', '*.hdf5',
            '*.sav', '*.dta', '*.sas7bdat',
            '*.xml', '*.html',
            '*.orc'
        ]
        
        fichiers = []
        for pattern in patterns:
            fichiers.extend(glob.glob(os.path.join(script_dir, pattern)))
        
        # Exclure les fichiers déjà traités
        fichiers = [f for f in fichiers if 'PROCESSED' not in os.path.basename(f).upper()]
        fichiers = [f for f in fichiers if 'BACKTESTER' not in os.path.basename(f).upper()]
    
    if not fichiers:
        print("\n❌ Aucun fichier dataset trouvé dans le dossier")
        print("\n💡 Usage : python PARAMETRES.py [fichier1] [fichier2] ...")
        print("   Ou placez vos datasets dans le même dossier que ce script")
    else:
        print(f"\n📂 {len(fichiers)} fichier(s) trouvé(s)")
        
        resultats = []
        for fichier in fichiers:
            if os.path.exists(fichier):
                succes, output = traiter_fichier_universel(fichier)
                resultats.append((fichier, succes, output))
        
        # Résumé final
        print("\n" + "="*80)
        print("  📋 RÉSUMÉ DES TRAITEMENTS")
        print("="*80)
        
        for fichier, succes, output in resultats:
            nom = os.path.basename(fichier)
            if succes:
                print(f"  ✅ {nom} → {os.path.basename(output)}")
            else:
                print(f"  ❌ {nom} → Échec")
    
    print("\n" + "-"*80)
    input("📌 Appuyez sur ENTRÉE pour terminer...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale : {e}")
        import traceback
        traceback.print_exc()
