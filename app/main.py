from fastapi import *
from . import models, schemas
from sqlalchemy.orm import Session
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# GET requests

@app.get("/")
def root():
    return {"message": "Welcome to AntsDB API!"}

# GET species list
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

# GET specie information
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

@app.get("/species/{species_id}/revisions")
def get_specie_revision(species_id: int, db: Session = Depends(get_db)):
    revisions = (db.query(models.SpeciesRevision).filter(models.SpeciesRevision.species_id == species_id).all())
    if not revisions:
        raise HTTPException(status_code=404, detail="No revisions found.")    

    result = []
    for r in revisions:
        result.append({
            "author_id": r.author_id,
            "created_at": r.created_at,
            "approved": r.approved,
            "content": r.content
        })   
    return result    
       
# POST requests
# POST specie --> create new specie
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

# POST specie revision --> create new revision
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

# DELETE requests
# DELETE specie
@app.delete("species/delete/{species_id}")
def delete_specie(species_id: int, db: Session = Depends(get_db)):
    specie = db.query(models.Species).filter(species_id == models.Species.id).first()

    if not specie:
        raise HTTPException(status_code=404, detail="Species not found")
    
    db.delete(specie)
    db.commit()

    return {"message": f"Species {species_id} deleted successfully"}

# DELETE revision
@app.delete("species/{species_id}/revision/del")
def delete_specie(revision_id: int, db: Session = Depends(get_db)):
    revision = db.query(models.SpeciesRevision).filter(revision_id == models.SpeciesRevision.id).first()

    if not revision:
        raise HTTPException(status_code=404, detail="Species not found")
    
    db.delete(revision)
    db.commit()

    return {"message": f"Species Revision {revision} deleted successfully"}

#PUT requests
#PUT specie --> update specie
@app.put("species/{species_id}/update")
def update_species(species_id: int, species: schemas.SpeciesCreate, db: Session = Depends(get_db)):
    specie = db.query(models.Species).filter(models.Species.id == species_id).first()

    if not specie:
        raise HTTPException(status_code=404, detail="Species not found")

    specie.update(species.model_dump())
    db.commit()

    return {"message": "Species updated successfully", "id": species_id}

#PUT revision --> update revision
@app.put("species/{species_id}/{revision_id}update")
def update_species(species_id: int, revision_id: int, species: schemas.SpeciesCreate, db: Session = Depends(get_db)):
    revision = db.query(models.Species).filter(models.SpeciesRevision.species_id == species_id).filter(models.SpeciesRevision.id == revision_id).first()

    if not revision:
        raise HTTPException(status_code=404, detail="Species/Revision not found")

    revision.update(species.model_dump())
    db.commit()

    return {"message": "Revision updated successfully", "id": species_id}