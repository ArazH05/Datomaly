from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

import pandas as pd
import io

from app.services.profiler import (
    profile_dataframe
)

from app.services.recommender import (
    generate_recommendations
)


router = APIRouter()


@router.post("/upload")
async def upload_dataset(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail=(
                "For now, Datomaly only "
                "supports CSV files."
            )
        )

    try:
        contents = await file.read()

        dataframe = pd.read_csv(
            io.BytesIO(contents)
        )

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Could not read CSV file: "
                f"{str(error)}"
            )
        )

    profile = profile_dataframe(
        dataframe
    )

    recommendations = (
        generate_recommendations(
            profile
        )
    )

    return {
        "filename": file.filename,
        "profile": profile,
        "recommendations": recommendations
    }