from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal

router = APIRouter()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Project endpoints
@router.get("/projects/", response_model=list[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = crud.project.get_multi(db, skip=skip, limit=limit)
    return projects

@router.post("/projects/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    return crud.project.create(db=db, obj_in=project)

@router.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.project.get(db=db, id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)
):
    db_project = crud.project.get(db=db, id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.project.update(db=db, db_obj=db_project, obj_in=project)

@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = crud.project.get(db=db, id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        crud.project.remove(db=db, id=project_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"ok": True}


# Place endpoints
@router.post("/projects/{project_id}/places/", response_model=schemas.Place, status_code=status.HTTP_201_CREATED)
def create_place_for_project(
    project_id: int, place: schemas.PlaceCreate, db: Session = Depends(get_db)
):
    # Verify project exists
    db_project = crud.project.get(db=db, id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        return crud.place.create(db=db, obj_in=place, project_id=project_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects/{project_id}/places/", response_model=list[schemas.Place])
def read_places_for_project(
    project_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    # Verify project exists
    db_project = crud.project.get(db=db, id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    places = crud.place.get_multi_by_project(db=db, project_id=project_id, skip=skip, limit=limit)
    return places

@router.get("/projects/{project_id}/places/{place_id}", response_model=schemas.Place)
def read_place(
    project_id: int, place_id: int, db: Session = Depends(get_db)
):
    # Verify project exists
    db_project = crud.project.get(db=db, id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_place = crud.place.get(db=db, id=place_id)
    if db_place is None or db_place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found in this project")
    return db_place

@router.put("/projects/{project_id}/places/{place_id}", response_model=schemas.Place)
def update_place(
    project_id: int, place_id: int, place: schemas.PlaceUpdate, db: Session = Depends(get_db)
):
    # Verify project exists
    db_project = crud.project.get(db=db, id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_place = crud.place.get(db=db, id=place_id)
    if db_place is None or db_place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found in this project")

    return crud.place.update(db=db, db_obj=db_place, obj_in=place)

@router.delete("/projects/{project_id}/places/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_place(
    project_id: int, place_id: int, db: Session = Depends(get_db)
):
    # Verify project exists
    db_project = crud.project.get(db=db, id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_place = crud.place.get(db=db, id=place_id)
    if db_place is None or db_place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found in this project")

    crud.place.remove(db=db, id=place_id)
    return {"ok": True}


# Special endpoints for updating place notes and visited status
@router.patch("/projects/{project_id}/places/{place_id}/notes", response_model=schemas.Place)
def update_place_notes(
    project_id: int, place_id: int, notes: str, db: Session = Depends(get_db)
):
    # Verify project exists
    db_project = crud.project.get(db=db, id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_place = crud.place.get(db=db, id=place_id)
    if db_place is None or db_place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found in this project")

    db_place.notes = notes
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

@router.patch("/projects/{project_id}/places/{place_id}/visit", response_model=schemas.Place)
def mark_place_as_visited(
    project_id: int, place_id: int, db: Session = Depends(get_db)
):
    # Verify project exists
    db_project = crud.project.get(db=db, id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db_place = crud.place.get(db=db, id=place_id)
    if db_place is None or db_place.project_id != project_id:
        raise HTTPException(status_code=404, detail="Place not found in this project")

    db_place.visited = True
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place