# 🗑️ Pipeline de Traitement — Enquête sur la Gestion des Ordures Ménagères
### ENSAE · UCG · Région de Dakar · 2018

---

## 📋 Présentation

Ce projet implémente un **pipeline de traitement de données reproductible et scalable ** pour l'enquête sur la gestion des ordures ménagères dans la région de Dakar au Sénégal, menée conjointement par l'ENSAE et l'UCG (Unité de Coordination de la Gestion des Déchets Solides).

Le pipeline extrait, nettoie, transforme et stocke les données brutes (format Stata `.dta`) en une table analytique consolidée, accompagnée d'un rapport de contrôle qualité.

Il est également accessible via une **interface web + API REST**, permettant à n'importe quel membre de l'équipe de traiter une nouvelle édition de l'enquête sans toucher au code.

---

## 🏗️ Structure du projet

```
Groupe5_Insalubrite_traitement_donnees/
│
├── input/                    ← Données brutes (non versionnées sur GitHub)
│   └── Base.dta
│
├── output/                   ← Résultats générés automatiquement
│   ├── dataset_dechets.csv   
│   ├── dataset_dechets.dta   
│   ├── QAQC_rapport.xlsx     
│   └── pipeline_YYYYMMDD.log 
│
├── src/                      ← Code source du pipeline
│   ├── config.py             ← ⚙️  Mappings et paramètres centralisés
│   ├── loader.py             ← 📥  Chargement, nettoyage, contrôles qualité
│   ├── builder.py            ← 🔨  Construction des variables analytiques
│   ├── qaqc.py               ← 📊  Rapport qualité Excel
│   ├── exporter.py           ← 📤  Export CSV et Stata
│   └── run_pipeline.py       ← ▶️   Orchestrateur principal
│
├── templates/
│   └── index.html            ← Interface web (upload + téléchargement)
│
├── main.py                   ← API FastAPI
├── requirements.txt          ← Dépendances Python
├── render.yaml               ← Configuration déploiement Render
├── .gitignore
└── README.md
```

---

## 📦 Variables produites (132 au total)

### Bloc A — Caractéristiques du ménage (12 variables)
| Variable | Description |
|---|---|
| `commune_code` | Code commune |
| `quartier` | Quartier de l'enquête |
| `zone` | Zone géographique (Région de Dakar — urbain) |
| `taille_menage` | Taille totale du ménage |
| `nb_enfants_0_4` | Nombre d'enfants de moins de 5 ans |
| `nb_enfants_5_15` | Nombre d'enfants de 5 à 15 ans |
| `nb_adultes_H` | Nombre d'hommes adultes (15+) |
| `nb_adultes_F` | Nombre de femmes adultes (15+) |
| `statut_occupation` | Locataire / Propriétaire / Logé par un tiers |
| `type_habitat` | Case·Baraque / Maison basse / Maison en étage / Appartement |
| `proxy_niveau_vie` | Score proxy niveau de vie (0–3) |
| `proxy_niveau_vie_label` | Faible / Moyen-bas / Moyen-haut / Élevé |

> **Note :** Région, département, milieu de résidence, dépenses et actifs du ménage ne sont pas collectés directement. Le proxy niveau de vie est construit à partir du statut d'occupation, du type de logement et du paiement du service d'évacuation.

### Bloc B — Caractéristiques du Chef de Ménage (19 variables)
| Variable | Description |
|---|---|
| `cm_sexe` | Homme / Femme |
| `cm_age` | Âge en années |
| `cm_tranche_age` | Moins de 25 ans / 25–34 / 35–44 / 45–59 / 60 ans et plus |
| `cm_type_enseignement` | École française / arabe / coranique / Aucun |
| `cm_niveau_instruction` | Primaire / Secondaire / Supérieur |
| `cm_est_alphabetise` | Alphabétisé dans au moins une langue |
| `cm_alpha_francais` | Alphabétisé en français |
| `cm_alpha_anglais` | Alphabétisé en anglais |
| `cm_alpha_arabe` | Alphabétisé en arabe |
| `cm_alpha_lng_nationale` | Alphabétisé en langue nationale |
| `repondant_statut` | Lien du répondant avec le CM |
| `repondant_est_cm` | Le répondant est-il le CM ? |

> **Note :** Situation matrimoniale, statut d'emploi, secteur d'emploi et revenu du CM ne sont pas collectés dans ce questionnaire.

### Bloc C — Gestion des déchets ménagers (87 variables)
Variables clés :

| Variable | Description |
|---|---|
| `sources_liste` | Sources de déchets (liste textuelle) |
| `natures_liste` | Natures des déchets |
| `mode_stockage` | Poubelle / Seau / Fût / Carton / Sac |
| `stockage_couvert` | Récipient fermé ou couvert |
| `tri_avant_evacuation` | Pratique du tri |
| `revente_dechets` | Revente de déchets |
| `au_moins_un_traitement` | Enfouissement / Incinération / Recyclage / Compostage |
| `acces_benne_tasseuse` | Accès au service public de collecte |
| `benne_usage_regulier` | Utilisation régulière de la benne |
| `satisfaction_benne` | Très bon / Bon / Mauvais / Très mauvais |
| `service_alternatif_type` | Charrette / Pré-collecte / Association |
| `service_evacuation_payant` | Service payant ? |
| `montant_mensuel_evacuation_fcfa` | Montant mensuel estimé (0 si gratuit) |
| `acces_depotoire_normalise` | Accès à un bac ou corbeille de rue |
| `depots_sauvages_observes` | Fréquence des dépôts sauvages dans le quartier |
| `nuisibles_liste` | Moustiques / Mouches / Cafards / Souris / Rats |
| `connait_UCG` | Connaissance de l'UCG |

### Bloc D — Conséquences sanitaires (14 variables)
| Variable | Description |
|---|---|
| `maladies_liste` | Maladies déclarées (liste textuelle) |
| `nb_maladies` | Nombre de types de maladies déclarées |
| `aucune_maladie` | Aucune maladie déclarée (0/1) |
| `maladie_liee_dechets` | Au moins une maladie potentiellement liée aux déchets |
| `maladie_asthme` ... | Détail par maladie |

---

## ⚙️ Installation et exécution

### Prérequis
- Python 3.10 ou supérieur
- pip

### 1. Cloner le projet
```bash
git clone https://github.com/ndeyekharysall/Insalubrite_traitement_donnees
cd Groupe5_Insalubrite_traitement_donnees
```

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Placer les données
Copier votre fichier `Base.dta` dans le dossier `input/` :
```
input/Base.dta
```

### 4a. Lancer le pipeline en ligne de commande
```bash
cd src
python run_pipeline.py
```
Les résultats apparaissent dans `output/`.

### 4b. Lancer la plateforme web
```bash
uvicorn main:app --reload
```
Ouvrir http://localhost:8000 dans votre navigateur.

---

## 🌐 Utiliser l'API

### Via l'interface web
1. Ouvrir http://localhost:8000
2. Glisser-déposer votre fichier `.dta`
3. Cliquer **Lancer le pipeline**
4. Télécharger le ZIP contenant les 3 fichiers de sortie

### Via curl (ligne de commande)
```bash
# Traiter un fichier
curl -X POST "http://localhost:8000/api/process" \
  -F "file=@input/Base.dta" \
  --output resultats.zip

# Informations sur le pipeline
curl http://localhost:8000/api/info
```

### Documentation interactive (Swagger)
```
http://localhost:8000/docs
```

---

## 🚀 Déploiement en ligne sur Render

1. Pousser le projet sur GitHub
2. Créer un compte sur [render.com](https://render.com)
3. New → **Web Service** → connecter votre repo GitHub
4. Render détecte automatiquement `render.yaml`
5. Cliquer **Deploy**

Votre plateforme est accessible en ligne à l'URL fournie par Render.

---

## 🔄 Adapter le pipeline à une nouvelle édition

Le pipeline est conçu pour être **scalable**. Pour une nouvelle édition de l'enquête avec les mêmes modules :

1. Placer le nouveau fichier `.dta` dans `input/`
2. Ouvrir `src/config.py` et vérifier que les codes correspondent au nouveau questionnaire
3. Relancer `python src/run_pipeline.py`

**Aucune modification** des autres fichiers n'est nécessaire si la structure du questionnaire est identique.

---

## 🧪 Contrôle qualité

Le fichier `QAQC_rapport.xlsx` contient 6 onglets :

| Onglet | Contenu |
|---|---|
| 01_Résumé | Dimensions, taux de complétion global |
| 02_Anomalies_QC | Log des 49 anomalies détectées |
| 03_Manquants | Taux de valeurs manquantes par variable |
| 04_Estimations_Primaires | Distributions de toutes les variables clés |
| 05_Montant_Evacuation | Statistiques sur les montants mensuels |
| 06_Variables_Absentes | Documentation des variables non collectées |

---

## 👥 Équipe

Groupe 5 — ENSAE AS3 · 2025–2026  
Projet : Insalubrité et Gestion des Déchets Ménagers  
Encadrement : UCG (Unité de Coordination de la Gestion des Déchets Solides)

---

## 📄 Licence

Projet académique — ENSAE Dakar. Données confidentielles, usage pédagogique uniquement.
