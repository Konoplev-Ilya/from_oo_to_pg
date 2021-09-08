# -*- coding: utf8 -*-

import asyncio

from db import setup_db, Visitor
from config import base_url, list_clients_url, username_digialq, passwd_digialq
from config import login_pg, pass_pg, host_pg
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def write_rows(rows, sessin_db):
    for row in rows:
        visitor = []
        for i in row.find_all('td'):
            if i.span.text == '---':
                visitor.append(None)
            else:
                visitor.append(i.span.text)
        if visitor[7]:
            visitor[7] = visitor[7][3:6] + visitor[7][0:3] + visitor[7][6:] + '+03'
        
        if visitor[8]:
            visitor[8] = visitor[8][3:6] + visitor[8][0:3] + visitor[8][6:] + '+03'
        
        if visitor[9]:
            visitor[9] = visitor[9][3:6] + visitor[9][0:3] + visitor[9][6:] + '+03'
        
        exist_visitor = session_db.query(Visitor).filter_by(id=int(visitor[2])).first()
        if exist_visitor:
            exist_visitor.status = visitor[0].strip()
            exist_visitor.work_place = visitor[3].strip()
            exist_visitor.start_time = visitor[8]
            exist_visitor.finish_time = visitor[9]
        else:
            session_db.add(Visitor(visitor[0].strip(),
                        int(visitor[1]),
                        int(visitor[2]),
                        visitor[3].strip(),
                        visitor[5].strip(),
                        visitor[7],
                        visitor[8],
                        visitor[9]))
        session_db.commit()
        # with session_db.query(Visitor).filter_by(id=int(visitor[2])).first() as exist_visitor:
        #     exist_visitor.status = visitor[0].strip()
        #     exist_visitor.num_in_day = int(visitor[1])
        #     exist_visitor.id = int(visitor[2])
        #     exist_visitor.work_place = visitor[3].strip()
        #     exist_visitor.name_service = visitor[5].strip()
        #     exist_visitor.reg_time = visitor[7]
        #     exist_visitor.start_time = visitor[8]
        #     exist_visitor.finish_time = visitor[9]

        # session_db.add(Visitor(visitor[0].strip(),
        #                 int(visitor[1]),
        #                 int(visitor[2]),
        #                 visitor[3].strip(),
        #                 visitor[5].strip(),
        #                 visitor[7],
        #                 visitor[8],
        #                 visitor[9]))
        # #print(visitor[3].strip())
        # session_db.commit()

async def get_and_write(session_db):
    async with aiohttp.ClientSession() as session:
        jar = aiohttp.CookieJar(unsafe=True)
        session = aiohttp.ClientSession(cookie_jar=jar)
        async with session.get(base_url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            login_url = soup.form.attrs['action']
            url_post_login = urljoin(base_url, login_url)
        async with session.post(url_post_login, data = {'username' : username_digialq, 'password' : passwd_digialq}) as response:
            html = await response.text()

        #list_clients_url,  fucn(list_clients_url, session, session_db, date_to)
        url_next_page = list_clients_url
        while url_next_page:
            async with session.get(url_next_page) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                next_page = soup.find(title = 'Go to next page').attrs['href']
                url_next_page = urljoin(list_clients_url, next_page)
                rows = soup.find('table', 'table').tbody.find_all('tr')
                #while next_page:
                write_rows(rows, session_db)




if __name__ == '__main__':
    session_db = setup_db(login_pg, pass_pg, host_pg)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_and_write(session_db))