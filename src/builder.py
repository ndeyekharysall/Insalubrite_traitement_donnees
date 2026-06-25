# =============================================================================
# builder.py — Construction des variables analytiques
# Validé sur questionnaire ENSAE/UCG 2018 et structure réelle de la base
# =============================================================================

import logging
import numpy as np
import pandas as pd

from config import (
    SEXE, STATUT_REPONDANT, STATUT_OCCUPATION, TYPE_LOGEMENT,
    TYPE_ENSEIGNEMENT_CM, NIVEAU_INSTRUCTION_CM, ALPHA,
    MODE_STOCKAGE, PLACE_STOCKAGE, PROPORTION_TRAITEE, TRAITEMENT_PRATIQUE,
    ACCES_BENNE, RESPONSABLE_EVACUATION, DISTANCE_COLLECTE,
    FREQUENCE_BENNE, SATISFACTION_BENNE,
    SERVICE_ALTERNATIF, RAISON_SERVICE_ALTERNATIF,
    MONTANT_EVACUATION, FREQUENCE_PAIEMENT,
    MONTANT_MEDIAN_FCFA, FREQ_TO_MONTHLY,
    SATISFACTION_4PT, FREQUENCE_COMPORTEMENT,
    RAISON_INSATISFACTION_BACS, DEPOTS_SAUVAGES, DERNIER_DEPOT,
    GESTIONNAIRE_PLACE, GESTIONNAIRE_MARCHE, ORGANISATEUR_CAMPAGNE,
    DEPARTEMENT,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _col(df, col, default=None):
    """Retourne df[col] si la colonne existe, sinon une série de NaN avec un warning."""
    if col in df.columns:
        return df[col]
    logger.warning(f"Colonne brute absente : '{col}' — variable(s) dérivée(s) mise(s) à NaN.")
    if default is not None:
        return pd.Series(default, index=df.index)
    return pd.Series(np.nan, index=df.index)


def _map(series, mapping):
    return series.map(mapping)


def _oui_non(series):
    return series.map({1: "Oui", 2: "Non"})


def _binary_flag(series):
    return series.fillna(0).astype(int)


def _concat_flags(df, cols_labels, sep=" | "):
    """Construit une liste textuelle des modalités sélectionnées (binaires = 1)."""
    available = [(c, l) for c, l in cols_labels if c in df.columns]
    if not available:
        return pd.Series(np.nan, index=df.index)
    def row_labels(row):
        lbls = [l for c, l in available if row.get(c, 0) == 1]
        return sep.join(lbls) if lbls else np.nan
    return df[list(dict.fromkeys([c for c, _ in available]))].assign(
        **{c: df[c] for c, _ in available}
    ).apply(row_labels, axis=1)


def _sum_flags(df, cols):
    return sum(_col(df, c).fillna(0) for c in cols).astype(int)


# ---------------------------------------------------------------------------
# BLOC A — Ménage
# ---------------------------------------------------------------------------

def build_menage(df):
    out = pd.DataFrame(index=df.index)

    # Identifiants géographiques
    out["commune_code"] = _col(df, "Commune").astype(str).str.strip().replace({"nan": np.nan})
    out["quartier"]     = _col(df, "quartier").astype(str).str.strip().replace({"nan": np.nan})

    # Note : toute la zone est urbaine (Dakar), région non collectée comme variable
    out["zone"] = "Région de Dakar (urbain)"

    # Taille du ménage
    out["nb_enfants_0_4"]  = _col(df, "I_5_1").fillna(0).astype(int)
    out["nb_enfants_5_15"] = _col(df, "I_5_2").fillna(0).astype(int)
    out["nb_adultes_H"]    = _col(df, "I_5_3").fillna(0).astype(int)
    out["nb_adultes_F"]    = _col(df, "I_5_4").fillna(0).astype(int)

    i5 = _col(df, "I_5")
    if i5.notna().sum() > 0:
        out["taille_menage"] = pd.to_numeric(i5, errors="coerce")
    else:
        out["taille_menage"] = (out["nb_enfants_0_4"] + out["nb_enfants_5_15"] +
                                out["nb_adultes_H"]   + out["nb_adultes_F"])

    # Statut occupation et type logement
    out["statut_occupation"] = _map(_col(df, "I_6"), STATUT_OCCUPATION)
    out["type_habitat"]      = _map(_col(df, "I_7").astype(str), TYPE_LOGEMENT)

    # PROXY niveau de vie (0-3)
    # +1 si propriétaire, +1 si logement structuré (maison basse/étage/appart), +1 si paie déchets
    i6 = _col(df, "I_6")
    i7 = _col(df, "I_7").astype(str)
    ii24 = _col(df, "II_24")
    proxy = ((i6 == 2).astype(int) +
             i7.isin(["2", "3", "4"]).astype(int) +
             (ii24 == 1).astype(int))
    out["proxy_niveau_vie"]       = proxy
    out["proxy_niveau_vie_label"] = proxy.map({0: "Faible", 1: "Moyen-bas", 2: "Moyen-haut", 3: "Élevé"})

    logger.info(f"Bloc A (ménage) : {out.shape[1]} variables construites.")
    return out


# ---------------------------------------------------------------------------
# BLOC B — Chef de Ménage
# ---------------------------------------------------------------------------

def build_cm(df):
    out = pd.DataFrame(index=df.index)

    # Répondant
    out["repondant_sexe"]    = _map(_col(df, "I_2"), SEXE)
    out["repondant_age"]     = pd.to_numeric(_col(df, "I_3"), errors="coerce").replace({98: np.nan, 99: np.nan})
    out["repondant_statut"]  = _map(_col(df, "I_4").astype(str), STATUT_REPONDANT)
    out["repondant_est_cm"]  = (_col(df, "I_4").astype(str) == "1").map({True: "Oui", False: "Non"})

    # Chef de ménage
    out["cm_sexe"] = _map(_col(df, "I_8"), SEXE)
    cm_age = pd.to_numeric(_col(df, "I_9"), errors="coerce").replace({98: np.nan, 99: np.nan})
    out["cm_age"] = cm_age

    # Tranche d'âge CM
    bins   = [0, 25, 35, 45, 60, 200]
    labels = ["Moins de 25 ans", "25-34 ans", "35-44 ans", "45-59 ans", "60 ans et plus"]
    out["cm_tranche_age"] = pd.cut(cm_age, bins=bins, labels=labels, right=False).astype(object).where(cm_age.notna(), np.nan)

    # Instruction CM
    out["cm_type_enseignement"] = _map(_col(df, "I_10").astype(str), TYPE_ENSEIGNEMENT_CM)
    out["cm_niveau_instruction"] = _map(_col(df, "I_11"), NIVEAU_INSTRUCTION_CM)

    # Alphabétisation CM
    # Note : I_12_1 = Aucune langue (1=Oui sauf alpha), I_12_2 = Français, etc.
    out["cm_alpha_aucune_langue"] = _map(_col(df, "I_12_1"), ALPHA)
    out["cm_alpha_francais"]      = _map(_col(df, "I_12_2"), ALPHA)
    out["cm_alpha_anglais"]       = _map(_col(df, "I_12_3"), ALPHA)
    out["cm_alpha_arabe"]         = _map(_col(df, "I_12_4"), ALPHA)
    out["cm_alpha_lng_nationale"] = _map(_col(df, "I_12_5"), ALPHA)  # _5 = langue étrangère dans la base

    # CM alphabétisé dans au moins une langue (autre que "aucune")
    alpha_cols = ["I_12_2", "I_12_3", "I_12_4", "I_12_5"]
    alpha_bin = pd.DataFrame({c: (_col(df, c) == 1).astype(float) for c in alpha_cols})
    out["cm_est_alphabetise"] = alpha_bin.max(axis=1).map({1.0: "Oui", 0.0: "Non"})

    # Variables non collectées
    out["cm_situation_matrimoniale"] = np.nan
    out["cm_statut_emploi"]          = np.nan
    out["cm_secteur_emploi"]         = np.nan
    out["cm_revenu"]                 = np.nan

    logger.info(f"Bloc B (CM) : {out.shape[1]} variables construites.")
    return out


# ---------------------------------------------------------------------------
# BLOC C — Déchets Ménagers
# ---------------------------------------------------------------------------

def build_dechets(df):
    out = pd.DataFrame(index=df.index)

    # --- II.1 Sources de déchets ---
    sources = [
        ("_v1", "Consommation alimentaire / Cuisine"),
        ("_v2", "Gestion du foyer (hors alimentation)"),
        ("_v3", "Élevage"),
        ("_v4", "Animaux domestiques"),
        ("_v5", "Entretien du logement"),
        ("_v6", "Commerce / activités de production"),
        ("_v7", "Autre source"),
    ]
    for col, lbl in sources:
        out[f"src_{col}"] = _binary_flag(_col(df, col, 0))
    out["sources_liste"]  = _concat_flags(df, sources)
    out["nb_sources"]     = _sum_flags(df, [c for c, _ in sources])

    # --- II.2 Nature des déchets ---
    natures = [
        ("_v8",  "Plastiques"),
        ("_v9",  "Papier / Carton"),
        ("_v10", "Restes d'aliments"),
        ("_v11", "Vêtements / Tissus"),
        ("_v12", "Déchets électroménagers"),
        ("_v13", "Déchets verts"),
        ("_v14", "Métal"),
        ("_v15", "Excréments d'animaux"),
        ("_v16", "Médicaments"),
        ("_v17", "Autre nature"),
    ]
    for col, lbl in natures:
        out[f"nat_{col}"] = _binary_flag(_col(df, col, 0))
    out["natures_liste"] = _concat_flags(df, natures)
    out["nb_natures"]    = _sum_flags(df, [c for c, _ in natures])

    # --- II.3-II.6 Stockage ---
    out["mode_stockage"]              = _map(_col(df, "II_3").astype(str), MODE_STOCKAGE)
    out["stockage_couvert"]           = _oui_non(_col(df, "II_4"))
    out["place_stockage"]             = _map(_col(df, "II_5").astype(str), PLACE_STOCKAGE)
    out["capacite_stockage_suffisante"] = _oui_non(_col(df, "II_6"))

    # --- II.7-II.10 Tri et revente ---
    out["tri_avant_evacuation"] = _oui_non(_col(df, "II_7"))
    out["revente_dechets"]      = _oui_non(_col(df, "II_8"))
    revendus = [
        ("_v18", "Journaux"), ("_v19", "Verre"), ("_v20", "Ferraille"),
        ("_v21", "Plastique"), ("_v22", "Autre déchet revendu"),
    ]
    out["types_revendus_liste"] = _concat_flags(df, revendus)
    out["raison_non_revente"]   = _col(df, "II_10").map({
        1: "N'en a pas connaissance",
        2: "Revenus faibles",
        3: "Ne connaît pas les modes de revente",
        4: "N'a pas le temps nécessaire",
        5: "N'est pas intéressé",
    })

    # --- II.11-II.12 Traitement ---
    out["proportion_traitee"]    = _map(_col(df, "II_11"), PROPORTION_TRAITEE)
    out["traitement_enfouissement"] = _map(_col(df, "II_12_1"), TRAITEMENT_PRATIQUE)
    out["traitement_incineration"]  = _map(_col(df, "II_12_2"), TRAITEMENT_PRATIQUE)
    out["traitement_recyclage"]     = _map(_col(df, "II_12_3"), TRAITEMENT_PRATIQUE)
    out["traitement_compostage"]    = _map(_col(df, "II_12_4"), TRAITEMENT_PRATIQUE)
    trait_bin = pd.DataFrame({
        "e": _col(df, "II_12_1").isin([1, 2]).astype(float),
        "i": _col(df, "II_12_2").isin([1, 2]).astype(float),
        "r": _col(df, "II_12_3").isin([1, 2]).astype(float),
        "c": _col(df, "II_12_4").isin([1, 2]).astype(float),
    })
    out["au_moins_un_traitement"] = trait_bin.max(axis=1).map({1.0: "Oui", 0.0: "Non"})

    # --- II.12 Responsable évacuation ---
    out["responsable_evacuation"] = _map(_col(df, "II_15"), RESPONSABLE_EVACUATION)

    # --- II.13-II.20 Bennes tasseuses (service public) ---
    out["acces_benne_tasseuse"]   = _map(_col(df, "II_13"), ACCES_BENNE)
    out["benne_usage_regulier"]   = _oui_non(_col(df, "II_14"))
    out["distance_point_collecte"] = _map(_col(df, "II_16"), DISTANCE_COLLECTE)
    out["benne_point_nettoyage"]  = _oui_non(_col(df, "II_17"))
    out["benne_heure_convient"]   = _oui_non(_col(df, "II_17"))  # II_17 dans questionnaire
    out["frequence_benne"]        = _map(_col(df, "II_19"), FREQUENCE_BENNE)
    out["satisfaction_benne"]     = _map(_col(df, "II_20"), SATISFACTION_BENNE)

    # --- II.21-II.23 Service alternatif (si pas de benne) ---
    out["service_alternatif_type"]   = _map(_col(df, "II_22").astype(str), SERVICE_ALTERNATIF)
    out["service_alternatif_raison"] = _map(_col(df, "II_23").astype(str), RAISON_SERVICE_ALTERNATIF)
    out["a_service_alternatif"]      = _col(df, "II_22").astype(str).isin(
        ["1", "2", "3", "other"]
    ).map({True: "Oui", False: "Non"})

    # --- II.23-II.25 Paiement ---
    out["service_evacuation_payant"]       = _oui_non(_col(df, "II_24"))
    out["montant_evacuation_tranche"]      = _map(_col(df, "II_25_1"), MONTANT_EVACUATION)
    out["frequence_paiement"]              = _map(_col(df, "II_25_2"), FREQUENCE_PAIEMENT)
    med  = _col(df, "II_25_1").map(MONTANT_MEDIAN_FCFA)
    freq = _col(df, "II_25_2").map(FREQ_TO_MONTHLY)
    montant_calc = (med * freq).round(0)
    out["montant_mensuel_evacuation_fcfa"] = np.where(
        _col(df, "II_24") == 1, montant_calc, 0
    )

    # --- III.1 Durée dans le quartier ---
    out["duree_quartier"] = _col(df, "III_1").map({1: "Moins d'un mois", 2: "1 mois et plus"})

    # --- III.2-III.4 Bacs à ordures publics ---
    out["existence_bacs_quartier"]     = _col(df, "III_2").map({1: "Oui", 2: "Non", 3: "Ne sait pas"})
    out["satisfaction_bacs"]           = _map(_col(df, "III_3"), SATISFACTION_4PT)
    out["raison_insatisfaction_bacs"]  = _map(_col(df, "III_4").astype(str), RAISON_INSATISFACTION_BACS)

    # --- III.5-III.9 Corbeilles de rue ---
    out["corbeilles_rue_presentes"]          = _oui_non(_col(df, "III_5"))
    out["satisfaction_emplacements_corbeilles"] = _map(_col(df, "III_6"), SATISFACTION_4PT)
    out["satisfaction_qualite_corbeilles"]   = _map(_col(df, "III_8"), SATISFACTION_4PT)

    # Indicateur : accès à un dépotoire normalisé
    bac_ok      = _col(df, "III_2") == 1
    corbeille_ok = _col(df, "III_5") == 1
    out["acces_depotoire_normalise"] = (bac_ok | corbeille_ok).map({True: "Oui", False: "Non"})

    # --- III.10-III.16 Dépôts sauvages ---
    out["dep_sauvages_rue_freq"]       = _map(_col(df, "III_10"), FREQUENCE_COMPORTEMENT)
    out["eaux_usees_rue_freq"]         = _map(_col(df, "III_11"), FREQUENCE_COMPORTEMENT)
    out["depots_sauvages_observes"]    = _map(_col(df, "III_12"), DEPOTS_SAUVAGES)
    out["dernier_depot_sauvage"]       = _map(_col(df, "III_13"), DERNIER_DEPOT)
    out["contact_UCG_pour_depot"]      = _oui_non(_col(df, "III_14"))
    out["satisfaction_reaction_UCG"]   = _map(_col(df, "III_15"), SATISFACTION_4PT)

    # --- III.17 Nuisibles ---
    nuisibles = [
        ("_v23", "Moustiques"), ("_v24", "Mouches"), ("_v25", "Cafards"),
        ("_v26", "Souris"), ("_v27", "Vers"), ("_v28", "Rats"), ("_v29", "Autre"),
    ]
    for col, lbl in nuisibles:
        out[f"nuisible_{col}"] = _binary_flag(_col(df, col, 0))
    out["nuisibles_liste"] = _concat_flags(df, nuisibles)
    out["nb_nuisibles"]    = _sum_flags(df, [c for c, _ in nuisibles])

    # --- III.18-III.20 Balayage ---
    out["service_balayage_rues"]    = _col(df, "III_18").map({1: "Oui", 2: "Non", 3: "Ne sait pas"})
    out["satisfaction_balayage"]    = _map(_col(df, "III_19"), SATISFACTION_4PT)
    out["set_setal"]                = _oui_non(_col(df, "III_21"))

    # --- III.22-III.24 Place publique ---
    out["place_publique"]               = _oui_non(_col(df, "III_22"))
    out["gestionnaire_place_publique"]  = _map(_col(df, "III_23").astype(str), GESTIONNAIRE_PLACE)
    out["salubrite_place_publique"]     = _map(_col(df, "III_24"), SATISFACTION_4PT)

    # --- III.25-III.27 Marché ---
    out["marche_present"]           = _oui_non(_col(df, "III_25"))
    out["gestionnaire_marche"]      = _map(_col(df, "III_26").astype(str), GESTIONNAIRE_MARCHE)
    out["gestion_dechets_marche"]   = _map(_col(df, "III_27"), SATISFACTION_4PT)

    # --- III.28-III.33 Sensibilisation ---
    out["connait_UCG"]                = _oui_non(_col(df, "III_28"))
    out["campagne_sensibilisation"]   = _oui_non(_col(df, "III_29"))
    out["organisateur_campagne"]      = _map(_col(df, "III_30").astype(str), ORGANISATEUR_CAMPAGNE)
    out["satisfait_campagne"]         = _oui_non(_col(df, "III_31"))
    out["suggestions_amelioration"]   = _col(df, "III_33").astype(str).replace({"nan": np.nan})

    logger.info(f"Bloc C (déchets) : {out.shape[1]} variables construites.")
    return out


# ---------------------------------------------------------------------------
# BLOC D — Conséquences sanitaires (Section IV)
# ---------------------------------------------------------------------------

def build_consequences(df):
    out = pd.DataFrame(index=df.index)

    # IV.1 — Maladies déclarées (multi-select)
    maladies = [
        ("_v30", "Fièvre"),
        ("_v31", "Asthme"),
        ("_v32", "Rhume"),
        ("_v33", "Sinusite"),
        ("_v34", "Toux"),
        ("_v35", "Nausées ou vomissements"),
        ("_v36", "Démangeaisons"),
        ("_v37", "Aucune maladie"),
        ("_v38", "Autre maladie"),
    ]
    for col, lbl in maladies:
        out[f"maladie_{col}"] = _binary_flag(_col(df, col, 0))

    out["maladies_liste"]     = _concat_flags(df, maladies)
    out["nb_maladies"]        = _sum_flags(df, [c for c, l in maladies if l != "Aucune maladie"])
    out["aucune_maladie"]     = _binary_flag(_col(df, "_v37", 0))

    # IV_count = nombre total de types de maladies dans le ménage
    if "IV_count" in df.columns:
        out["nb_types_maladies_menage"] = pd.to_numeric(df["IV_count"], errors="coerce")

    # Indicateur : au moins une maladie potentiellement liée aux déchets
    # (asthme, sinusite, toux, nausées, démangeaisons — hors fièvre et rhume)
    cols_liees = ["_v31", "_v33", "_v34", "_v35", "_v36"]
    somme_liees = _sum_flags(df, cols_liees)
    out["maladie_liee_dechets"] = (somme_liees >= 1).map({True: "Oui", False: "Non"})

    logger.info(f"Bloc D (conséquences) : {out.shape[1]} variables construites.")
    return out


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def run(df_raw):
    blocs = [
        build_menage(df_raw),
        build_cm(df_raw),
        build_dechets(df_raw),
        build_consequences(df_raw),
    ]
    df_final = pd.concat(blocs, axis=1).reset_index(drop=True)
    logger.info(f"Table consolidée : {df_final.shape[0]} lignes × {df_final.shape[1]} colonnes.")
    return df_final
