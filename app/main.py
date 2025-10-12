from fastapi import FastAPI, Depends, HTTPException
from . import models, schemas
from sqlalchemy.orm import Session
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to AntsDB API!"}

@app.get("/species")
def get_all_species(db: Session = Depends(get_db)):
    species = (db.query(models.Species).all())

    if not species:
        raise HTTPException(status_code=404, detail="No species found.")
    
    result = []
    for s in species:
        result.append({
        "id": s.id,
        "scientific_name": s.scientific_name
        })

    return result    

@app.get("/species/{species_id}")
def get_species(species_id: int, db: Session = Depends(get_db)):
    species = (db.query(models.Species).filter(models.Species.id == species_id).first())
    if not species:
        raise HTTPException(status_code=404, detail="Species not found.")
    
    revision = (db.query(models.SpeciesRevision).filter(models.SpeciesRevision.id == species_id).filter(models.SpeciesRevision.approved == True).order_by(models.SpeciesRevision.created_at.desc()).first())
    
    content = revision.content if revision else {}
    return {
        "scientific_name": species.scientific_name,
        "current_content": content
    }

@app.post("/species")
def create_species(specie: schemas.SpeciesCreate, db: Session = Depends(get_db)):

    new_specie = models.Species(
        scientific_name=specie.scientific_name,
        genus=specie.genus,
        species=specie.species,
        subspecies=specie.subspecies,
        family=specie.family,
        subfamily=specie.subfamily,
        status=specie.status
    )
    db.add(new_specie)
    db.commit()
    db.refresh(new_specie)

    return {"id": new_specie.id, "scientific_name": new_specie.scientific_name}


@app.post("/species/{species_id}/revision")
def create_revision(species_id: int, revision: schemas.SpeciesRevisionCreate, db: Session = Depends(get_db)):
    try:
        new_rev = models.SpeciesRevision(
            species_id=species_id,
            author_id=revision.author_id,
            content=revision.content,
            approved=False
        )
        db.add(new_rev)
        db.commit()
        db.refresh(new_rev)
        return {"id": new_rev.id, "author": new_rev.author_id, "content": new_rev.content, "approved": new_rev.approved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
