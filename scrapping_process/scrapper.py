from datetime   import datetime, timedelta
from models     import downloadAuction
from bs4        import BeautifulSoup
import logging
import requests
import sys

def findTrs(game, headers):
    try:
        url = f'https://ludopedia.com.br/jogo/{game.nome_ludopedia}?v=anuncios'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        trs = soup.find_all('tr')
        if trs:
            logging.debug('searchAuctions: TRs were found')
            return trs
        else:
            logging.error(
                'This page is differente', 
                exc_info=True, 
                extra={
                    'MainFunction':'searchAuctions',
                    'Function': 'findTrs',
                    'id':game.id,
                    'game_name': game.nome,
                    'soup': soup.find('body')
                }
            )
            return None
    except:
        logging.critical(
            'Connection error on Ludopedia',
            exc_info=True, 
            extra={
                'MainFunction':'searchAuctions',
                'Function': 'findTrs',
                'id':game.id,
                'game_name': game.nome
            }
        )

def auctionConference(engine, tr, game):
    a=tr.find('a')
    if a:
        if a.text=='Leilão':
            link=a.get('href')
            auc_id=link.split('/')[4]
            validation=downloadAuction(engine, auc_id)
            if validation:
                now=datetime.now()-timedelta(hours=3) 
                new_auc={
                    'id_leilao':auc_id,
                    'id_jogo':game.id,
                    'link_leilao':link,
                    'valor_pago':0,
                    'status':'em andamento',
                    'data_alteracao':now,
                    'data_registro':now
                }
                logging.debug('searchAuction: New auction were found')
                return new_auc
    return None

def updateSelectionProcess(auction, headers):
    response = requests.get(auction.link_leilao, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    canceled_tag=soup.find('div', class_='alert alert-danger')
    if canceled_tag:
        if 'Para dar lances é necessário estar logado no site.' in canceled_tag.text or 'Leilão não encontrado ou excluído\n×\n' in canceled_tag.text:
            if 'Leilão não encontrado ou excluído\n×\n' in canceled_tag.text:
                info=canceledInfo
            else:
                complement_info=complementInfo(auction, soup)
                finish_info=finishInfo(auction, soup)
                info={**complement_info,**finish_info}
            logging.debug('updateAuction: Final data information created')
            return info
        else:
            logging.critical(
                'Canceled tag found but with different text', 
                extra={
                    'MainFunction':'updateAuctions',
                    'Function':'updateSelectionProcess',
                    'logging':'First Logging',
                    'id':auction.id,
                    'game_id': auction.id_jogo,
                    'auction_id': auction.id_leilao,
                    'link': auction.link_leilao,
                    'soup': soup.find('body')})
    else:
        logging.critical(
            'Somenthing happened that I dont know',
            extra={
                'MainFunction':'updateAuctions',
                'Function':'updateSelectionProcess',
                'logging':'Second Logging',
                'id':auction.id,
                'game_id': auction.id_jogo,
                'auction_id': auction.id_leilao,
                'link': auction.link_leilao,
                'soup': soup.find('body')
            }
        )
    return None

def canceledInfo():
    info={
        'status':'cancelado',
        'data_alteracao':datetime.now()-timedelta(hours=3)
    }
    logging.debug('updateAuction: Canceled info created')
    return info

def complementInfo(auction, soup):
    try:
        if not auction.local:
            title=soup.find('h3',attrs=('class','title')).text.strip()
            desc=soup.find(id='bloco-descricao-item').text.strip()
            obs=f'{title}/|/|{desc}'
            local=soup.find_all('div',attrs=('class','media-body'))[3].text.split('(')[1].split(')')[0]
            estado_item = soup.find_all('div',attrs=('class','col-xs-12 col-md-6'))[3].text.split(':')[1].strip()
            info={
                'observacoes':obs,
                'local':local,
                'estado_item': 0 if estado_item=='Usado' else 1,
                'data_alteracao':datetime.now()-timedelta(hours=3)
            }
        else:
            info={}
        logging.debug('updateAuction: Complement info created')
        return info
    except:
        logging.error(
            'This page is differente', 
            exc_info=True, 
            extra={
                'MainFunction':'updateAuctions',
                'Function':'complementInfo',
                'id':auction.id,
                'game_id': auction.id_jogo,
                'auction_id': auction.id_leilao,
                'link': auction.link_leilao,
                'soup': soup.find('body')
            }
        )
        sys.exit()

def finishInfo(auction, soup):
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
            info={
                'valor_pago':value,
                'data_fim_leilao':end_date,
                'status':'finalizado',
                'data_alteracao':datetime.now()-timedelta(hours=3)
            }
        else:
            info={}
            
        logging.debug('updateAuction: Finish info created')
        return info
    except:
        logging.error(
            'This page is differente', 
            exc_info=True, 
            extra={
                'MainFunction':'updateAuctions',
                'Function':'finishInfo',
                'id':auction.id,
                'game_id': auction.id_jogo,
                'auction_id': auction.id_leilao,
                'link': auction.link_leilao,
                'soup': soup.find('body')
            }
        )
        sys.exit()