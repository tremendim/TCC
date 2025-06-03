# backend/app/alterar_divisao_times.py

import sqlite3

# Caminho para o seu banco de dados
db_path = "campeonato.db"

# IDs dos times que serão alterados
ids_para_alterar = (1, 2)
nova_divisao = "B"

# Conectar ao banco de dados SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # O comando UPDATE irá alterar a coluna 'divisao'
    # para os times cujos IDs estão na lista (1, 2)
    comando_sql = "UPDATE times SET divisao = ? WHERE id IN (?, ?)"

    # Executa o comando com os parâmetros
    cursor.execute(comando_sql, (nova_divisao,) + ids_para_alterar)

    # Verifica quantos times foram afetados pela alteração
    times_afetados = cursor.rowcount
    print(f"✅ {times_afetados} time(s) foram atualizados para a Divisão '{nova_divisao}'.")

    # Salva (commit) a transação
    conn.commit()
    print("✅ Alterações salvas no banco de dados!")

except sqlite3.Error as e:
    # Em caso de erro, reverte a transação
    conn.rollback()
    print(f"❌ Ocorreu um erro de banco de dados: {e}")
    print("Nenhuma alteração foi salva.")

finally:
    # Fecha a conexão com o banco de dados
    conn.close()