
from app.evaluation.database import engine, Base
from app.evaluation.models import EvaluationHistory

# Create all tables defined in models
Base.metadata.create_all(bind=engine)

print("Database and tables created successfully!")

print("Tables:", Base.metadata.tables.keys())
