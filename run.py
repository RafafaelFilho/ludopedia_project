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
    logging.info(
        'searchAuction: Process finished',
        extra={
            'Initial Auctions':'developing',
            'Updated Auctions':'developing',
            'Update Details':{
                'Canceled Auctions':'developing',
                'Complemented Auctions':'developing',
                'Finished Auctions':'developing'
            }
        }
    )

def updateAuctions(headers):
    logger_setup()
    engine=connectEngine('updateAuctions')
    auctions=downloadAuctions(engine)
    for auction in auctions:
        info=updateSelectionProcess(auction, headers)
        if info:
            saveUpdates(engine, auction, info)
    logging.info(
        'updateAuction: Process finished',
        extra={
            'Initial Auctions':'developing',
            'Updated Auctions':'developing',
            'Update Details':{
                'Canceled Auctions':'developing',
                'Complemented Auctions':'developing',
                'Finished Auctions':'developing'
            }
        }
    )

if __name__=='__main__':
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"}
#    schedule.every().day.at('10:00').do(lambda: updateAuctions(headers))
#    schedule.every().day.at('20:00').do(lambda: searchAuctions(headers))
#    while True:
#        schedule.run_pending()
#        time.sleep(1)
    searchAuctions(headers)
