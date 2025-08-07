from sqlmodel   import Session, select
from datetime   import datetime, timedelta
from bs4        import BeautifulSoup
from ludopedia  import Leilao, Jogo, conectEngine
from logger     import logger_setup
import requests
import schedule
import time
import logging

# Functions: Update Auctions group
def update_auction(headers, sql):
    logger_setup()
    now=datetime.now()-timedelta(hours=3)
    engine=conectEngine(sql)
    if engine:
        with Session(engine) as session:
            auctions=download_auctions(session)
            for auction in auctions:
                logging.debug(f'Game search: {auction.link_leilao}')
                response = requests.get(auction.link_leilao, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                canceled_tag=soup.find('div', class_='alert alert-danger')
                if canceled_tag:
                    if 'Leilão não encontrado ou excluído\n×\n' in canceled_tag.text:
                        canceled_auction_process(auction,now)
                    if 'Para dar lances é necessário estar logado no site.' in canceled_tag.text:
                        if not auction.local:
                            complement_info(auction, soup, now)
                        finish_auction(auction, soup, now)
                    else:
                        logging.critical(
                            'Somenthing happened that I dont know', 
                            extra={
                                'id':auction.id,
                                'game_id': auction.id_jogo,
                                'auction_id': auction.id_leilao,
                                'link': auction.link_leilao,
                                'soup': soup.find('body')})
                else:
                        logging.critical(
                            'Somenthing happened that I dont know',
                            extra={
                                'id':auction.id,
                                'game_id': auction.id_jogo,
                                'auction_id': auction.id_leilao,
                                'link': auction.link_leilao,
                                'soup': soup.find('body')})
            session.commit()
        logging.info('Update Auction: Finished')

def download_auctions(session):
    auctions=session.exec(select(Leilao).where(Leilao.status=='em andamento')).all ()
    logging.debug('Auctions downloaded')
    return auctions

def canceled_auction_process(auction, now):
    auction.status='cancelado'
    auction.data_alteracao=now
    logging.debug('Complement info updated')

def complement_info(auction, soup, now):
    try:
        title=soup.find('h3',attrs=('class','title')).text.strip()
        desc=soup.find(id='bloco-descricao-item').text.strip()
        obs=f'{title}/|/|{desc}'
        local=soup.find_all('div',attrs=('class','media-body'))[3].text.split('(')[1].split(')')[0]
        estado_item = soup.find_all('div',attrs=('class','col-xs-12 col-md-6'))[3].text.split(':')[1].strip()
        auction.observacoes=obs
        auction.local=local
        auction.estado_item= 0 if estado_item=='Usado' else 1
        auction.data_alteracao=now
        logging.debug('Complement info updated')
    except:
        logging.error(
            'This page is differente', 
            exc_info=True, 
            extra={
                'id':auction.id,
                'game_id': auction.id_jogo,
                'auction_id': auction.id_leilao,
                'link': auction.link_leilao,
                'soup': soup.find('body')})


def finish_auction(auction, soup, now):
    try:
        spans=soup.find('div', class_='leilao-dados-lance form-group').find_all('span')
        value=spans[2].find('span') or spans[2].find('b')
        data_span=spans[0].find('span')
        if 'Finalizado' in data_span.text:
            end_date=datetime.strptime(data_span.text[12:-7] + '/2025', '%d/%m/%Y')
            try:
                value=int(value.text.replace("R$", "").replace(".", "").replace(",","").strip())
            except:
                value=0
            auction.valor_pago=value
            auction.data_fim_leilao=end_date
            auction.status='finalizado'
            auction.data_alteracao=now
    except:
        logging.error(
            'This page is differente', 
            exc_info=True, 
            extra={
                'id':auction.id,
                'game_id': auction.id_jogo,
                'auction_id': auction.id_leilao,
                'link': auction.link_leilao,
                'soup': soup.find('body')})
        
# Functions: Search Auctions group
def search_auction(headers, sql):
    engine=conectEngine(sql)
    if engine:
        with Session(engine) as session:
            games=download_games(session)
            for game in games:
                logging.debug(game.nome)
                trs=find_trs(game, headers)
                if trs:
                    for tr in trs:
                        auction_conf, auction_id, link=auction_conference(session, tr, game)
                        if not auction_conf:
                            logging.debug('Auction found')
                            add_auction(session, game, auction_id, link)
            session.commit()
        logging.info('Search Auction: Finished')

def download_games(session):
    games=session.exec(select(Jogo)).all()
    logging.debug('Games downloaded')
    return games
def find_trs(game, headers):
    url = f'https://ludopedia.com.br/jogo/{game.nome_ludopedia}?v=anuncios'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    trs = soup.find_all('tr')
    if trs:
        return trs
    else:
        logging.error(
            'Search Acution: This page is differente', 
            exc_info=True, 
            extra={
                'function': 'find_trs',
                'id':game.id,
                'game_name': game.nome,
                'soup': soup.find('body')})
        return None
def auction_conference(session, tr, game):
    a=tr.find('a')
    if a:
        if a.text=='Leilão':
            link=a.get('href')
            auction_id=link.split('/')[4]
            auction_conf=session.exec(select(Leilao).where(Leilao.id_leilao==auction_id)).first()
            return auction_conf, auction_id, link
    else:
        logging.error(
            'Search Acution: This page is differente', 
            exc_info=True, 
            extra={
                'function': 'find_trs',
                'id':game.id,
                'game_name': game.nome,
                'tr': tr})
    return True, None, None
def add_auction(session, game, auction_id, link):
    l=Leilao(
        id_leilao=auction_id,
        id_jogo=game.id,
        link_leilao=link,
        valor_pago=0,
        data_alteracao=datetime.now()-timedelta(hours=3)
    )
    session.add(l)
    
# Functions: Schedule Job
def job_17h():
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"}
    search_auction(headers,'mysql')
    
def job_07h():
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115 Safari/537.36"}
    update_auction(headers,'mysql')
    now=datetime.now()-timedelta(hours=3)

if __name__=='__main__':
    schedule.every().day.at('20:00').do(job_17h)
    schedule.every().day.at('10:00').do(job_07h)
    while True:
        schedule.run_pending()
        time.sleep(1)
