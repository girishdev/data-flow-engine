
from app.database.connection import Base, engine
from app.models.database_models import User, DataAutomation


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized successfully")


if __name__ == "__main__":
    initialize_database()
