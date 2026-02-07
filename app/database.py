from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

import os
import shutil

# --- Db Migration & Path Setup ---
OLD_DB_PATH = "./job_assistant.db"
DATA_DIR = "./.data"
NEW_DB_PATH = os.path.join(DATA_DIR, "job_assistant.db")

# Ensure .data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# move old db if needd
if os.path.exists(OLD_DB_PATH) and not os.path.exists(NEW_DB_PATH):
    try:
        shutil.move(OLD_DB_PATH, NEW_DB_PATH)
        print(f"✅ Migrated database from {OLD_DB_PATH} to {NEW_DB_PATH}")
    except Exception as e:
        print(f"⚠️ Migration failed: {e}. Starting with fresh DB.")


db_path_str = NEW_DB_PATH.replace("\\", "/")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path_str}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Db Tables ---

class UserProfileTable(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True)
    data_json = Column(Text) 

class JobApplicationTable(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    job_title = Column(String)
    company = Column(String)
    status = Column(String, default="Not Submitted")
    match_score = Column(Integer)
    url = Column(String)

class UserPreferencesTable(Base):
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    values = Column(Text)  # json list
    field = Column(String)
    subfield = Column(String)
    specialization = Column(String)
    locations = Column(Text)  # json list
    remote_preference = Column(Integer)  # 0 or 1 for boolean
    role_level = Column(String)

# create teh tables
Base.metadata.create_all(bind=engine)


# --- CRUD Funcs ---

def save_user_profile(profile_data: dict):
    db = SessionLocal()
    try:
        user = db.query(UserProfileTable).first()
        # use get so it doesnt crash
        personal = profile_data.get('personal_info', {})
        name = personal.get('name', 'Unknown')
        email = personal.get('email', 'N/A')

        if not user:
            user = UserProfileTable(
                full_name=name,
                email=email,
                data_json=json.dumps(profile_data)
            )
            db.add(user)
        else:
            user.full_name = name
            user.email = email
            user.data_json = json.dumps(profile_data)
        db.commit()
    finally:
        db.close()

def add_application(job_title: str, company: str, score: int, url: str):
    db = SessionLocal()
    try:
        new_app = JobApplicationTable(
            job_title=job_title,
            company=company,
            match_score=score,
            url=url
        )
        db.add(new_app)
        db.commit()
        db.refresh(new_app)
        return new_app
    finally:
        db.close()

def get_all_applications():
    db = SessionLocal()
    try:
        apps = db.query(JobApplicationTable).all()
        return apps
    finally:
        db.close()

def save_user_preferences(preferences: dict):
    """Save or update user preferences"""
    db = SessionLocal()
    try:
        user_id = preferences.get('user_id')
        existing = db.query(UserPreferencesTable).filter_by(user_id=user_id).first()
        
        if existing:
            # Update existing preferences
            existing.values = json.dumps(preferences.get('values', []))
            existing.field = preferences.get('field', '')
            existing.subfield = preferences.get('subfield', '')
            existing.specialization = preferences.get('specialization', '')
            existing.locations = json.dumps(preferences.get('locations', []))
            existing.remote_preference = 1 if preferences.get('remote_preference') else 0
            existing.role_level = preferences.get('role_level', '')
        else:
            # Create new preferences
            new_prefs = UserPreferencesTable(
                user_id=user_id,
                values=json.dumps(preferences.get('values', [])),
                field=preferences.get('field', ''),
                subfield=preferences.get('subfield', ''),
                specialization=preferences.get('specialization', ''),
                locations=json.dumps(preferences.get('locations', [])),
                remote_preference=1 if preferences.get('remote_preference') else 0,
                role_level=preferences.get('role_level', '')
            )
            db.add(new_prefs)
        
        db.commit()
        return True
    except Exception as e:
        print(f"Error saving preferences: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def get_user_preferences(user_id: str):
    """Get user preferences by user_id"""
    db = SessionLocal()
    try:
        prefs = db.query(UserPreferencesTable).filter_by(user_id=user_id).first()
        if prefs:
            return {
                'user_id': prefs.user_id,
                'values': json.loads(prefs.values),
                'field': prefs.field,
                'subfield': prefs.subfield,
                'specialization': prefs.specialization,
                'locations': json.loads(prefs.locations),
                'remote_preference': bool(prefs.remote_preference),
                'role_level': prefs.role_level
            }
        return None
    finally:
        db.close()
