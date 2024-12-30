from sqlalchemy.orm import Session
from database import SessionLocal
from models import Time, Jogo

def corrigir_gols_null():
    db: Session = SessionLocal()
    try:
        times_com_null = db.query(Jogo).filter(
            (Jogo.placar_casa == None) | (Jogo.placar_visitante == None)
        ).all()

        for jogador in times_com_null:
            if jogador.placar_casa is None:
                jogador.placar_casa = 0
            if jogador.placar_visitante is None:
                jogador.placar_visitante = 0


        db.commit()
        print("Atualização concluída.")
    except Exception as e:
        db.rollback()
        print(f"Erro ao atualizar os valores: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    corrigir_gols_null()
