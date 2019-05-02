#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import requests
from bs4 import BeautifulSoup
from datetime import date
import time
from influxdb import InfluxDBClient
import configparser
import json
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
file_handler = RotatingFileHandler('ranking.log', 'a', 1000000, 1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

def parse_args():
    """Parse the args"""
    logger.info('parse_args')
    parser = argparse.ArgumentParser(
        description='Tool to parse and store ranking metrics from rappelz website')
    parser.add_argument('--host', type=str, required=False,
                        default='localhost',
                        help='hostname influxdb http API')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port influxdb http API')
    parser.add_argument('--configfile', type=str, required=False, default='rappelz-ranking.cfg',
                                    help='config file')
    return parser.parse_args()

def url2table(url):
    """From an url given, extract only the 'rangkingTable' using beautifulsoup"""
    logger.info('url2table')
    response = requests.get(url)
    page_html = response.text
    soup = BeautifulSoup(page_html, 'html.parser')
    rangkingtable = soup.find_all(attrs={"class": "rangkingTable"})[1]
    return rangkingtable

def table2timeseries(table, measurement):
    """convert table to an array of timeseries datapoints in influx format :
    measurement,pseudonyme=xx,classe=xx,guilde=xx,serveur=xx rang=xxi,niveau=xxi timestamp
    measurement = table in influxDB
    pseudonyme = character name
    classe = job name
    guilde = guild name
    serveur = server name
    rang = field with rank value, as integer
    niveau = field with level value, as integer
    timestamp = timestamp
    """
    logger.info('table2timeseries')
    influxtime = date.today().strftime("%Y-%m-%dT03:00:00Z")
    points = []

    rows = table.findAll("tr")
    for row in rows:
        cells = row.findAll("td")
        if len(cells) == 7:
            cell = [i.text for i in cells]
            Rang = cell[0].strip()
            Pseudonyme = cell[2].strip()
            Classe = cell[3].strip()
            Guilde = cell[4].strip()
            Serveur = cell[5].replace(" ", "")
            Niveau = cell[6].strip()
            point = {
                "measurement": measurement,
                "time": influxtime,
                "fields": {
                    "rang": int(Rang),
                    "niveau": int(Niveau)
                },
                "tags": {
                    "pseudonyme": Pseudonyme,
                    "classe": Classe,
                    "guilde": Guilde,
                    "serveur": Serveur
                }
            }
            points.append(point)
    return points

def timeserie2influx(host, port, user, pwd, dbname, datapoints):
    """Connect to InfluxDB and write datapoints"""
    logger.info('timeserie2influx')
    client = InfluxDBClient(host, port, user, pwd, dbname)
    client.write_points(datapoints)
    logger.info('datapoints written')

def main(host, port, configfile):
    logger.info('main')

    config = configparser.ConfigParser()
    config.read(configfile)
    
    markets = json.loads(config.get("common", "markets"))
    limit = int(config['common']['limit'])

    USER = config['influx']['USER']
    PASSWORD = config['influx']['PASSWORD']
    DBNAME = config['influx']['DBNAME']

    for market in markets:
        section = "url-"+market
        servers = json.loads(config.get(section, "servers"))
        url = config[section]['url']
        
        for server in servers:
            for page in list(range(1, limit)):
                page_url = url.replace("SERVER",server).replace("PAGE",str(page))
                logger.info('processing page %s', page_url)
                timeserie2influx(host=host, port=port, user=USER, pwd=PASSWORD, dbname=DBNAME, \
                datapoints=table2timeseries(table=url2table(url=page_url), measurement=market))

if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port, configfile=args.configfile)
