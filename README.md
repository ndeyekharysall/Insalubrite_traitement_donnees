# Pipeline Déchets Ménagers — ENSAE / UCG
## Plateforme Web + API

---

## Lancer en local

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Ouvrir http://localhost:8000

---

## Déployer sur Render (gratuit)

1. Créer un compte sur https://render.com
2. New → Web Service → connecter votre dépôt GitHub
3. Render détecte automatiquement `render.yaml`
4. Cliquer **Deploy**

Votre API sera disponible à l'adresse :
`https://pipeline-dechets-menagers.onrender.com`

---

## Utiliser l'API directement (sans interface)

### Traiter un fichier
```bash
curl -X POST "http://localhost:8000/api/process" \
  -F "file=@Base.dta" \
  --output resultats.zip
```

### Informations sur le pipeline
```bash
curl http://localhost:8000/api/info
```

### Documentation interactive (Swagger)
```
http://localhost:8000/docs
```

---

## Structure du projet

```
plateforme/
├── main.py              ← API FastAPI
├── requirements.txt     ← dépendances Python
├── render.yaml          ← config déploiement Render
├── README.md
├── templates/
│   └── index.html       ← interface web
└── src/
    ├── config.py        ← mappings et paramètres (à adapter si nouvelle édition)
    ├── loader.py        ← chargement et contrôles qualité
    ├── builder.py       ← construction des variables analytiques
    ├── qaqc.py          ← rapport de qualité Excel
    └── exporter.py      ← export CSV et DTA
```

---

## Pour une nouvelle édition de l'enquête

1. Mettre à jour `src/config.py` si les codes ont changé
2. Déposer le nouveau fichier `.dta` sur la plateforme
3. Le pipeline s'adapte automatiquement
