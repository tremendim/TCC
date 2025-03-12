from sqlalchemy.orm import Session
from database import SessionLocal
from models import Jogo

def reset_jogos_finalizados():
    db: Session = SessionLocal()

    try:
        # Atualiza todos os jogos, definindo jogo_finalizado como False
        db.query(Jogo).update({"jogo_finalizado": False})
        db.commit()
        print("✅ Todos os jogos foram marcados como não finalizados (False)!")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao resetar jogos finalizados: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    reset_jogos_finalizados()
