from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from datetime import datetime

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
    data_registro: datetime = Field(default_factory=datetime.now)

class Jogo(SQLModel, table=True):
    __tablename__ = "jogo"

    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    nome_ludopedia: str
    link_imagem: str

if __name__=='__main__':
    engine = create_engine("sqlite:///leiloes_jogos.db")
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    lista_de_jogos=['Carson City Big Box', 'Wonderlans War', 'Root', 'Arcs', 'Barrage', 'Hues and Cues', 'Northern Pacific', 
        'Marvel Zombies X-Men Resistance', 'Kingsburg 2 dition', 'Os Incriveis Parques de Miss Liz', 'Tammany Hall', 
        'Ponzi Scheme', 'Pax Pamir 2 edition', 'Nefertiti', 'Santiago', 'That Time You Killed Me', 'Irish Gauge', 'Automobile', 
        'Mosaic a Story of Civilization', 'Brian Boru', 'Hansa Teutonica Big Box', 'Hegemony Lead Your Class to Victory', 'Biohack', 
        'Last Light', 'Puerto Rico', 'Northgard', 'Coimbra', 'The King is Dead 2 edition', 'Lancaster', 'Flamecraft', 'Tulip Bubble', 
        'Arquitetos do Reino Ocidental', 'Nations', 'The Red Cathedral', 'The White Castle'
    ]
    lista_de_nomes_ludopedia=['carson-city-big-box', 'wonderland-s-war', 'root', 'arcs', 'barrage', 'hues-and-cues', 'northern-pacific', 
        'marvel-zombies-x-men-resistance', 'kingsburg-second-edition', 'os-incriveis-parques-de-miss-liz', 'tammany-hall', 
        'ponzi-scheme', 'pax-pamir-second-edition', 'nefertiti', 'santiago', 'that-time-you-killed-me', 'irish-gauge', 
        'automobile', 'mosaic-a-story-of-civilization', 'brian-boru-high-king-of-ireland', 'hansa-teutonica-big-box', 
        'hegemony-lead-your-class-to-victory', 'biohack', 'last-light', 'puerto-rico', 'northgard-uncharted-lands', 
        'coimbra', 'the-king-is-dead-second-edition', 'lancaster', 'flamecraft', 'tulip-bubble', 
        'architects-of-the-west-kingdom', 'nations', 'the-red-cathedral', 'the-white-castle'
    ]
    if len(lista_de_jogos)==len(lista_de_nomes_ludopedia):
        registros=list(zip(lista_de_jogos, lista_de_nomes_ludopedia))
        with Session(engine) as session:
            for registro in registros:
                j=Jogo(
                    nome=registro[0],
                    nome_ludopedia=registro[1]
                )
                session.add(j)
            session.commit()
        print('tabelas criadas com sucesso')
    else:
        print('listas com quantidades diferentes')