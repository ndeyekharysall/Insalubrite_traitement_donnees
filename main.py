# =============================================================================
# main.py — API FastAPI pour le pipeline de traitement des déchets ménagers
# Pages : /  (accueil)   /app  (application)
# API   : POST /api/process  -> JSON {stats, fichiers base64}
# =============================================================================

import os
import sys
import base64
import shutil
import logging
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Pipeline Déchets Ménagers",
    description="API de traitement de l'enquête sur la gestion des ordures ménagères — ENSAE/UCG",
    version="2.0.0",
)

templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
from pathlib import Path
from fastapi.responses import HTMLResponse

TEMPLATES_DIR = Path(__file__).parent / "templates"

@app.get("/", response_class=HTMLResponse)
async def accueil():
    return HTMLResponse((TEMPLATES_DIR / "acueil.html").read_text(encoding="utf-8"))

@app.get("/app", response_class=HTMLResponse)
async def application():
    return HTMLResponse((TEMPLATES_DIR / "app.html").read_text(encoding="utf-8"))

@app.get("/equipe", response_class=HTMLResponse)
async def equipe():
    return HTMLResponse((TEMPLATES_DIR / "equipe.html").read_text(encoding="utf-8"))

# ---------------------------------------------------------------------------
# API — traitement du fichier
# ---------------------------------------------------------------------------

def _encode_file(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


@app.post("/api/process")
async def process_file(file: UploadFile = File(...)):
    """
    Reçoit un .dta, lance le pipeline et renvoie un JSON :
    { success, input_filename, stats:{lignes,variables,anomalies}, files:[{key,filename,mime,b64}] }
    """
    if not file.filename.endswith(".dta"):
        raise HTTPException(
            status_code=400,
            detail="Format invalide. Seuls les fichiers .dta (Stata) sont acceptés.",
        )

    tmp_dir = Path(tempfile.mkdtemp())
    input_dir = tmp_dir / "input"
    output_dir = tmp_dir / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    try:
        # Sauvegarder l'upload
        input_path = input_dir / "Base.dta"
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        logger.info(f"Fichier reçu : {file.filename} ({len(content)/1024:.0f} KB)")

        # Pipeline
        import importlib
        import config, loader, builder, qaqc, exporter

        config.INPUT_DIR = str(input_dir)
        config.OUTPUT_DIR = str(output_dir)
        config.INPUT_FILE = "Base.dta"
        importlib.reload(loader)
        importlib.reload(exporter)

        qc_log = []
        df_raw, meta = loader.run(qc_log)
        df_final = builder.run(df_raw)

        csv_path = str(output_dir / "dataset_dechets.csv")
        dta_path = str(output_dir / "dataset_dechets.dta")
        qaqc_path = str(output_dir / "QAQC_rapport.xlsx")

        df_final.to_csv(csv_path, index=False, encoding="utf-8-sig")

        import pyreadstat
        df_stata, _ = exporter._prepare_for_stata(df_final)
        pyreadstat.write_dta(
            df_stata, dta_path,
            file_label="Enquête déchets ménagers — données traitées",
        )

        qaqc.run(df_raw, df_final, qc_log, qaqc_path)

        logger.info(
            f"Pipeline terminé : {df_final.shape[0]} ménages, "
            f"{df_final.shape[1]} variables, {len(qc_log)} signalements QC"
        )

        payload = {
            "success": True,
            "input_filename": file.filename,
            "stats": {
                "lignes": int(df_final.shape[0]),
                "variables": int(df_final.shape[1]),
                "anomalies": int(len(qc_log)),
            },
            "files": [
                {"key": "csv", "filename": "dataset_dechets.csv",
                 "mime": "text/csv", "b64": _encode_file(csv_path)},
                {"key": "dta", "filename": "dataset_dechets.dta",
                 "mime": "application/octet-stream", "b64": _encode_file(dta_path)},
                {"key": "xlsx", "filename": "QAQC_rapport.xlsx",
                 "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                 "b64": _encode_file(qaqc_path)},
            ],
        }
        return JSONResponse(payload)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur pipeline : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement : {e}")
    finally:
        # Nettoyage systématique du répertoire temporaire
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# API — informations
# ---------------------------------------------------------------------------

@app.get("/api/info")
async def info():
    return JSONResponse({
        "pipeline": "Enquête Déchets Ménagers — ENSAE/UCG 2018",
        "version": "2.0.0",
        "format_accepte": ".dta (Stata)",
        "outputs": [
            "dataset_dechets.csv — table analytique finale",
            "dataset_dechets.dta — table analytique finale (Stata)",
            "QAQC_rapport.xlsx — rapport qualité 6 onglets",
        ],
        "blocs": {
            "A_menage": "Commune, département, habitat, taille, proxy niveau de vie",
            "B_cm": "Sexe, âge, instruction, alphabétisation du CM",
            "C_dechets": "Stockage, évacuation, traitement, satisfaction, nuisibles",
            "D_consequences": "Maladies déclarées, indicateurs sanitaires",
        },
    })


# ---------------------------------------------------------------------------
# Lancement local
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)