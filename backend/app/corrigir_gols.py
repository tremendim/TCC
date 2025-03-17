import sqlite3

# Caminho do banco de dados
db_path = "campeonato.db"  # Substitua pelo caminho correto

# Conectar ao banco de dados SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Resetar os gols dos times
    cursor.execute("UPDATE times SET gols_feitos = 0, gols_sofridos = 0")

    # Excluir o time com id = 4
    cursor.execute("DELETE FROM times WHERE id = 4")

    # Atualizar as siglas dos times 1 e 2
    cursor.execute("UPDATE times SET sigla = 'TJP' WHERE id = 1")
    cursor.execute("UPDATE times SET sigla = 'CHB' WHERE id = 2")

    # Confirmar as alterações
    conn.commit()
    print("✅ Modificações realizadas com sucesso!")

except Exception as e:
    conn.rollback()
    print(f"❌ Erro ao modificar o banco de dados: {e}")

finally:
    conn.close()
