# =============================================================================
# config.py — Configuration centrale — validée sur questionnaire ENSAE/UCG 2018
# =============================================================================

import os

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ATTENTION casse : sous Linux/Render "input" != "Input". On résout le dossier
# réellement présent pour éviter un FileNotFoundError silencieux.
_cand_dirs  = [d for d in ("input", "Input", "INPUT") if os.path.isdir(os.path.join(BASE_DIR, d))]
INPUT_DIR   = os.path.join(BASE_DIR, _cand_dirs[0]) if _cand_dirs else os.path.join(BASE_DIR, "input")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output")
DOC_DIR     = os.path.join(BASE_DIR, "Documentation")
# Mets ici le nom EXACT de ton fichier brut (sensible à la casse sous Linux).
INPUT_FILE  = "base_Insalubrite.dta"

# ---------------------------------------------------------------------------
# MODULE I — Ménage & Chef de Ménage
# ---------------------------------------------------------------------------

SEXE = {1: "Homme", 2: "Femme"}

# I.4 — Statut du répondant (codes string dans la base)
STATUT_REPONDANT = {
    "1":     "Chef de ménage",
    "2":     "Femme ou Mari",
    "3":     "Fils ou Fille",
    "4":     "Gendre / Belle-fille",
    "5":     "Petit-fils / Petite-fille",
    "6":     "Frère ou Sœur",
    "7":     "Coépouse",
    "8":     "Autre parent",
    "9":     "Sans parenté",
    "10":    "Employé(e) rémunéré(e)",
    "other": "Autre",
}

# I.6 — Statut d'occupation (labels Stata déjà corrects)
STATUT_OCCUPATION = {1: "Locataire", 2: "Propriétaire", 3: "Logé par un tiers"}

# I.7 — Type de logement (codes string)
TYPE_LOGEMENT = {
    "1":     "Case / Baraque",
    "2":     "Maison basse",
    "3":     "Maison en étage",
    "4":     "Appartement",
    "other": "Autre",
}

# I.10 — Type d'enseignement CM (codes string)
TYPE_ENSEIGNEMENT_CM = {
    "1":     "École française",
    "2":     "École arabe",
    "3":     "École coranique",
    "4":     "Aucun",
    "5":     "Ne sait pas",
    "other": "Autre",
}

# I.11 — Niveau d'instruction CM (labels Stata déjà corrects)
NIVEAU_INSTRUCTION_CM = {1: "Primaire", 2: "Secondaire", 3: "Supérieur", 4: "Ne sait pas"}

# I.12 — Alphabétisation (labels Stata déjà corrects)
ALPHA = {1: "Oui", 2: "Non", 3: "Ne sait pas"}

# ---------------------------------------------------------------------------
# MODULE II — Déchets
# ---------------------------------------------------------------------------

# II.3 — Mode de stockage (codes string)
MODE_STOCKAGE = {
    "1":     "Poubelle spécialisée",
    "2":     "Seau / Bassine",
    "3":     "Fût",
    "4":     "Carton",
    "5":     "Sac",
    "other": "Autre",
}

# II.5 — Place habituelle de stockage (codes string)
PLACE_STOCKAGE = {
    "1":     "Dans la cuisine",
    "2":     "Dans la parcelle",
    "3":     "Dans la rue, près de la maison",
    "4":     "Dans la rue, loin de la maison",
    "other": "Autre",
}

# II.11 — Proportion traitée (labels Stata déjà corrects)
PROPORTION_TRAITEE = {1: "La totalité", 2: "Une partie", 3: "Aucune partie"}

# II.12 — Traitement pratiqué (labels Stata déjà corrects)
TRAITEMENT_PRATIQUE = {1: "Oui — la totalité", 2: "Oui — une partie", 3: "Non"}

# II.13 — Bennes tasseuses (labels20 : 1=Oui, 2=Non). Toute autre valeur -> NaN.
ACCES_BENNE = {1: "Oui", 2: "Non"}

# II.15 — Responsable évacuation (labels Stata déjà corrects)
RESPONSABLE_EVACUATION = {
    1: "Chef de ménage",
    2: "Conjoint du CM",
    3: "Femme de ménage",
    4: "Autre membre féminin de plus de 12 ans",
    5: "Autre membre féminin de 12 ans ou moins",
    6: "Autre membre masculin de plus de 12 ans",
    7: "Autre membre masculin de 12 ans ou moins",
}

# II.16 — Distance point collecte (labels Stata déjà corrects)
DISTANCE_COLLECTE = {1: "Proche", 2: "Acceptable", 3: "Éloignée"}

# II.19 — Fréquence benne (labels Stata déjà corrects)
FREQUENCE_BENNE = {1: "Régulière", 2: "Pas régulière"}

# II.20 — Satisfaction collecte benne (labels Stata déjà corrects)
SATISFACTION_BENNE = {1: "Très bon", 2: "Bon", 3: "Mauvais", 4: "Très mauvais"}

# II.22 — Service alternatif (codes string)
SERVICE_ALTERNATIF = {
    "1":     "Charrettes / brouettes / pousse-pousse",
    "2":     "Société de pré-collecte",
    "3":     "Associations communautaires",
    "other": "Autre",
}

# II.23 — Raison préférence service alternatif (codes string)
RAISON_SERVICE_ALTERNATIF = {
    "1":     "Meilleure qualité",
    "2":     "Plus accessible",
    "3":     "Plus serviable",
    "4":     "Plus disponible",
    "other": "Autre",
}

# II.25_1 — Tranche montant (labels Stata déjà corrects)
MONTANT_EVACUATION = {
    1: "Moins de 200 FCFA",
    2: "Entre 200 et 400 FCFA",
    3: "Entre 401 et 1 000 FCFA",
    4: "Entre 1 001 et 2 000 FCFA",
    5: "Plus de 2 000 FCFA",
}

# II.25_2 — Fréquence paiement (labels Stata — valeur 4 absent des données mais prévu)
FREQUENCE_PAIEMENT = {1: "Par jour", 2: "Par semaine", 3: "Par mois", 4: "Par an"}

# Proxy montant médian FCFA et facteur de conversion vers mensuel
MONTANT_MEDIAN_FCFA  = {1: 100, 2: 300, 3: 700, 4: 1500, 5: 2500}
FREQ_TO_MONTHLY      = {1: 30, 2: 4.33, 3: 1, 4: 1/12}

# ---------------------------------------------------------------------------
# MODULE III — Quartier
# ---------------------------------------------------------------------------

SATISFACTION_4PT = {
    1: "Très bon / Très satisfait",
    2: "Bon / Satisfait",
    3: "Mauvais / Pas satisfait",
    4: "Très mauvais / Pas du tout satisfait",
}

FREQUENCE_COMPORTEMENT = {
    1: "Oui, très souvent",
    2: "Oui, rarement",
    3: "Non, jamais",
}

# III.4 — Raison insatisfaction bacs
RAISON_INSATISFACTION_BACS = {
    "1":     "Pas suivi ou non-respect",
    "2":     "Insuffisance",
    "3":     "Les poubelles ne sont pas vidées",
    "other": "Autre",
}

# III.12 — Dépôts sauvages
DEPOTS_SAUVAGES = {1: "Oui, fréquemment", 2: "Oui, rarement", 3: "Non, jamais"}

# III.13 — Dernier dépôt sauvage
DERNIER_DEPOT = {1: "Moins de 2 jours", 2: "2 à 7 jours", 3: "Plus de 7 jours"}

# III.23 — Gestionnaire place publique (codes string)
GESTIONNAIRE_PLACE = {
    "1":     "UCG",
    "2":     "Mairie",
    "3":     "Service privé",
    "4":     "Association du quartier",
    "5":     "NSP",
    "6":     "Personne",
    "other": "Autre",
}

# III.26 — Gestionnaire marché (codes string)
GESTIONNAIRE_MARCHE = {
    "1":     "UCG",
    "2":     "Mairie",
    "3":     "Les commerçants",
    "4":     "Service privé",
    "5":     "Association du quartier",
    "6":     "NSP",
    "other": "Autre / Personne",
}

# III.30 — Organisateur campagne
ORGANISATEUR_CAMPAGNE = {
    "1":     "UCG",
    "2":     "Service d'hygiène",
    "other": "Autre",
}

# ---------------------------------------------------------------------------
# DÉPARTEMENT — dérivé de la commune (région de Dakar = 4 départements)
# ---------------------------------------------------------------------------
DEPARTEMENT = {1: "Dakar", 2: "Pikine", 3: "Rufisque", 4: "Guédiawaye"}

# Libellés des communes (value label labels0 du brut)
COMMUNE_LIBELLE = {
    1: "Bambylor", 2: "Biscuiterie", 3: "Mermoz / Sacré-Cœur", 4: "Cambérène",
    5: "Colobane / Fass / Gueule Tapée", 6: "Bargny", 7: "Diamniadio",
    8: "Jaxaay / Parcelles / Niakoul Rap", 9: "Sangalkam", 10: "Sébikotane",
    11: "Sendou", 12: "Dalifort", 13: "Diack Sao", 14: "Diamaguène / Sicap M'Bao",
    15: "Dieuppeul Derklé", 16: "Djidah Thiaroye Kao", 17: "Fann / Point E / Amitié",
    18: "Golf Sud", 19: "Gorée", 20: "Grand Dakar", 21: "Grand Yoff",
    22: "Guinaw Rail Nord", 23: "Guinaw Rail Sud", 24: "Hann / Bel Air", 25: "HLM",
    26: "Keur Massar", 27: "M'Bao", 28: "Malika", 29: "Médina", 30: "Médina Gounass",
    31: "N'Diarème Limamoulaye", 32: "N'Gor", 33: "Ouakam", 34: "Parcelles Assainies",
    35: "Patte d'Oie", 36: "Pikine Est", 37: "Pikine Ouest", 38: "Pikine Sud",
    39: "Plateau", 40: "Rufisque Centre (Nord)", 41: "Rufisque Est", 42: "Rufisque Ouest",
    43: "Sam Notaire", 44: "Sicap Liberté", 45: "Thiaroye / Mer", 46: "Thiaroye Gare",
    47: "Tivaouane Peulh-Niagha", 48: "Wakhinane Nimzatt", 49: "Yène",
    50: "Yeumbeul Nord", 51: "Yeumbeul Sud", 52: "Yoff",
}

# Crosswalk commune -> département (découpage administratif 2018, avant la
# création du département de Keur Massar en 2021).
# NB : si tu veux le découpage POST-2021, déplace les communes 8, 26, 28, 50, 51
#      de "Pikine" vers "Keur Massar".
COMMUNE_DEPARTEMENT = {
    # Dakar (19)
    2: "Dakar", 3: "Dakar", 4: "Dakar", 5: "Dakar", 15: "Dakar", 17: "Dakar",
    19: "Dakar", 20: "Dakar", 21: "Dakar", 24: "Dakar", 25: "Dakar", 29: "Dakar",
    32: "Dakar", 33: "Dakar", 34: "Dakar", 35: "Dakar", 39: "Dakar", 44: "Dakar",
    52: "Dakar",
    # Guédiawaye (5)
    18: "Guédiawaye", 30: "Guédiawaye", 31: "Guédiawaye", 43: "Guédiawaye",
    48: "Guédiawaye",
    # Pikine (16 — inclut les futures communes de Keur Massar)
    8: "Pikine", 12: "Pikine", 14: "Pikine", 16: "Pikine", 22: "Pikine",
    23: "Pikine", 26: "Pikine", 27: "Pikine", 28: "Pikine", 36: "Pikine",
    37: "Pikine", 38: "Pikine", 45: "Pikine", 46: "Pikine", 50: "Pikine",
    51: "Pikine",
    # Rufisque (12)
    1: "Rufisque", 6: "Rufisque", 7: "Rufisque", 9: "Rufisque", 10: "Rufisque",
    11: "Rufisque", 13: "Rufisque", 40: "Rufisque", 41: "Rufisque", 42: "Rufisque",
    47: "Rufisque", 49: "Rufisque",
}

# II.10 — Raison de non-revente (labels14), centralisé ici
RAISON_NON_REVENTE = {
    1: "N'en a pas connaissance",
    2: "Revenus faibles",
    3: "Ne connaît pas les modes de revente",
    4: "N'a pas le temps nécessaire",
    5: "N'est pas intéressé",
}

# ---------------------------------------------------------------------------
# SEUILS QC
# ---------------------------------------------------------------------------
QC_AGE_MIN            = 15
QC_AGE_MAX            = 110
QC_TAILLE_MAX         = 50
QC_DUREE_QUARTIER_MAX = 600
QC_MISSING_THRESH     = 0.50

# ---------------------------------------------------------------------------
# VARIABLES ABSENTES — documentation
# ---------------------------------------------------------------------------
VARS_ABSENTES = {
    "milieu_residence":    "Non collectée. Toute la zone est urbaine (région de Dakar).",
    "depenses_menage":     "Non collectée. Proxy construit via statut occupation + type logement + paiement déchets.",
    "actifs_menage":       "Non collectée. Inclus dans le proxy niveau de vie.",
    "revenu_CM":           "Non collecté dans ce questionnaire. Proxy via statut occupation et paiement service déchets.",
    "situation_matrimoniale_CM": "Non collectée dans ce questionnaire.",
    "statut_emploi_CM":    "Non collecté dans ce questionnaire.",
    "secteur_emploi_CM":   "Non collecté dans ce questionnaire.",
}
# NB : 'region' et 'departement' NE SONT PLUS absentes — region est fixée à
# "Dakar" et departement est dérivé de la commune via COMMUNE_DEPARTEMENT.
