from fastapi import FastAPI, APIRouter, HTTPException, status, Depends, Response, UploadFile, Query
import uvicorn
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Annotated, List
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from io import StringIO


from app.auth import User, Token, authenticate_user, create_access_token, get_current_user
from app.database import get_db
from app.schemas import Measurement
import app.models as models
from app.database import engine

import pandas as pd

models.Base.metadata.create_all(bind=engine)


description_API = """
This API allows to download moderate monitoring data.
"""

app = FastAPI(
    title = "Eurac - Moderate Store Data",
    description = description_API,
    version = "0.0.1",
    terms_of_service = "http://example.com/terms/",
    contact = {
    },
    license_info = {
        "name" : "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    },
    # openapi_tags=tags_metadata
    docs_url='/store_data/api/docs',
    redoc_url='/store_data/api/redoc',
    openapi_url='/store_data/api/openapi.json'
)


router = APIRouter(prefix="/store_data")


# ======================================================================
#                    SECURITY TOKEN 
# ======================================================================
@router.post("/api/v1/token", response_model=Token, tags = ['Authentication'])
async def login_for_access_token(
    clientID: str,
    secret:str
):
    user = authenticate_user(clientID, secret)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.clientid}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# ======================================================================
#                             MEASUREMENTS 
# ======================================================================


@router.post("/api/v1/measurement")
async def create_measurement(
    current_user: Annotated[User, Depends(get_current_user)],
    measurement: Measurement, db: Session = Depends(get_db)
):
    new_measurement = models.Measurement(**measurement.model_dump())
    db.add(new_measurement)
    db.commit()
    db.refresh(new_measurement)
    return new_measurement


@router.post(
        "/api/v1/measurements", 
        description="Upload a CSV file and save to measurements database. Columns: 'time', 'sensor_id', 'value'.")
async def load_mesurements_from_file(
    current_user: Annotated[User, Depends(get_current_user)],
    file: UploadFile,
    db: Session = Depends(get_db)
):
    content = file.file.read()
    content_str = content.decode('utf-8')
    csv_data = StringIO(content_str)
    df = pd.read_csv(csv_data)

    try:
        df.to_sql("measurement", engine, if_exists="append", index=False)
    except IntegrityError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return f"{file.filename} loaded with success."


@router.get("/api/v1/measurements")
async def get_all_measurements(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int | None = None,
    db: Session = Depends(get_db)
):
    if limit: 
        all_measurements = db.query(models.Measurement).order_by(models.Measurement.time).limit(limit).all()
    else: 
        all_measurements = db.query(models.Measurement).order_by(models.Measurement.time).all()
        
    return all_measurements


@router.get("/api/v1/measurements/{sensor_id}")
async def get_measurements(
    current_user: Annotated[User, Depends(get_current_user)],
    sensor_id: str,
    time_from: datetime | None = None, 
    time_to: datetime | None = None,
    limit: int | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Measurement).filter(models.Measurement.sensor_id == sensor_id)
    if time_from is not None:
        query = query.filter(models.Measurement.time >= time_from)
    if time_to is not None:
        query = query.filter(models.Measurement.time < time_to)
    
    if limit: 
        measurements = query.order_by(models.Measurement.time).limit(limit).all()
    else: 
        measurements = query.order_by(models.Measurement.time).all()
            
    return measurements


@router.get("/api/v1/measurements/{sensor_id}/summary",
    description="Return first and last measurement."
)
async def get_measurements(
    current_user: Annotated[User, Depends(get_current_user)],
    sensor_id: str,
    db: Session = Depends(get_db)
):
    first = db.query(models.Measurement).filter(models.Measurement.sensor_id == sensor_id).order_by(models.Measurement.time).limit(1).first()
    last = db.query(models.Measurement).filter(models.Measurement.sensor_id == sensor_id).order_by(desc(models.Measurement.time)).limit(1).first()
    
    measurements = [
        first,
        last
    ]
    return measurements


@router.delete("/api/v1/measurement/{sensor_id}")
async def delete_measurement(
    current_user: Annotated[User, Depends(get_current_user)],
    sensor_id: str, db: Session = Depends(get_db)
):
    delete_post = db.query(models.Measurement).filter(models.Measurement.sensor_id == sensor_id)
    if delete_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no matching item was found")
    else:
        delete_post.delete(synchronize_session=False)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/api/v1/measurement/{sensor_id}/{time}")
async def delete_measurement(
    current_user: Annotated[User, Depends(get_current_user)],
    sensor_id: str, time: datetime, db: Session = Depends(get_db)
):
    delete_post = db.query(models.Measurement).filter(models.Measurement.sensor_id == sensor_id).filter(models.Measurement.time == time)
    if delete_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no matching item was found")
    else:
        delete_post.delete(synchronize_session=False)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/api/v1/measurement/{identifier}/{time}")
async def update_measurement(
    current_user: Annotated[User, Depends(get_current_user)],
    sensor_id: str, time: datetime, measurement: Measurement, db: Session=Depends(get_db)
):
    updated_post = db.query(models.Measurement).filter(models.Measurement.sensor_id == sensor_id).filter(models.Measurement.time == time)
    if updated_post.first() == None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no matching item was found")
    else:
        updated_post.update(measurement.model_dump(), synchronize_session=False)
        db.commit()
    return updated_post.first()


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
