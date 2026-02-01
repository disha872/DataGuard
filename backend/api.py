from fastapi import FastAPI, UploadFile, File
import pandas as pd
import io
from fastapi.encoders import jsonable_encoder
from backend.data_profiling import profile_dataset
from backend.data_validation import validate_dataset

app = FastAPI(
    title="DataGuard API",
    description="Data Quality Validation API",
    version="1.0"
)

@app.get("/")
def root():
    return {"message": "Welcome to DataGuard API"}

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))

        profile_result = profile_dataset(df)
        validation_result = validate_dataset(df, profile_result)

        result = {
            "profile": profile_result,
            "validation": validation_result
        }

        # 🔑 convert numpy/pandas objects to JSON-safe types
        return jsonable_encoder(result)

    except Exception as e:
        return {"error": str(e)}
