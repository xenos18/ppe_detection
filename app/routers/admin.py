from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker
from database import _init
from crud import get_location

router = APIRouter(prefix='/api')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_init())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/locations", tags=["location"])
async def read_locations(db: Session = Depends(get_db)):
    resource = [i.serialize() for i in get_location(db)]
    json_compatible_item_data = jsonable_encoder(resource)
    return JSONResponse(content=json_compatible_item_data)


@router.get("/all_events", tags=["location"])
async def read_events(db: Session = Depends(get_db)):
    resource = [i.serialize() for i in get_location(db)]
    json_compatible_item_data = jsonable_encoder(resource)
    return JSONResponse(content=json_compatible_item_data)

#
#
# @router.get("/users/{username}", tags=["users"])
# async def read_user(username: str):
#     return {"username": username}
