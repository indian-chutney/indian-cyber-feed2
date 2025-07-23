from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.models import models, schemas

class SourceService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_sources(self) -> List[models.Source]:
        return self.db.query(models.Source).order_by(models.Source.name).all()

    def get_source_by_id(self, source_id: UUID) -> Optional[models.Source]:
        return self.db.query(models.Source).filter(models.Source.id == source_id).first()

    def create_source(self, source: schemas.SourceCreate) -> models.Source:
        db_source = models.Source(**source.dict())
        self.db.add(db_source)
        self.db.commit()
        self.db.refresh(db_source)
        return db_source

    def update_source(self, source_id: UUID, source_update: schemas.SourceCreate) -> Optional[models.Source]:
        db_source = self.get_source_by_id(source_id)
        if not db_source:
            return None

        for field, value in source_update.dict(exclude_unset=True).items():
            setattr(db_source, field, value)

        self.db.commit()
        self.db.refresh(db_source)
        return db_source

    def delete_source(self, source_id: UUID) -> bool:
        db_source = self.get_source_by_id(source_id)
        if not db_source:
            return False

        self.db.delete(db_source)
        self.db.commit()
        return True

    def get_active_sources(self) -> List[models.Source]:
        return self.db.query(models.Source).filter(models.Source.is_active == True).all()

    def get_sources_by_type(self, source_type: models.SourceType) -> List[models.Source]:
        return self.db.query(models.Source).filter(models.Source.source_type == source_type).all()