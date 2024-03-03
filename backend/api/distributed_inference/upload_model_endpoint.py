# NOTE: This is designed to be an internal endpoint used by the user, not in any way exposed to the actually public api.

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
from zipfile import ZipFile
import traceback
import shutil

router = APIRouter()

MODEL_DIR = os.getenv("MODEL_DIR", "backend/models")


@router.post("/upload-model", tags=["Model Management"])
async def upload_model(file: UploadFile = File(...)):
    # Ensure the MODEL_DIR exists
    os.makedirs(MODEL_DIR, exist_ok=True)

    try:
        # Adjust the following line if you'd like to alter the path or naming convention for saved models
        model_path = os.path.join(MODEL_DIR, file.filename)

        if not file.filename.endswith(".zip"):
            raise HTTPException(
                status_code=400,
                detail="Only .zip files containing model data are accepted.",
            )

        # Save the uploaded zip file to the filesystem
        with open(model_path, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        # Optionally, you can unzip the file and organize contents here
        # Ensure that you handle potential security issues with unzipping carefully
        with ZipFile(model_path, "r") as zip_ref:
            model_extraction_path = os.path.splitext(model_path)[0]
            zip_ref.extractall(
                model_extraction_path
            )  # Extract into a subdirectory named after the file (sans ".zip")

        return JSONResponse(
            content={"message": "Model uploaded successfully."}, status_code=200
        )
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
