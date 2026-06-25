# =============================================================================
# config.py — Configuration centrale — validée sur questionnaire ENSAE/UCG 2018
# =============================================================================

import os

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR   = os.path.join(BASE_DIR, "input")
OUTPUT_DIR  = os.path.join(BASE_DIR, "output")
INPUT_FILE  = "Base.dta"

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

# II.13 — Bennes tasseuses (1=Oui, 2=Non, valeurs 3-6 = codes enquête mobile non définis)
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
# DÉPARTEMENT (page de garde questionnaire)
# ---------------------------------------------------------------------------
DEPARTEMENT = {1: "Dakar", 2: "Pikine", 3: "Rufisque", 4: "Guédiawaye"}

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
    "region":              "Non collectée directement. L'enquête couvre uniquement la région de Dakar.",
    "departement":         "Présent dans l'identifiant questionnaire (Dép/Commune/N°Enquêteur/N°Quest) mais pas comme variable séparée dans la base.",
    "milieu_residence":    "Non collectée. Toute la zone est urbaine (région de Dakar).",
    "depenses_menage":     "Non collectée. Proxy construit via statut occupation + type logement + paiement déchets.",
    "actifs_menage":       "Non collectée. Inclus dans le proxy niveau de vie.",
    "revenu_CM":           "Non collecté. Proxy via statut occupation et paiement service déchets.",
    "situation_matrimoniale_CM": "Non collectée dans ce questionnaire.",
    "statut_emploi_CM":    "Non collecté dans ce questionnaire.",
    "secteur_emploi_CM":   "Non collecté dans ce questionnaire.",
}
