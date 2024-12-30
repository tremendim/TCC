from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL do banco de dados (ajuste conforme necessário)
DATABASE_URL = "sqlite:///./campeonato.db"

# Configuração do engine do SQLite
# Para outros bancos (PostgreSQL, MySQL), troque a URL e configure adequadamente
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Sessão do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos do SQLAlchemy
Base = declarative_base()

# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
