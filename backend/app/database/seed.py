import logging
from app.database.session import Base, engine, SessionLocal
from app.models.db_models import User

logger = logging.getLogger(__name__)

DEMO_USER_ID = "demo-user-id"

def init_db():
    if engine is None:
        logger.warning("[Seed] Engine not initialized.")
        return
    try:
        # Create all tables automatically
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        try:
            demo_user = db.query(User).filter(User.id == DEMO_USER_ID).first()
            if not demo_user:
                demo_user = User(
                    id=DEMO_USER_ID,
                    name="Demo User",
                    email="demo@beforeyouthrowitaway.org"
                )
                db.add(demo_user)
                db.commit()
                logger.info("[Seed] Default demo user created successfully.")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"[Seed] Error initializing database tables: {str(e)}")

if __name__ == "__main__":
    init_db()
