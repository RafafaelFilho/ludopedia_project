from sqlmodel   import SQLModel, Field, create_engine, Session, text, select
from dotenv     import load_dotenv
from datetime   import datetime
from typing     import Optional
import os
import logging
import sys

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

def connectEngine(main_function):
    try:
        load_dotenv()
        user=os.getenv('MYSQL_USER')
        password=os.getenv('MYSQL_PASSWORD')
        host=os.getenv('MYSQL_HOST')
        port=os.getenv('MYSQL_PORT')
        db=os.getenv('MYSQL_DATABASE')
        database_url=f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
        #database_url = "sqlite:///leiloes_jogos.db"
        engine=create_engine(database_url)
        with Session(engine) as session:
            session.exec(text('SELECT 1'))
        logging.debug('Database connected')
        return engine
    except:
        logging.error(
            'Database connection error', 
            exc_info=True, 
            extra={
                'MainFunction':main_function,
                'Function':'connectEngine'
            }
        ) 
        sys.exit()

def downloadGames(engine):
    try:
        with Session(engine) as session:
            games=session.exec(select(Jogo)).all()
        logging.debug('searchAuctions: Games were downloaded')
        return games
    except:
        logging.critical(
            'Download error', 
            exc_info=True, 
            extra={
                'MainFunction':'searchAuctions',
                'Function':'downloadGames'
            }
        ) 

def addAuction(engine, auctions: list):
    try:
        with Session(engine) as session:
            for auction in auctions:
                l=Leilao(**auction)
                session.add(l)
            session.commit()
        logging.debug('searchAuction: Auctions have been added')
    except:
        logging.critical('Error to add new auctions',
            exc_info=True, 
            extra={
                'MainFunction':'searchAuctions',
                'Function': 'addAuction'
            }
        )
        sys.exit()

def downloadAuctions(engine):
    try:
        with Session(engine) as session:
            auctions=session.exec(select(Leilao).where(Leilao.status=='em andamento')).all()
        logging.debug('updatehAuctions: Auctions downloaded')
        return auctions
    except:
        logging.critical(
            'Error to download', 
            exc_info=True, 
            extra={
                'MainFunction':'updateAuctions',
                'Function':'downloadAuctions'
            }
        ) 
def downloadAuction(engine, auc_id):
    with Session(engine) as session:
        query=session.exec(select(Leilao).where(Leilao.id_leilao==auc_id)).first()
        if query:
            logging.debug('searchAuction: Auction already exists in the database (returng False)')
            return False
        else:
            logging.debug("searchAuction: Auction doesn't exist in the database (returning True)")
            return True
    
def saveUpdates(engine, auction, info):
    with Session(engine) as session:
        for key, value in info.items():
            setattr(auction,key,value)
        session.add(auction)
        session.commit()