# ====================================================================================================
# MAPPING POSITIONS COLONNES - SOURCE CSV RÉFÉRENCE (119 COLONNES)
# ====================================================================================================
# Numérotation : Ligne CSV = Numéro dans code
# Accès Python : df.iloc[ligne - 1]
# Total : 119 colonnes (A à DO)
# Source validée : REFERENCE_COLUMNS_VALIDATED.csv
# ====================================================================================================

# MATCH DATA (Lignes 1-9)
COL_DATE = 1           # A (ligne 1, index Python 0) : Match Data - Date
COL_TIMER = 2          # B (ligne 2, index Python 1) : Match Data - Timer
COL_STRIKE = 3         # C (ligne 3, index Python 2) : Match Data - Strike
COL_REGION = 4         # D (ligne 4, index Python 3) : Match Data - Region
COL_LEAGUE = 5         # E (ligne 5, index Python 4) : Match Data - League
COL_HOME = 6           # F (ligne 6, index Python 5) : Match Data - Home
COL_AWAY = 7           # G (ligne 7, index Python 6) : Match Data - Away
COL_HOME_POS = 8       # H (ligne 8, index Python 7) : Match Data - Home Pos
COL_AWAY_POS = 9       # I (ligne 9, index Python 8) : Match Data - Away Pos

# ALERT TIME STATS (Lignes 10-33)
COL_ALERT_HOME_SCORE = 10        # J (ligne 10, index Python 9) : Alert Time Stats - H Score
COL_ALERT_AWAY_SCORE = 11        # K (ligne 11, index Python 10) : Alert Time Stats - A Score
COL_ALERT_HOME_MOMENTUM = 12     # L (ligne 12, index Python 11) : Alert Time Stats - H Momentum
COL_ALERT_AWAY_MOMENTUM = 13     # M (ligne 13, index Python 12) : Alert Time Stats - A Momentum
COL_ALERT_HOME_XG = 14           # N (ligne 14, index Python 13) : Alert Time Stats - H xG
COL_ALERT_AWAY_XG = 15           # O (ligne 15, index Python 14) : Alert Time Stats - A xG
COL_ALERT_HOME_SOT = 16          # P (ligne 16, index Python 15) : Alert Time Stats - H SOT
COL_ALERT_AWAY_SOT = 17          # Q (ligne 17, index Python 16) : Alert Time Stats - A SOT
COL_ALERT_HOME_SOFF = 18         # R (ligne 18, index Python 17) : Alert Time Stats - H SOFF
COL_ALERT_AWAY_SOFF = 19         # S (ligne 19, index Python 18) : Alert Time Stats - A SOFF
COL_ALERT_HOME_CORNERS = 20      # T (ligne 20, index Python 19) : Alert Time Stats - H Corners
COL_ALERT_AWAY_CORNERS = 21      # U (ligne 21, index Python 20) : Alert Time Stats - A Corners
COL_ALERT_HOME_ATTACKS = 22      # V (ligne 22, index Python 21) : Alert Time Stats - H Attacks
COL_ALERT_AWAY_ATTACKS = 23      # W (ligne 23, index Python 22) : Alert Time Stats - A Attacks
COL_ALERT_HOME_DN_ATTACKS = 24   # X (ligne 24, index Python 23) : Alert Time Stats - H Dn Attacks
COL_ALERT_AWAY_DN_ATTACKS = 25   # Y (ligne 25, index Python 24) : Alert Time Stats - A Dn Attacks
COL_ALERT_HOME_POSS = 26         # Z (ligne 26, index Python 25) : Alert Time Stats - H Poss %
COL_ALERT_AWAY_POSS = 27         # AA (ligne 27, index Python 26) : Alert Time Stats - A Poss %
COL_ALERT_HOME_YCARDS = 28       # AB (ligne 28, index Python 27) : Alert Time Stats - H Y Cards
COL_ALERT_AWAY_YCARDS = 29       # AC (ligne 29, index Python 28) : Alert Time Stats - A Y Cards
COL_ALERT_HOME_RCARDS = 30       # AD (ligne 30, index Python 29) : Alert Time Stats - H R Cards
COL_ALERT_AWAY_RCARDS = 31       # AE (ligne 31, index Python 30) : Alert Time Stats - A R Cards
COL_ALERT_HOME_PENALTIES = 32    # AF (ligne 32, index Python 31) : Alert Time Stats - H Penalties
COL_ALERT_AWAY_PENALTIES = 33    # AG (ligne 33, index Python 32) : Alert Time Stats - A Penalties

# HALF TIME STATS (Lignes 34-57)
COL_HALF_HOME_SCORE = 34         # AH (ligne 34, index Python 33) : Half Time Stats - H Score
COL_HALF_AWAY_SCORE = 35         # AI (ligne 35, index Python 34) : Half Time Stats - A Score
COL_HALF_HOME_MOMENTUM = 36      # AJ (ligne 36, index Python 35) : Half Time Stats - H Momentum
COL_HALF_AWAY_MOMENTUM = 37      # AK (ligne 37, index Python 36) : Half Time Stats - A Momentum
COL_HALF_HOME_XG = 38            # AL (ligne 38, index Python 37) : Half Time Stats - H xG
COL_HALF_AWAY_XG = 39            # AM (ligne 39, index Python 38) : Half Time Stats - A xG
COL_HALF_HOME_SOT = 40           # AN (ligne 40, index Python 39) : Half Time Stats - H SOT
COL_HALF_AWAY_SOT = 41           # AO (ligne 41, index Python 40) : Half Time Stats - A SOT
COL_HALF_HOME_SOFF = 42          # AP (ligne 42, index Python 41) : Half Time Stats - H SOFF
COL_HALF_AWAY_SOFF = 43          # AQ (ligne 43, index Python 42) : Half Time Stats - A SOFF
COL_HALF_HOME_CORNERS = 44       # AR (ligne 44, index Python 43) : Half Time Stats - H Corners
COL_HALF_AWAY_CORNERS = 45       # AS (ligne 45, index Python 44) : Half Time Stats - A Corners
COL_HALF_HOME_ATTACKS = 46       # AT (ligne 46, index Python 45) : Half Time Stats - H Attacks
COL_HALF_AWAY_ATTACKS = 47       # AU (ligne 47, index Python 46) : Half Time Stats - A Attacks
COL_HALF_HOME_DN_ATTACKS = 48    # AV (ligne 48, index Python 47) : Half Time Stats - H Dn Attacks
COL_HALF_AWAY_DN_ATTACKS = 49    # AW (ligne 49, index Python 48) : Half Time Stats - A Dn Attacks
COL_HALF_HOME_POSS = 50          # AX (ligne 50, index Python 49) : Half Time Stats - H Poss %
COL_HALF_AWAY_POSS = 51          # AY (ligne 51, index Python 50) : Half Time Stats - A Poss %
COL_HALF_HOME_YCARDS = 52        # AZ (ligne 52, index Python 51) : Half Time Stats - H Y Cards
COL_HALF_AWAY_YCARDS = 53        # BA (ligne 53, index Python 52) : Half Time Stats - A Y Cards
COL_HALF_HOME_RCARDS = 54        # BB (ligne 54, index Python 53) : Half Time Stats - H R Cards
COL_HALF_AWAY_RCARDS = 55        # BC (ligne 55, index Python 54) : Half Time Stats - A R Cards
COL_HALF_HOME_PENALTIES = 56     # BD (ligne 56, index Python 55) : Half Time Stats - H Penalties
COL_HALF_AWAY_PENALTIES = 57     # BE (ligne 57, index Python 56) : Half Time Stats - A Penalties

# FULL TIME STATS (Lignes 58-81)
COL_FULL_HOME_SCORE = 58         # BF (ligne 58, index Python 57) : Full Time Stats - H Score
COL_FULL_AWAY_SCORE = 59         # BG (ligne 59, index Python 58) : Full Time Stats - A Score
COL_FULL_HOME_MOMENTUM = 60      # BH (ligne 60, index Python 59) : Full Time Stats - H Momentum
COL_FULL_AWAY_MOMENTUM = 61      # BI (ligne 61, index Python 60) : Full Time Stats - A Momentum
COL_FULL_HOME_XG = 62            # BJ (ligne 62, index Python 61) : Full Time Stats - H xG
COL_FULL_AWAY_XG = 63            # BK (ligne 63, index Python 62) : Full Time Stats - A xG
COL_FULL_HOME_SOT = 64           # BL (ligne 64, index Python 63) : Full Time Stats - H SOT
COL_FULL_AWAY_SOT = 65           # BM (ligne 65, index Python 64) : Full Time Stats - A SOT
COL_FULL_HOME_SOFF = 66          # BN (ligne 66, index Python 65) : Full Time Stats - H SOFF
COL_FULL_AWAY_SOFF = 67          # BO (ligne 67, index Python 66) : Full Time Stats - A SOFF
COL_FULL_HOME_CORNERS = 68       # BP (ligne 68, index Python 67) : Full Time Stats - H Corners
COL_FULL_AWAY_CORNERS = 69       # BQ (ligne 69, index Python 68) : Full Time Stats - A Corners
COL_FULL_HOME_ATTACKS = 70       # BR (ligne 70, index Python 69) : Full Time Stats - H Attacks
COL_FULL_AWAY_ATTACKS = 71       # BS (ligne 71, index Python 70) : Full Time Stats - A Attacks
COL_FULL_HOME_DN_ATTACKS = 72    # BT (ligne 72, index Python 71) : Full Time Stats - H Dn Attacks
COL_FULL_AWAY_DN_ATTACKS = 73    # BU (ligne 73, index Python 72) : Full Time Stats - A Dn Attacks
COL_FULL_HOME_POSS = 74          # BV (ligne 74, index Python 73) : Full Time Stats - H Poss %
COL_FULL_AWAY_POSS = 75          # BW (ligne 75, index Python 74) : Full Time Stats - A Poss %
COL_FULL_HOME_YCARDS = 76        # BX (ligne 76, index Python 75) : Full Time Stats - H Y Cards
COL_FULL_AWAY_YCARDS = 77        # BY (ligne 77, index Python 76) : Full Time Stats - A Y Cards
COL_FULL_HOME_RCARDS = 78        # BZ (ligne 78, index Python 77) : Full Time Stats - H R Cards
COL_FULL_AWAY_RCARDS = 79        # CA (ligne 79, index Python 78) : Full Time Stats - A R Cards
COL_FULL_HOME_PENALTIES = 80     # CB (ligne 80, index Python 79) : Full Time Stats - H Penalties
COL_FULL_AWAY_PENALTIES = 81     # CC (ligne 81, index Python 80) : Full Time Stats - A Penalties

# LIVE ODDS - ALERT TIME (Lignes 82-96)
COL_LIVE_3WAY_HOME = 82          # CD (ligne 82, index Python 81) : Live Odds (Alert Time) - 3-Way: Home
COL_LIVE_3WAY_DRAW = 83          # CE (ligne 83, index Python 82) : Live Odds (Alert Time) - 3-Way: Draw
COL_LIVE_3WAY_AWAY = 84          # CF (ligne 84, index Python 83) : Live Odds (Alert Time) - 3-Way: Away
COL_LIVE_OVER_05 = 85            # CG (ligne 85, index Python 84) : Live Odds (Alert Time) - Over 0.5 Goals
COL_LIVE_UNDER_05 = 86           # CH (ligne 86, index Python 85) : Live Odds (Alert Time) - Under 0.5 Goals
COL_LIVE_OVER_15 = 87            # CI (ligne 87, index Python 86) : Live Odds (Alert Time) - Over 1.5 Goals
COL_LIVE_UNDER_15 = 88           # CJ (ligne 88, index Python 87) : Live Odds (Alert Time) - Under 1.5 Goals
COL_LIVE_OVER_25 = 89            # CK (ligne 89, index Python 88) : Live Odds (Alert Time) - Over 2.5 Goals
COL_LIVE_UNDER_25 = 90           # CL (ligne 90, index Python 89) : Live Odds (Alert Time) - Under 2.5 Goals
COL_LIVE_OVER_35 = 91            # CM (ligne 91, index Python 90) : Live Odds (Alert Time) - Over 3.5 Goals
COL_LIVE_UNDER_35 = 92           # CN (ligne 92, index Python 91) : Live Odds (Alert Time) - Under 3.5 Goals
COL_LIVE_OVER_45 = 93            # CO (ligne 93, index Python 92) : Live Odds (Alert Time) - Over 4.5 Goals
COL_LIVE_UNDER_45 = 94           # CP (ligne 94, index Python 93) : Live Odds (Alert Time) - Under 4.5 Goals
COL_LIVE_BTTS_YES = 95           # CQ (ligne 95, index Python 94) : Live Odds (Alert Time) - BTTS: Yes
COL_LIVE_BTTS_NO = 96            # CR (ligne 96, index Python 95) : Live Odds (Alert Time) - BTTS: No

# PRE-MATCH ODDS (Lignes 97-111)
COL_PREMATCH_3WAY_HOME = 97      # CS (ligne 97, index Python 96) : Pre-Match Odds - 3-Way: Home
COL_PREMATCH_3WAY_DRAW = 98      # CT (ligne 98, index Python 97) : Pre-Match Odds - 3-Way: Draw
COL_PREMATCH_3WAY_AWAY = 99      # CU (ligne 99, index Python 98) : Pre-Match Odds - 3-Way: Away
COL_PREMATCH_OVER_05 = 100       # CV (ligne 100, index Python 99) : Pre-Match Odds - Over 0.5 Goals
COL_PREMATCH_UNDER_05 = 101      # CW (ligne 101, index Python 100) : Pre-Match Odds - Under 0.5 Goals
COL_PREMATCH_OVER_15 = 102       # CX (ligne 102, index Python 101) : Pre-Match Odds - Over 1.5 Goals
COL_PREMATCH_UNDER_15 = 103      # CY (ligne 103, index Python 102) : Pre-Match Odds - Under 1.5 Goals
COL_PREMATCH_OVER_25 = 104       # CZ (ligne 104, index Python 103) : Pre-Match Odds - Over 2.5 Goals
COL_PREMATCH_UNDER_25 = 105      # DA (ligne 105, index Python 104) : Pre-Match Odds - Under 2.5 Goals
COL_PREMATCH_OVER_35 = 106       # DB (ligne 106, index Python 105) : Pre-Match Odds - Over 3.5 Goals
COL_PREMATCH_UNDER_35 = 107      # DC (ligne 107, index Python 106) : Pre-Match Odds - Under 3.5 Goals
COL_PREMATCH_OVER_45 = 108       # DD (ligne 108, index Python 107) : Pre-Match Odds - Over 4.5 Goals
COL_PREMATCH_UNDER_45 = 109      # DE (ligne 109, index Python 108) : Pre-Match Odds - Under 4.5 Goals
COL_PREMATCH_BTTS_YES = 110      # DF (ligne 110, index Python 109) : Pre-Match Odds - BTTS: Yes
COL_PREMATCH_BTTS_NO = 111       # DG (ligne 111, index Python 110) : Pre-Match Odds - BTTS: No

# GOAL TIMES (Lignes 112-113)
COL_GOAL_TIMES_HOME = 112        # DH (ligne 112, index Python 111) : Goal Times - Home
COL_GOAL_TIMES_AWAY = 113        # DI (ligne 113, index Python 112) : Goal Times - Away

# SUMMARY (Lignes 114-119)
COL_SUMMARY_SCORE = 114          # DJ (ligne 114, index Python 113) : Summary - Score
COL_SUMMARY_HT_SCORE = 115       # DK (ligne 115, index Python 114) : Summary - HT Score
COL_SUMMARY_FT_SCORE = 116       # DL (ligne 116, index Python 115) : Summary - FT Score
COL_SUMMARY_CORNERS = 117        # DM (ligne 117, index Python 116) : Summary - Corners
COL_SUMMARY_HT_CORNERS = 118     # DN (ligne 118, index Python 117) : Summary - HT Corners
COL_SUMMARY_FT_CORNERS = 119     # DO (ligne 119, index Python 118) : Summary - FT Corners

# ====================================================================================================
# NOTES IMPORTANTES
# ====================================================================================================
# 1. Numérotation : Les constantes utilisent la ligne CSV (1-119), pas l'index Python (0-118)
# 2. Accès : Pour accéder aux données, utiliser df.iloc[COL_xxx - 1]
# 3. Pattern 
#    - LIVE : CG/CH, CI/CJ, CK/CL, CM/CN, CO/CP
#    - PRE-MATCH : CV/CW, CX/CY, CZ/DA, DB/DC, DD/DE
# 4. Total colonnes : 119 (A à DO), pas 118
# 5. Dernière colonne : DO (ligne 119) = Summary - FT Corners
# ====================================================================================================
