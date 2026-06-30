# =============================================================================
# check_brut.py — Diagnostic à lancer AVANT de faire confiance à la sortie.
# Pose ce fichier à la racine du repo (à côté de main.py) puis :  python check_brut.py
# =============================================================================
import os
import sys

import pandas as pd
import pyreadstat

# --- localiser src/ et le fichier brut ---------------------------------------
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "src"))

import config  # noqa: E402  (utilise INPUT_DIR / INPUT_FILE résolus par config.py)
import builder  # noqa: E402

FILEPATH = os.path.join(config.INPUT_DIR, config.INPUT_FILE)
print(f"Fichier lu : {FILEPATH}")
if not os.path.exists(FILEPATH):
    sys.exit(f"  -> INTROUVABLE. Vérifie le nom dans config.INPUT_FILE et le dossier input/Input.")

df, meta = pyreadstat.read_dta(FILEPATH)
print(f"Dimensions brutes : {df.shape[0]} lignes x {df.shape[1]} colonnes\n")

# --- 1. Champs string ODK sans value label : codes réellement présents -------
# Si tu vois "1.0" / "2.0" ou des espaces, les mappings string de config échoueront.
print("=" * 70)
print("1. CHAMPS STRING (codes attendus : '1','2',... ou 'other')")
print("=" * 70)
str_fields = ["I_4", "I_7", "I_10", "II_3", "II_5",
              "II_22", "II_23", "III_4", "III_23", "III_26", "III_30"]
for c in str_fields:
    if c not in df.columns:
        print(f"  {c:8s} : ABSENT de la base")
        continue
    vc = df[c].astype(str).str.strip().replace({"nan": "<NaN>"}).value_counts(dropna=False)
    apercu = ", ".join(f"{repr(k)}:{v}" for k, v in vc.head(8).items())
    print(f"  {c:8s} : {apercu}")

# --- 2. II_13 : le codebook ne définit que 1=Oui, 2=Non ----------------------
print("\n" + "=" * 70)
print("2. II_13 (bennes) — valeurs au-dela de 1/2 = mappees en NaN")
print("=" * 70)
if "II_13" in df.columns:
    print(pd.to_numeric(df["II_13"], errors="coerce").value_counts(dropna=False).to_string())
else:
    print("  II_13 ABSENT")

# --- 3. La sortie n'est plus vide (le test qui prouve que le brut est le bon) -
print("\n" + "=" * 70)
print("3. SORTIE DU BUILDER — doit avoir BEAUCOUP de colonnes non vides")
print("=" * 70)
out = builder.run(df)
n = len(out)
vides = [c for c in out.columns if out[c].isna().all()]
remplies = [c for c in out.columns if out[c].notna().any()]
print(f"  Colonnes de sortie : {out.shape[1]}")
print(f"  Colonnes 100% vides : {len(vides)}   (si > 50, tu as relu le MAUVAIS fichier)")
print(f"  Colonnes remplies   : {len(remplies)}")

# Aperçu des variables clés reconstruites
print("\n  Aperçu variables clés :")
for c in ["departement", "commune_libelle", "cm_est_alphabetise",
          "benne_point_nettoyage", "benne_heure_convient",
          "satisfaction_benne", "acces_benne_tasseuse"]:
    if c in out.columns:
        vals = out[c].dropna().value_counts().head(4).to_dict()
        print(f"    {c:24s} -> {vals}")

print("\nDiagnostic terminé.")
