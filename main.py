"""
main.py — API FastAPI pour le pipeline de traitement des déchets ménagers
Déployable sur Render.com
"""

import io
import os
import sys
import uuid
import logging
import tempfile
import zipfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pipeline Déchets Ménagers",
    description="API de traitement de l'enquête sur la gestion des ordures ménagères — ENSAE/UCG",
    version="1.0.0",
)

templates = Jinja2Templates(directory="templates")

# ---------------------------------------------------------------------------
# Route principale — interface web
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------------------------------------------------------------------
# Route API — traitement du fichier
# ---------------------------------------------------------------------------

@app.post("/api/process")
async def process_file(file: UploadFile = File(...)):
    """
    Reçoit un fichier .dta, lance le pipeline, retourne un ZIP contenant :
    - dataset_dechets.csv
    - dataset_dechets.dta
    - QAQC_rapport.xlsx
    """

    # Validation du format
    if not file.filename.endswith(".dta"):
        raise HTTPException(
            status_code=400,
            detail="Format invalide. Seuls les fichiers .dta (Stata) sont acceptés."
        )

    # Créer un répertoire temporaire pour ce traitement
    tmp_dir = Path(tempfile.mkdtemp())
    input_dir  = tmp_dir / "input"
    output_dir = tmp_dir / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Sauvegarder le fichier uploadé
    input_path = input_dir / "Base.dta"
    content = await file.read()
    with open(input_path, "wb") as f:
        f.write(content)

    logger.info(f"Fichier reçu : {file.filename} ({len(content)/1024:.0f} KB)")

    # Lancer le pipeline
    try:
        import importlib
        import config, loader, builder, qaqc, exporter

        # Patcher dynamiquement les chemins pour ce traitement
        config.INPUT_DIR  = str(input_dir)
        config.OUTPUT_DIR = str(output_dir)
        config.INPUT_FILE = "Base.dta"

        # Recharger les modules pour prendre en compte les nouveaux chemins
        importlib.reload(loader)
        importlib.reload(exporter)

        qc_log = []
        df_raw, meta = loader.run(qc_log)
        df_final     = builder.run(df_raw)

        # Export
        csv_path  = str(output_dir / "dataset_dechets.csv")
        dta_path  = str(output_dir / "dataset_dechets.dta")
        qaqc_path = str(output_dir / "QAQC_rapport.xlsx")

        df_final.to_csv(csv_path, index=False, encoding="utf-8-sig")

        import pyreadstat
        df_stata, _ = exporter._prepare_for_stata(df_final)
        pyreadstat.write_dta(df_stata, dta_path,
                             file_label="Enquête déchets ménagers — données traitées")

        qaqc.run(df_raw, df_final, qc_log, qaqc_path)

        logger.info(f"Pipeline terminé : {df_final.shape[0]} ménages, {df_final.shape[1]} variables")

    except Exception as e:
        logger.error(f"Erreur pipeline : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement : {str(e)}")

    # Créer un ZIP avec les 3 fichiers de sortie
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(csv_path,  "dataset_dechets.csv")
        zf.write(dta_path,  "dataset_dechets.dta")
        zf.write(qaqc_path, "QAQC_rapport.xlsx")
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=resultats_pipeline.zip"}
    )


# ---------------------------------------------------------------------------
# Route API — statut et informations
# ---------------------------------------------------------------------------

@app.get("/api/info")
async def info():
    """Retourne les informations sur le pipeline."""
    return JSONResponse({
        "pipeline": "Enquête Déchets Ménagers — ENSAE/UCG 2018",
        "version": "1.0.0",
        "format_accepte": ".dta (Stata)",
        "outputs": [
            "dataset_dechets.csv — Table analytique finale (132 variables)",
            "dataset_dechets.dta — Table analytique finale (Stata)",
            "QAQC_rapport.xlsx — Rapport qualité 6 onglets"
        ],
        "blocs": {
            "A_menage":       "Commune, habitat, taille, proxy niveau de vie",
            "B_cm":           "Sexe, âge, instruction, alphabétisation du CM",
            "C_dechets":      "Stockage, évacuation, traitement, satisfaction, nuisibles",
            "D_consequences": "Maladies déclarées, indicateurs sanitaires"
        }
    })


# ---------------------------------------------------------------------------
# Lancement local
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
