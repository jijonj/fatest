from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos.db'
SQLALCHEMY_DATABASE_URL = 'postgresql://jijonj:WpYehtIwrwLkwPNwH2yRWIKIaDfj5x3I@dpg-cle6an7pc7cc73ell00g-a.oregon-postgres.render.com/todo_h1yc'

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
