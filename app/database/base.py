# app/database/base.py
from sqlalchemy.ext.declarative import declarative_base

# ЕДИНСТВЕННЫЙ Base объект, используется во всех моделях
Base = declarative_base()
