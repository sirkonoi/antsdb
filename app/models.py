from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, timezone

class Species(Base):
    __tablename__ = "species"

    id = Column(Integer, primary_key=True, index=True)
    scientific_name = Column(String, unique=True, index=True, nullable=False)
    genus = Column(String, index=True)
    species = Column(String, index=True)
    subspecies = Column(String, nullable=True)
    subfamily = Column(String, nullable=True)
    family = Column(String, default="Formicidae")
    order = Column(String, default="Hymenoptera")

    status = Column(String, default="draft")  # draft, pending, approved
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    revisions = relationship("SpeciesRevision", back_populates="species", cascade="all, delete-orphan")
    contributors = relationship("Contributors", back_populates="species", cascade="all, delete-orphan")

class SpeciesRevision(Base):
    __tablename__ = "species_revisions"

    id = Column(Integer, primary_key=True, index=True)
    species_id = Column(Integer, ForeignKey("species.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    approved = Column(Boolean, default=False)  # deve essere approvata da un moderatore!!

    content = Column(JSON, nullable=False)

    species = relationship("Species", back_populates="revisions")
    author = relationship("Users", back_populates="revisions")

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
    joined = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    revisions = relationship("SpeciesRevision", back_populates="author", cascade="all, delete-orphan")
    contributions = relationship("Contributors", back_populates="user", cascade="all, delete-orphan")
              

class Contributors(Base):
    __tablename__ = "contributors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(Users.id), nullable=False)
    specie_id = Column(Integer, ForeignKey(Species.id), nullable=False)

    user = relationship("Users", back_populates="contributions")
    species = relationship("Species", back_populates="contributors")
