from sqlmodel import Session, select, text
from fastapi import FastAPI, Depends, HTTPException, Body
from models import Leilao, Jogo, LeilaoUpdate, getSession

app=FastAPI()

@app.get('/auctions', response_model=list[Leilao])
def getAllAuctions(session:Session=Depends(getSession)):
    auctions = session.exec(select(Leilao)).all()
    return auctions

@app.get('/auctions/{nome}', response_model=list[Leilao])
def getAuctionsByName(nome:str, session:Session=Depends(getSession)):
    auctions=session.exec(select(Leilao).join(Jogo, Leilao.id_jogo==Jogo.id).where(Jogo.nome==nome)).all()
    return auctions

@app.get('/auction/{id_leilao}', response_model=Leilao)
def getAuctionById(id_leilao:int, session:Session=Depends(getSession)):
    auction=session.exec(select(Leilao).where(Leilao.id_leilao==id_leilao)).first()
    if not auction:
        raise HTTPException(status_code=404, detail=f'Auction {id_leilao} not found')
    return auction

@app.get('/games', response_model=list[Jogo])
def getGames(session:Session=Depends(getSession)):
    games=session.exec(select(Jogo)).all()
    return games

@app.put('/update/auction/{id_leilao}', response_model=Leilao)
def updateAuctionById(id_leilao: int, data: LeilaoUpdate=Body(...), session:Session=Depends(getSession)):
    auction=session.exec(select(Leilao).where(Leilao.id_leilao==id_leilao)).first()
    if not auction:
        raise HTTPException(status_code=404, detail=f'Auction {id_leilao} not found')
    auction_data=data.model_dump(exclude_unset=True)
    for key, value in auction_data.items():
        setattr(auction, key, value)
    session.add(auction)
    session.commit()
    session.refresh(auction)
    return auction