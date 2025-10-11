from fastapi import FastAPI, Depends, HTTPException
from . import models   
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
