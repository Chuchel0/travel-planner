from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from . import models, schemas
from .services import ArtInstituteService


class CRUDProject:
    def get(self, db: Session, id: int) -> Optional[models.Project]:
        return db.query(models.Project).filter(models.Project.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[models.Project]:
        return db.query(models.Project).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: schemas.ProjectCreate) -> models.Project:
        db_obj = models.Project(
            name=obj_in.name,
            description=obj_in.description,
            start_date=obj_in.start_date
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: models.Project, obj_in: schemas.ProjectUpdate
    ) -> models.Project:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> models.Project:
        obj = db.query(models.Project).get(id)
        if obj:
            # Check if any places in this project are visited
            visited_places = db.query(models.Place).filter(
                and_(
                    models.Place.project_id == id,
                    models.Place.visited == True
                )
            ).count()

            if visited_places > 0:
                raise ValueError("Cannot delete project with visited places")

            db.delete(obj)
            db.commit()
        return obj

    def create_with_places(
        self, db: Session, *, obj_in: schemas.ProjectCreate, places_in: List[schemas.PlaceCreate]
    ) -> models.Project:
        # Validate places exist in external API
        art_service = ArtInstituteService()
        for place_in in places_in:
            if not art_service.validate_place_exists(place_in.external_api_id):
                raise ValueError(f"Place with external_api_id {place_in.external_api_id} not found in Art Institute API")

        # Check project places limit
        if len(places_in) > 10:
            raise ValueError("Cannot have more than 10 places in a project")

        # Create project
        db_obj = models.Project(
            name=obj_in.name,
            description=obj_in.description,
            start_date=obj_in.start_date
        )
        db.add(db_obj)
        db.flush()  # Get the ID without committing

        # Create places
        for place_in in places_in:
            place_obj = models.Place(
                external_api_id=place_in.external_api_id,
                name=place_in.name,
                description=place_in.description,
                project_id=db_obj.id
            )
            db.add(place_obj)

        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDPlace:
    def get(self, db: Session, id: int) -> Optional[models.Place]:
        return db.query(models.Place).filter(models.Place.id == id).first()

    def get_by_external_api_id_and_project(
        self, db: Session, *, external_api_id: str, project_id: int
    ) -> Optional[models.Place]:
        return db.query(models.Place).filter(
            and_(
                models.Place.external_api_id == external_api_id,
                models.Place.project_id == project_id
            )
        ).first()

    def get_multi_by_project(
        self, db: Session, *, project_id: int, skip: int = 0, limit: int = 100
    ) -> List[models.Place]:
        return (
            db.query(models.Place)
            .filter(models.Place.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(
        self, db: Session, *, obj_in: schemas.PlaceCreate, project_id: int
    ) -> models.Place:
        # Check if place already exists in this project
        existing = self.get_by_external_api_id_and_project(
            db, external_api_id=obj_in.external_api_id, project_id=project_id
        )
        if existing:
            raise ValueError("Place already exists in this project")

        # Validate place exists in external API
        art_service = ArtInstituteService()
        if not art_service.validate_place_exists(obj_in.external_api_id):
            raise ValueError(f"Place with external_api_id {obj_in.external_api_id} not found in Art Institute API")

        # Check project places limit
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")

        current_places_count = db.query(models.Place).filter(
            models.Place.project_id == project_id
        ).count()

        if current_places_count >= 10:
            raise ValueError("Cannot have more than 10 places in a project")

        db_obj = models.Place(
            external_api_id=obj_in.external_api_id,
            name=obj_in.name,
            description=obj_in.description,
            project_id=project_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: models.Place, obj_in: schemas.PlaceUpdate
    ) -> models.Place:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> models.Place:
        obj = db.query(models.Place).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


project = CRUDProject()
place = CRUDPlace()