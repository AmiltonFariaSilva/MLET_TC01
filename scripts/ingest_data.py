import pandas as pd 
import sys 
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))
from database import session_local, engine, Base
from models import Books 


def ingest_data():
    print("Criando a tabela 'books' (se não existir) ... ")
    Base.metadata.create_all(bind = engine)
    print("Tabela pronta !")
    books_csv_path = project_root / "data" / "books.csv"
    try:
        df_books = pd.read_csv(books_csv_path)
        print(f"Dados lidos do csv: {books_csv_path}!")
    except Exception as e:
        print(f"Erro: Arquivo {books_csv_path} não encontrado")
        return 
    db = session_local()
    
    try: 
        # Limpa bd antes da próxima inserção 
        print(f"Limpando dados antigos da tabela ... ")
        db.query(Books).delete()
        print("Iniciando a inserção de dados no banco ... ")
        for _, row in df_books.iterrows():
            book_data = Books (
                title = row.get('title'), 
                price = str(row.get('price')), 
                rating = row.get('rating'), 
                availability = row.get('availability'), 
                category = row.get('category'), 
                image_url = row.get('image_url')
            )
            db.add(book_data)
        db.commit()
        print("Dados inseridos com sucesso !")
    except Exception as e: 
        print(f"Erro ocorrido: {e}")
        db.rollback()
    finally:
        db.close()    
        
if __name__ == "__main__":
    ingest_data()