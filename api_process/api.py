from sqlmodel import Session, select, text
from fastapi import FastAPI, Depends, HTTPException
from models import Leilao, Jogo, getSession

app=FastAPI()

@app.get('/auctions', response_model=list[Leilao])
def getAllAuctions(session:Session=Depends(getSession)):
    auctions = session.exec(select(Leilao)).all()
    return auctions

@app.get('/auctions/{nome}', response_model=list[Leilao])
def getAuctionsByName(nome:str, session:Session=Depends(getSession)):
    auctions=session.exec(select(Leilao).join(Jogo, Leilao.id_jogo==Jogo.id).where(Jogo.nome==nome)).all()

@app.get('/auction/{id_leilao}', response_model=Leilao)
def get_auction_by_id(id_leilao:int, session:Session=Depends(getSession)):
    auction=session.exec(select(Leilao).where(Leilao.id_leilao==id_leilao)).first()
    if not auction:
        raise HTTPException(status_code=404, detail=f'Auction {id_leilao} not found')
    return auction
