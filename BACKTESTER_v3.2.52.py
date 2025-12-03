#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BACKTESTER.PY - Version Finale Corrigée
✅ Conversion correcte des colonnes de cotes
✅ Format Excel européen parfait
"""

import pandas as pd
import numpy as np
import sys
import os
import glob
from datetime import datetime
import re

# ====================================================================================================
# CONFIGURATION
# ====================================================================================================
SEUIL_FAVORI = 1.8  # Seuil pour identifier le favori

# Mapping COMPLET des colonnes selon la documentation
MAPPING_COLONNES = {
    # Match Data
    'date': 0,              # Match Data - Date
    'timer': 1,             # Match Data - Timer
    'strike': 2,            # Match Data - Strike
    'region': 3,            # Match Data - Region
    'league': 4,            # Match Data - League
    'home': 5,              # Match Data - Home
    'away': 6,              # Match Data - Away
    'home_pos': 7,          # Match Data - Home Pos
    'away_pos': 8,          # Match Data - Away Pos
    
    # Pre-Match Odds (pour calcul Fav/Und)
    'cote_home': 96,        # Pre-Match Odds - 3-Way: Home
    'cote_draw': 97,        # Pre-Match Odds - 3-Way: Draw
    'cote_away': 98,        # Pre-Match Odds - 3-Way: Away
}

# Noms exacts des colonnes selon la documentation
NOMS_COLONNES_EXACTES = {
    # Alert Time Stats (indices 9-32)
    9: 'H Score',
    10: 'A Score',
    11: 'H Momentum',
    12: 'A Momentum',
    13: 'H xG',
    14: 'A xG',
    15: 'H SOT',
    16: 'A SOT',
    17: 'H SOFF',
    18: 'A SOFF',
    19: 'H Corners',
    20: 'A Corners',
    21: 'H Attacks',
    22: 'A Attacks',
    23: 'H Dn Attacks',
    24: 'A Dn Attacks',
    25: 'H Poss %',
    26: 'A Poss %',
    27: 'H Y Cards',
    28: 'A Y Cards',
    29: 'H R Cards',
    30: 'A R Cards',
    31: 'H Penalties',
    32: 'A Penalties',
    
    # Half Time Stats (indices 33-56)
    33: 'H Score.1',
    34: 'A Score.1',
    35: 'H Momentum.1',
    36: 'A Momentum.1',
    37: 'H xG.1',
    38: 'A xG.1',
    39: 'H SOT.1',
    40: 'A SOT.1',
    41: 'H SOFF.1',
    42: 'A SOFF.1',
    43: 'H Corners.1',
    44: 'A Corners.1',
    45: 'H Attacks.1',
    46: 'A Attacks.1',
    47: 'H Dn Attacks.1',
    48: 'A Dn Attacks.1',
    49: 'H Poss %.1',
    50: 'A Poss %.1',
    51: 'H Y Cards.1',
    52: 'A Y Cards.1',
    53: 'H R Cards.1',
    54: 'A R Cards.1',
    55: 'H Penalties.1',
    56: 'A Penalties.1',
    
    # Full Time Stats (indices 57-80)
    57: 'H Score.2',
    58: 'A Score.2',
    59: 'H Momentum.2',
    60: 'A Momentum.2',
    61: 'H xG.2',
    62: 'A xG.2',
    63: 'H SOT.2',
    64: 'A SOT.2',
    65: 'H SOFF.2',
    66: 'A SOFF.2',
    67: 'H Corners.2',
    68: 'A Corners.2',
    69: 'H Attacks.2',
    70: 'A Attacks.2',
    71: 'H Dn Attacks.2',
    72: 'A Dn Attacks.2',
    73: 'H Poss %.2',
    74: 'A Poss %.2',
    75: 'H Y Cards.2',
    76: 'A Y Cards.2',
    77: 'H R Cards.2',
    78: 'A R Cards.2',
    79: 'H Penalties.2',
    80: 'A Penalties.2',
    
    # Live Odds (Alert Time) - indices 81-95
    # Note: Les colonnes Live ont maintenant le suffixe AT comme toutes les autres stats Alert Time
    81: '3-Way: Home AT',
    82: '3-Way: Draw AT',
    83: '3-Way: Away AT',
    84: 'Over 0.5 Goals AT',
    85: 'Under 0.5 Goals AT',
    86: 'Over 1.5 Goals AT',
    87: 'Under 1.5 Goals AT',
    88: 'Over 2.5 Goals AT',
    89: 'Under 2.5 Goals AT',
    90: 'Over 3.5 Goals AT',
    91: 'Under 3.5 Goals AT',
    92: 'Over 4.5 Goals AT',
    93: 'Under 4.5 Goals AT',
    94: 'BTTS: Yes AT',
    95: 'BTTS: No AT',
    
    # Pre-Match Odds - indices 96-110
    # Note: Pandas ajoute .1 car ce sont les mêmes noms que les cotes Live mais sans le suffixe AT
    96: '3-Way: Home.1',
    97: '3-Way: Draw.1',
    98: '3-Way: Away.1',
    99: 'Over 0.5 Goals.1',
    100: 'Under 0.5 Goals.1',
    101: 'Over 1.5 Goals.1',
    102: 'Under 1.5 Goals.1',
    103: 'Over 2.5 Goals.1',
    104: 'Under 2.5 Goals.1',
    105: 'Over 3.5 Goals.1',
    106: 'Under 3.5 Goals.1',
    107: 'Over 4.5 Goals.1',
    108: 'Under 4.5 Goals.1',
    109: 'BTTS: Yes.1',
    110: 'BTTS: No.1',
}

# ====================================================================================================
# FONCTIONS UTILITAIRES
# ====================================================================================================

def clear_screen():
    """Efface l'écran"""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    """Met le programme en pause"""
    print("\n" + "-"*80)
    input("📌 Appuyez sur ENTRÉE pour fermer cette fenêtre...")

def convertir_nombre_excel_europeen(valeur):
    """
    Convertit simplement un nombre au format Excel européen
    Point → Virgule pour les décimales
    """
    if pd.isna(valeur) or valeur == '' or valeur is None:
        return ''
    
    val_str = str(valeur).strip()
    
    # Cas spécial : scores comme "1-2"
    if '-' in val_str and val_str.count('-') == 1 and not val_str.startswith('-'):
        # Vérifier si c'est un score
        parties = val_str.split('-')
        try:
            int(parties[0])
            int(parties[1])
            return "'" + val_str  # Protéger le score
        except:
            pass
    
    # Convertir en nombre et formater
    try:
        num = float(val_str)
        
        # Si c'est un entier, pas de décimales
        if num == int(num):
            return str(int(num))
        else:
            # Remplacer le point par une virgule
            result = str(num).replace('.', ',')
            return result
            
    except:
        # Ce n'est pas un nombre, retourner tel quel
        return val_str

# ====================================================================================================
# RENOMMAGE INTELLIGENT DES COLONNES
# ====================================================================================================

def renommer_colonnes_intelligemment(df):
    """
    Renomme intelligemment les colonnes avec .1, .2, etc.
    """
    print("\n🔧 Renommage intelligent des colonnes...")
    print("-" * 80)
    
    colonnes = df.columns.tolist()
    nouvelles_colonnes = []
    stats_de_base = ['Score', 'Momentum', 'xG', 'SOT', 'SOFF', 'Corners', 
                     'Attacks', 'Dn Attacks', 'Poss %', 'Y Cards', 'R Cards', 'Penalties']
    
    compteur_stats = {stat: {'H': 0, 'A': 0} for stat in stats_de_base}
    renommages_effectues = []
    
    prefixes_cotes = ('3-Way', 'Over', 'Under', 'BTTS')
    
    for i, col in enumerate(colonnes):
        col_str = str(col)
        nouvelle_col = col_str
        
        # Ajouter AT aux colonnes de cotes Live (sans suffixe .1)
        if any(col_str.startswith(prefix) for prefix in prefixes_cotes):
            if '.' not in col_str and not col_str.endswith(' AT'):
                nouvelle_col = f'{col_str} AT'
                renommages_effectues.append((col_str, nouvelle_col))
                nouvelles_colonnes.append(nouvelle_col)
                continue
        
        # Détecter les colonnes de stats
        for stat in stats_de_base:
            # Pattern pour Home
            if re.match(rf'^H {stat}(\.\d+)?$', col_str) or col_str == f'H {stat}':
                count = compteur_stats[stat]['H']
                if count == 0:
                    nouvelle_col = f'H {stat} AT'
                elif count == 1:
                    nouvelle_col = f'H {stat} HT'
                elif count == 2:
                    nouvelle_col = f'H {stat} FT'
                compteur_stats[stat]['H'] += 1
                if nouvelle_col != col_str:
                    renommages_effectues.append((col_str, nouvelle_col))
                break
            
            # Pattern pour Away
            elif re.match(rf'^A {stat}(\.\d+)?$', col_str) or col_str == f'A {stat}':
                count = compteur_stats[stat]['A']
                if count == 0:
                    nouvelle_col = f'A {stat} AT'
                elif count == 1:
                    nouvelle_col = f'A {stat} HT'
                elif count == 2:
                    nouvelle_col = f'A {stat} FT'
                compteur_stats[stat]['A'] += 1
                if nouvelle_col != col_str:
                    renommages_effectues.append((col_str, nouvelle_col))
                break
        
        # Autres colonnes avec .1, .2 (SAUF les colonnes de cotes)
        if nouvelle_col == col_str and '.' in col_str:
            base, suffix = col_str.rsplit('.', 1)
            if suffix.isdigit():
                # Ne PAS renommer les colonnes de cotes (3-Way, Goals, BTTS)
                if any(x in base for x in ['3-Way', 'Goals', 'BTTS']):
                    # Garder le nom original pour les cotes Pre-Match
                    nouvelle_col = col_str
                else:
                    # Renommer les autres colonnes normalement
                    suffix_int = int(suffix)
                    if suffix_int == 1:
                        nouvelle_col = f'{base} HT'
                    elif suffix_int == 2:
                        nouvelle_col = f'{base} FT'
                    if nouvelle_col != col_str:
                        renommages_effectues.append((col_str, nouvelle_col))
        
        nouvelles_colonnes.append(nouvelle_col)
    
    if renommages_effectues:
        print("\n📝 Colonnes renommées :")
        for ancien, nouveau in renommages_effectues[:10]:
            print(f"  • {ancien:30} → {nouveau}")
        if len(renommages_effectues) > 10:
            print(f"  ... et {len(renommages_effectues) - 10} autres colonnes")
    
    df.columns = nouvelles_colonnes
    
    print(f"\n  ✅ {len(renommages_effectues)} colonnes renommées")
    
    return df, nouvelles_colonnes

# ====================================================================================================
# CHARGEMENT DES DONNÉES
# ====================================================================================================

def charger_dataset(filepath):
    """Charge un dataset correctement"""
    print(f"\n📖 Chargement : {os.path.basename(filepath)}")
    print("-" * 80)
    
    extension = os.path.splitext(filepath)[1].lower()
    
    try:
        if extension == '.csv':
            # Lire le fichier normalement
            df = pd.read_csv(filepath, skiprows=1, low_memory=False)
            print(f"  • Fichier CSV chargé (virgule comme séparateur)")
                
        elif extension in ['.xls', '.xlsx']:
            df = pd.read_excel(filepath)
            print("  • Fichier Excel chargé")
        else:
            print(f"  ❌ Extension non supportée : {extension}")
            return None, None
            
        print(f"  ✅ {len(df)} lignes × {len(df.columns)} colonnes")
        
        # Renommer les colonnes
        df, nouvelles_colonnes = renommer_colonnes_intelligemment(df)
        
        return df, nouvelles_colonnes
        
    except Exception as e:
        print(f"  ❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return None, None

# ====================================================================================================
# CALCUL FAV/UND (SANS TOUCHER AUX VALEURS ORIGINALES)
# ====================================================================================================

def construire_mapping_dynamique(colonnes):
    """Construit le mapping pour le calcul Fav/Und"""
    stats_mapping = {
        'AT': {},
        'HT': {},
        'FT': {}
    }
    
    stats_de_base = ['Score', 'Momentum', 'xG', 'SOT', 'SOFF', 'Corners', 
                     'Attacks', 'Dn Attacks', 'Poss %', 'Y Cards', 'R Cards', 'Penalties']
    
    for stat in stats_de_base:
        for moment in ['AT', 'HT', 'FT']:
            col_h = f'H {stat} {moment}'
            col_a = f'A {stat} {moment}'
            
            if col_h in colonnes and col_a in colonnes:
                stats_mapping[moment][stat] = (col_h, col_a)
    
    return stats_mapping

def calculer_fav_und(df, colonnes_list, seuil=SEUIL_FAVORI):
    """Calcule les 72 colonnes Fav/Und SANS modifier les colonnes de cotes"""
    print(f"\n🎯 Calcul Fav/Und (seuil={seuil})")
    print("-" * 80)
    
    stats_mapping = construire_mapping_dynamique(colonnes_list)
    
    # Vérifier les colonnes de cotes
    if len(df.columns) <= MAPPING_COLONNES['cote_away']:
        print("  ⚠️ Colonnes de cotes manquantes")
        return df
    
    # Créer les 72 colonnes Fav/Und
    colonnes_fav_und = []
    
    for moment in ['AT', 'HT', 'FT']:
        for stat in ['Score', 'Momentum', 'xG', 'SOT', 'SOFF', 'Corners',
                    'Attacks', 'Dn Attacks', 'Poss %', 'Y Cards', 'R Cards', 'Penalties']:
            colonnes_fav_und.append(f"{moment}_Fav {stat}")
    
    for moment in ['AT', 'HT', 'FT']:
        for stat in ['Score', 'Momentum', 'xG', 'SOT', 'SOFF', 'Corners',
                    'Attacks', 'Dn Attacks', 'Poss %', 'Y Cards', 'R Cards', 'Penalties']:
            colonnes_fav_und.append(f"{moment}_Und {stat}")
    
    valeurs_fav_und = []
    matchs_avec_favori = 0
    
    for idx in range(len(df)):
        valeurs_match = []
        
        # Récupérer les cotes pour le calcul SANS les modifier dans le DataFrame
        try:
            # Lire les valeurs
            val_home = df.iloc[idx, MAPPING_COLONNES['cote_home']]
            val_away = df.iloc[idx, MAPPING_COLONNES['cote_away']]
            
            # Convertir pour le calcul uniquement
            if pd.notna(val_home):
                cote_home = float(str(val_home).replace(',', '.'))
            else:
                cote_home = None
                
            if pd.notna(val_away):
                cote_away = float(str(val_away).replace(',', '.'))
            else:
                cote_away = None
                
        except:
            cote_home = None
            cote_away = None
        
        # Déterminer le favori
        home_favori = False
        a_un_favori = False
        
        if cote_home and cote_away:
            if cote_home <= seuil and cote_away > seuil:
                home_favori = True
                a_un_favori = True
            elif cote_away <= seuil and cote_home > seuil:
                home_favori = False
                a_un_favori = True
            elif cote_home <= seuil and cote_away <= seuil:
                home_favori = (cote_home <= cote_away)
                a_un_favori = True
        
        if a_un_favori:
            matchs_avec_favori += 1
            
            # Remplir les valeurs Fav
            for moment in ['AT', 'HT', 'FT']:
                stats = stats_mapping[moment]
                
                for stat in ['Score', 'Momentum', 'xG', 'SOT', 'SOFF', 'Corners',
                            'Attacks', 'Dn Attacks', 'Poss %', 'Y Cards', 'R Cards', 'Penalties']:
                    if stat in stats:
                        col_h, col_a = stats[stat]
                        try:
                            val_h = df.loc[idx, col_h] if col_h in df.columns else ''
                            val_a = df.loc[idx, col_a] if col_a in df.columns else ''
                            val_fav = val_h if home_favori else val_a
                        except:
                            val_fav = ''
                    else:
                        val_fav = ''
                    valeurs_match.append(val_fav)
            
            # Remplir les valeurs Und
            for moment in ['AT', 'HT', 'FT']:
                stats = stats_mapping[moment]
                
                for stat in ['Score', 'Momentum', 'xG', 'SOT', 'SOFF', 'Corners',
                            'Attacks', 'Dn Attacks', 'Poss %', 'Y Cards', 'R Cards', 'Penalties']:
                    if stat in stats:
                        col_h, col_a = stats[stat]
                        try:
                            val_h = df.loc[idx, col_h] if col_h in df.columns else ''
                            val_a = df.loc[idx, col_a] if col_a in df.columns else ''
                            val_und = val_a if home_favori else val_h
                        except:
                            val_und = ''
                    else:
                        val_und = ''
                    valeurs_match.append(val_und)
        else:
            valeurs_match = [''] * 72
        
        valeurs_fav_und.append(valeurs_match)
    
    print(f"  • {matchs_avec_favori}/{len(df)} matchs avec favori")
    print(f"  • 72 colonnes Fav/Und créées")
    
    df_fav_und = pd.DataFrame(valeurs_fav_und, columns=colonnes_fav_und)
    df_final = pd.concat([df, df_fav_und], axis=1)
    
    return df_final

# ====================================================================================================
# CONVERSION FINALE AU FORMAT EXCEL EUROPÉEN
# ====================================================================================================

def convertir_dataframe_excel_europeen_final(df):
    """
    Convertit TOUT le DataFrame au format Excel européen
    Y COMPRIS les colonnes de cotes
    """
    print("\n🔧 Conversion finale au format Excel européen...")
    
    colonnes_texte = ['Date', 'Timer', 'Strike', 'Region', 'League', 'Home', 'Away']
    colonnes_converties = 0
    
    # Créer un DataFrame de résultat avec toutes les colonnes en object (string)
    df_resultat = pd.DataFrame(index=df.index)
    
    # Convertir TOUTES les colonnes
    for i, col in enumerate(df.columns):
        col_str = str(col)
        
        # Skip les colonnes texte - les copier telles quelles
        if any(txt in col_str for txt in colonnes_texte):
            df_resultat[col] = df.iloc[:, i].astype(str)
            continue
        
        # Convertir chaque cellule de la colonne numérique
        nouvelle_colonne = []
        for val in df.iloc[:, i]:
            val_convertie = convertir_nombre_excel_europeen(val)
            nouvelle_colonne.append(val_convertie)
        
        # Forcer en string pour garder les virgules
        df_resultat[col] = nouvelle_colonne
        colonnes_converties += 1
    
    print(f"  ✅ {colonnes_converties} colonnes converties")
    print(f"  ✅ Colonnes de cotes (96, 98) incluses")
    
    return df_resultat

# ====================================================================================================
# FORMATAGE ET SAUVEGARDE
# ====================================================================================================

def formater_colonne_date(df):
    """Formate la première colonne (Date)"""
    if len(df.columns) > 0:
        date_col = df.columns[0]
        try:
            dates = pd.to_datetime(df[date_col], errors='coerce')
            df[date_col] = dates.dt.strftime('%d/%m/%Y %H:%M')
            df[date_col] = df[date_col].fillna('')
            print("  ✅ Colonne Date formatée : JJ/MM/AAAA HH:MM")
            return True
        except:
            pass
    return False

def sauvegarder_resultats(df, fichier_source):
    """Sauvegarde avec format Excel européen"""
    print("\n💾 SAUVEGARDE")
    print("-" * 80)
    
    nom_base = os.path.splitext(os.path.basename(fichier_source))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    output_excel = f"{nom_base}_BACKTESTER_{timestamp}.csv"
    
    # Sauvegarder avec point-virgule comme séparateur
    df.to_csv(output_excel, sep=';', index=False, encoding='utf-8-sig')
    
    print(f"  ✅ {output_excel}")
    print(f"     • Séparateur colonnes : point-virgule (;)")
    print(f"     • Séparateur décimal : virgule (,)")
    print(f"     • TOUTES les colonnes converties (y compris cotes)")
    
    return output_excel

# ====================================================================================================
# PROGRAMME PRINCIPAL
# ====================================================================================================

def traiter_fichier(filepath):
    """Traite un fichier complet"""
    nom = os.path.basename(filepath)
    
    print("\n" + "="*60)
    print(f"  TRAITEMENT : {nom}")
    print("="*60)
    
    try:
        # 1. Charger et renommer
        df, nouvelles_colonnes = charger_dataset(filepath)
        if df is None:
            return False
        
        # 2. Formater la date
        formater_colonne_date(df)
        
        # 3. Calculer Fav/Und (SANS modifier les colonnes de cotes)
        df = calculer_fav_und(df, nouvelles_colonnes)
        
        # 4. Conversion FINALE au format Excel européen (APRÈS le calcul)
        df = convertir_dataframe_excel_europeen_final(df)
        
        # 5. Statistiques
        print("\n📊 STATISTIQUES")
        print(f"  • Lignes : {len(df)}")
        print(f"  • Colonnes : {len(df.columns)}")
        cols_fav_und = [c for c in df.columns if 'Fav' in str(c) or 'Und' in str(c)]
        print(f"  • Colonnes Fav/Und : {len(cols_fav_und)}")
        
        # 6. Sauvegarder
        output = sauvegarder_resultats(df, filepath)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale"""
    clear_screen()
    
    print("="*80)
    print("                 BACKTESTER.PY")
    print("      Version Finale - Colonnes de Cotes Corrigées")
    print("="*80)
    print("\n✨ Améliorations :")
    print("   ✅ Conversion FINALE après calcul Fav/Und")
    print("   ✅ Colonnes 3-Way Home/Away converties en virgule")
    print("   ✅ Format Excel européen parfait pour TOUTES les colonnes")
    print("   ✅ 72 colonnes Fav/Und créées")
    
    if len(sys.argv) > 1:
        fichiers = [sys.argv[1]]
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        patterns = ['*.csv', '*.xls', '*.xlsx']
        
        fichiers = []
        for pattern in patterns:
            fichiers.extend(glob.glob(os.path.join(script_dir, pattern)))
        
        fichiers = [f for f in fichiers if 'BACKTESTER' not in os.path.basename(f).upper()]
    
    if not fichiers:
        print("\n❌ Aucun fichier trouvé")
        print("\n💡 Usage : python BACKTESTER.py [fichier.csv]")
    else:
        print(f"\n📂 {len(fichiers)} fichier(s) trouvé(s)")
        
        for fichier in fichiers:
            if os.path.exists(fichier):
                if traiter_fichier(fichier):
                    print("\n" + "🎉"*20)
                    print("     🎯 SUCCÈS ! 🎯")
                    print("🎉"*20)
    
    pause()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption")
        pause()
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        pause()
