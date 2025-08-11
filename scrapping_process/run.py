from scrapper   import findTrs, auctionConference, updateSelectionProcess
from models     import connectEngine, downloadGames, addAuction, downloadAuctions, saveUpdates
from logger     import logger_setup
import schedule
import logging
import time

def searchAuctions(headers):
    logger_setup()
    auctions=[]
    engine=connectEngine('searchAuctions')
    games=downloadGames(engine)
    for game in games:
        trs=findTrs(game, headers)
        if trs:
            for tr in trs:
                new_auction=auctionConference(engine, tr, game)
                if new_auction:
                    auctions.append(new_auction)
    if auctions:
        addAuction(engine, auctions)
    logging.info(f'searchAuction: Process finished | {len(auctions)} auctions were added')

def updateAuctions(headers):
    logger_setup()
    updated_auctions=0
    engine=connectEngine('updateAuctions')
    auctions=downloadAuctions(engine)
    for auction in auctions:
        info=updateSelectionProcess(auction, headers)
        if info:
            updated_auctions+=1
            saveUpdates(engine, auction, info)
    logging.info(f'updateAuction: Process finished | {updated_auctions} auctions were updated')

if __name__=='__main__':
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"}
    schedule.every().day.at('10:00').do(lambda: updateAuctions(headers))
    schedule.every().day.at('20:00').do(lambda: searchAuctions(headers))
    while True:
        schedule.run_pending()
        time.sleep(1)
