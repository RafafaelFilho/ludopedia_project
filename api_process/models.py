from sqlmodel   import SQLModel, Field, create_engine, Session, text, select
from dotenv     import load_dotenv
from datetime   import datetime
from typing     import Optional
import os

# Classes
class Leilao(SQLModel, table=True):
    __tablename__ = "leilao"
    id: Optional[int] = Field(default=None, primary_key=True)
    id_leilao: int = Field(unique=True)
    id_jogo: Optional[int] = Field(default=None, foreign_key="jogo.id")
    link_leilao: str
    valor_pago: int
    data_fim_leilao: datetime = Field(nullable=True)
    status: str = Field(default='em andamento')
    observacoes: str = Field(nullable=True)
    data_alteracao: datetime
    local: str = Field(nullable=True)
    estado_item: bool = Field(nullable=True) # 1-novo | 0-usado
    tipo: bool = Field(nullable=True) # 1-jogo | 2-extras
    data_registro: datetime 

class Jogo(SQLModel, table=True):
    __tablename__ = "jogo"
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    nome_ludopedia: str

class LeilaoUpdate(SQLModel):
    id_leilao: Optional[int] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None
    local: Optional[str] = None
    estado_item: Optional[bool] = None
    tipo: Optional[bool] = None

load_dotenv()
user=os.getenv('MYSQL_USER')
password=os.getenv('MYSQL_PASSWORD')
host=os.getenv('MYSQL_HOST')
port=os.getenv('MYSQL_PORT')
db=os.getenv('MYSQL_DATABASE')
database_url=f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
#database_url = "sqlite:///C:/Users/rfari/Documents/repos/projetos/analise_jogos_tabuleiro/leiloes_jogos.db"
engine=create_engine(database_url)

def getSession():
    with Session(engine) as session:
        yield session