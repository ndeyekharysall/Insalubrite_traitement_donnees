# =============================================================================
# loader.py — Chargement, nettoyage de base et contrôles de cohérence
# =============================================================================

import os
import logging
import numpy as np
import pandas as pd
import pyreadstat

from config import (
    INPUT_DIR, INPUT_FILE,
    QC_AGE_MIN, QC_AGE_MAX, QC_TAILLE_MAX,
    QC_DUREE_QUARTIER_MAX, QC_MISSING_THRESH,
)

logger = logging.getLogger(__name__)


def _to_numeric_or_nan(series):
    return pd.to_numeric(series, errors="coerce")


def _flag_outlier(df, col, lo, hi, label, qc_log):
    if col not in df.columns:
        return df
    mask = df[col].notna() & ((df[col] < lo) | (df[col] > hi))
    n = mask.sum()
    if n > 0:
        qc_log.append({
            "check": f"outlier_{col}",
            "description": f"{label} : valeurs hors [{lo}, {hi}]",
            "n_affected": int(n),
            "action": "Remplacé par NaN",
        })
        df.loc[mask, col] = np.nan
    return df


def _flag_incoherence(df, mask, label, action, qc_log):
    n = mask.sum()
    if n > 0:
        qc_log.append({
            "check": "incoherence",
            "description": label,
            "n_affected": int(n),
            "action": action,
        })
    return n


def load_raw(filepath: str):
    logger.info(f"Chargement : {filepath}")
    df, meta = pyreadstat.read_dta(filepath)
    logger.info(f"Dimensions brutes : {df.shape[0]} lignes × {df.shape[1]} colonnes")
    logger.info(f"Colonnes disponibles : {list(df.columns)}")
    return df, meta


def clean_types(df: pd.DataFrame, qc_log: list) -> pd.DataFrame:
    df = df.copy()

    # Colonnes "other" textuelles
    other_cols = [c for c in df.columns if c.endswith("_other")]
    for col in other_cols:
        df[col] = df[col].astype(str).str.strip().replace({"": np.nan, "nan": np.nan})

    # Colonnes codes catégoriels en string
    str_cat_cols = [
        "I_4", "I_7", "I_10", "II_3", "II_5", "II_22", "II_23",
        "III_4", "III_23", "III_26", "III_30", "Commune",
    ]
    for col in str_cat_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"": np.nan, "nan": np.nan})

    # Colonnes multi-réponses textuelles
    multichoix_cols = ["III_7", "III_9", "III_16", "III_20", "III_32", "III_33"]
    for col in multichoix_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({"": np.nan, "nan": np.nan})

    # Variables continues
    num_cols = ["I_3", "I_9", "I_5_1", "I_5_2", "I_5_3", "I_5_4", "III_1"]
    for col in num_cols:
        if col in df.columns:
            df[col] = _to_numeric_or_nan(df[col])

    if "I_5" in df.columns:
        df["I_5"] = _to_numeric_or_nan(df["I_5"])

    # Colonnes Likert et binaires
    likert_cols = [
        "I_2", "I_6", "I_8", "I_11",
        "I_12_1", "I_12_2", "I_12_3", "I_12_4", "I_12_5",
        "II_4", "II_6", "II_7", "II_8", "II_11",
        "II_12_1", "II_12_2", "II_12_3", "II_12_4",
        "II_13", "II_14", "II_15", "II_16", "II_17", "II_18", "II_19", "II_20",
        "II_24", "II_25_1", "II_25_2",
        "III_1", "III_2", "III_3", "III_5", "III_6", "III_8",
        "III_10", "III_11", "III_12", "III_13", "III_14", "III_15",
        "III_18", "III_19", "III_21", "III_22", "III_24", "III_25", "III_27",
        "III_28", "III_29", "III_31",
    ]
    for col in likert_cols:
        if col in df.columns:
            df[col] = _to_numeric_or_nan(df[col])

    binary_cols = [c for c in df.columns if c.startswith("_v")]
    for col in binary_cols:
        df[col] = _to_numeric_or_nan(df[col])

    logger.info("Nettoyage des types terminé.")
    return df


def quality_checks(df: pd.DataFrame, qc_log: list) -> pd.DataFrame:
    df = df.copy()

    # Outliers âge
    df = _flag_outlier(df, "I_3", QC_AGE_MIN, QC_AGE_MAX, "Âge répondant", qc_log)
    df = _flag_outlier(df, "I_9", QC_AGE_MIN, QC_AGE_MAX, "Âge chef de ménage", qc_log)
    df = _flag_outlier(df, "I_5", 0, QC_TAILLE_MAX, "Taille ménage totale", qc_log)

    # Cohérence benne tasseuse
    if "II_13" in df.columns:
        cols_benne_detail = ["II_14", "II_16", "II_17", "II_18", "II_19", "II_20"]
        mask_no_benne = df["II_13"] == 2
        for col in cols_benne_detail:
            if col in df.columns:
                incoherent = mask_no_benne & df[col].notna()
                _flag_incoherence(
                    df, incoherent,
                    f"Ménage sans benne (II_13=2) mais {col} renseigné",
                    "Conservé — skip pattern non appliqué par l'enquêteur",
                    qc_log,
                )

    # Cohérence payant sans montant
    if "II_24" in df.columns and "II_25_1" in df.columns:
        mask = (df["II_24"] == 1) & df["II_25_1"].isna()
        _flag_incoherence(df, mask,
            "Service déclaré payant (II_24=1) mais montant manquant (II_25_1)",
            "Conservé comme NaN — montant inconnu", qc_log)

    # Cohérence revente
    if "II_8" in df.columns:
        mask_no_revente = df["II_8"] == 2
        for col in ["_v18", "_v19", "_v20", "_v21", "_v22"]:
            if col in df.columns:
                incoherent = mask_no_revente & (df[col] == 1)
                _flag_incoherence(df, incoherent,
                    f"Pas de revente (II_8=2) mais {col}=1",
                    "Conservé — possible erreur de saisie", qc_log)

    # Cohérence dépôts sauvages
    if "III_12" in df.columns:
        mask_no_depot = df["III_12"] == 3
        for col in ["III_13", "III_14"]:
            if col in df.columns:
                incoherent = mask_no_depot & df[col].notna()
                _flag_incoherence(df, incoherent,
                    f"Pas de dépôt sauvage (III_12=3) mais {col} renseigné",
                    "Conservé — skip pattern", qc_log)

    # Taux de manquants
    for col in df.columns:
        rate = df[col].isna().mean()
        if rate > QC_MISSING_THRESH:
            qc_log.append({
                "check": "missing_rate",
                "description": f"Variable '{col}' : {rate:.1%} de valeurs manquantes",
                "n_affected": int(df[col].isna().sum()),
                "action": "Alerte — à interpréter selon le skip pattern attendu",
            })

    logger.info(f"Contrôles qualité : {len(qc_log)} signalements générés.")
    return df


def run(qc_log: list) -> tuple:
    filepath = os.path.join(INPUT_DIR, INPUT_FILE)
    df, meta = load_raw(filepath)
    df = clean_types(df, qc_log)
    df = quality_checks(df, qc_log)
    return df, meta
