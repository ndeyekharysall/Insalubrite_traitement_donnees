# Pipeline de traitement — Enquête Déchets Ménagers

Pipeline de nettoyage, construction de variables analytiques et contrôle qualité
des données d'une enquête sur la gestion des déchets ménagers et l'insalubrité.

À partir d'un fichier d'enquête brut (`.dta`), le pipeline produit une table
analytique propre et labellisée (CSV + Stata) ainsi qu'un rapport de contrôle
qualité (QAQC) au format Excel.

---

## 1. Structure du projet

```
Insalubrite_traitement_donnees/
├── input/                  # Fichier(s) source de l'enquête (.dta)
│   └── Base.dta
├── output/                 # Fichiers produits par le pipeline
│   ├── dataset_dechets.csv
│   ├── dataset_dechets.dta
│   ├── QAQC_rapport.xlsx
│   └── pipeline_AAAAMMJJ_HHMMSS.log
└── src/                    # Code source
    ├── run_pipeline.py     # Orchestrateur principal (point d'entrée)
    ├── config.py           # Configuration centrale : mappings de labels & seuils QC
    ├── loader.py           # Chargement, nettoyage des types, contrôles qualité
    ├── builder.py          # Construction des variables analytiques (4 blocs)
    ├── exporter.py         # Export CSV + Stata avec labels de variables
    └── qaqc.py             # Génération du rapport QAQC multi-onglets
```

---

## 2. Prérequis

- **Python 3.11+**
- Dépendances Python :

```bash
pip install pandas numpy pyreadstat openpyxl
```

| Paquet       | Usage                                          |
|--------------|------------------------------------------------|
| `pandas`     | Manipulation des données                       |
| `numpy`      | Opérations numériques / gestion des NaN        |
| `pyreadstat` | Lecture et écriture des fichiers Stata `.dta`  |
| `openpyxl`   | Génération du rapport Excel QAQC               |

---

## 3. Exécution

Depuis la racine du projet :

```bash
python src/run_pipeline.py
```

Le script lit le fichier configuré dans `config.py` (`INPUT_FILE`, par défaut
`Base.dta`) dans le dossier `input/`, puis écrit tous les résultats dans
`output/`.

> **Note encodage (Windows)** : la console Windows (cp1252) peut ne pas afficher
> certains caractères Unicode des logs (ex. `→`). Le fichier `.log` écrit dans
> `output/` est en UTF-8 et reste complet. Pour un affichage console propre :
>
> ```bash
> set PYTHONUTF8=1   &&   python src/run_pipeline.py     # cmd
> $env:PYTHONUTF8=1  ;    python src/run_pipeline.py     # PowerShell
> ```

---

## 4. Déroulé du pipeline

Le pipeline s'exécute en **4 étapes** orchestrées par `run_pipeline.py` :

### Étape 1 — Chargement & contrôle qualité (`loader.py`)
- Lecture du `.dta` via `pyreadstat`.
- **Nettoyage des types** (`clean_types`) : conversion des codes numériques,
  nettoyage des chaînes, gestion des valeurs vides → NaN.
- **Contrôles qualité** (`quality_checks`) : détection d'outliers (âges, taille
  de ménage), cohérences logiques (skip patterns), taux de manquants élevés.
  Chaque anomalie est journalisée dans `qc_log` (alimente le rapport QAQC).

> Les contrôles sont **défensifs** : si une variable attendue est absente du
> fichier, elle est signalée dans les logs et dans le `qc_log`, et le contrôle
> correspondant est simplement ignoré (pas d'interruption du pipeline).

### Étape 2 — Construction des variables analytiques (`builder.py`)
Transforme les variables brutes en variables propres, labellisées et dérivées,
organisées en **4 blocs** :

| Bloc | Contenu |
|------|---------|
| **A — Ménage**        | Identifiants géographiques, composition et taille du ménage, statut d'occupation, type d'habitat, proxy niveau de vie |
| **B — Chef de ménage**| Sexe, âge et tranche d'âge, statut du répondant, niveau d'études, alphabétisation |
| **C — Déchets**       | Sources et natures des déchets, stockage, tri/revente, traitement, accès aux services (bennes, alternatifs), montants payés, infrastructure et environnement du quartier |
| **D — Conséquences**  | Maladies déclarées, nuisibles, indicateurs sanitaires synthétiques |

L'accès aux colonnes brutes passe par un helper `_col()` : si une colonne attendue
est absente, les variables qui en dérivent sont mises à `NaN` (avec un
avertissement journalisé) au lieu de provoquer une erreur.

### Étape 3 — Export (`exporter.py`)
- **`dataset_dechets.csv`** : UTF-8 avec BOM (compatibilité Excel).
- **`dataset_dechets.dta`** : Stata, avec labels de variables. Les noms de
  colonnes > 32 caractères sont automatiquement raccourcis (limite Stata) ;
  le raccourcissement est journalisé.

### Étape 4 — Rapport QAQC (`qaqc.py`)
Génère **`QAQC_rapport.xlsx`**, classeur Excel mis en forme et multi-onglets :

| Onglet | Contenu |
|--------|---------|
| `01_Résumé`              | Dimensions brut/traité, nombre d'anomalies, taux de complétion global |
| `02_Anomalies_QC`        | Log détaillé des anomalies détectées en étape 1 |
| `03_Manquants`           | Taux de valeurs manquantes par variable, avec statut (OK / Modéré / Élevé) |
| `04_Estimations_Primaires` | Distributions (%) par bloc thématique + statistiques de la taille des ménages |
| `05_Montant_Evacuation`  | Statistiques sur le montant mensuel d'évacuation (proxy FCFA) |
| `06_Variables_Absentes`  | Documentation des variables non collectées directement |

---

## 5. Configuration (`config.py`)

Tout est centralisé dans `config.py`. Les éléments paramétrables :

- **Chemins** : `INPUT_DIR`, `OUTPUT_DIR`, `INPUT_FILE`.
- **Mappings de labels** : dictionnaires code → libellé pour chaque variable
  catégorielle (sexe, statut d'occupation, mode de stockage, satisfaction, etc.).
- **Seuils de contrôle qualité** :

  | Paramètre | Valeur par défaut | Rôle |
  |-----------|-------------------|------|
  | `QC_AGE_MIN` / `QC_AGE_MAX` | 15 / 110 | Bornes d'âge réalistes |
  | `QC_TAILLE_MAX`             | 50       | Taille de ménage maximale réaliste |
  | `QC_DUREE_QUARTIER_MAX`     | 600      | Durée max dans le quartier (mois) |
  | `QC_MISSING_THRESH`         | 0.50     | Seuil d'alerte sur le taux de manquants |

- **`VARS_ABSENTES`** : note documentaire sur les variables attendues mais non
  collectées directement (reportée dans le rapport QAQC).

### Adapter le pipeline à une nouvelle édition de l'enquête
La logique du pipeline est volontairement stable. Pour une nouvelle édition :

1. Placer le fichier source dans `input/` (adapter `INPUT_FILE` si le nom change).
2. Mettre à jour les **mappings de `config.py`** si les codes des modalités ont changé.
3. Relancer `python src/run_pipeline.py`.

---

## 6. Fichiers produits (`output/`)

| Fichier | Description |
|---------|-------------|
| `dataset_dechets.csv`        | Table analytique finale (CSV UTF-8 BOM) |
| `dataset_dechets.dta`        | Table analytique finale (Stata, avec labels) |
| `QAQC_rapport.xlsx`          | Rapport de contrôle qualité multi-onglets |
| `pipeline_AAAAMMJJ_HHMMSS.log` | Journal d'exécution horodaté |
