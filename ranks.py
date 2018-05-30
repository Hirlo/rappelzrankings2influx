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

def parse_args():
    """Parse the args"""
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
    response = requests.get(url)
    page_html = response.text
    soup = BeautifulSoup(page_html, 'html.parser')
    rangkingtable = soup.find_all(attrs={"class": "rangkingTable"})[1]
    return rangkingtable

def table2timeseries(table, measurement):
    """convert table to an array of timeseries datapoints in influx format :
    measurement,rangs=xx,niveaux=xx,pseudonyme=xx,classe=xx,guilde=xx,serveur=xx rang=xxi,niveau=xxi timestamp
    measurement = table in influxDB
    rangs = tag with rank value
    niveaux = tag with level value
    pseudonyme = character name
    classe = job name
    guilde = guild name
    serveur = server name
    rang = field with rank value, as integer
    niveau = field with level value, as integer
    timestamp = timestamp
    """
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
                    "rang": Rang+"i",
                    "niveau": Niveau+"i"
                },
                "tags": {
                    "rangs": Rang,
                    "niveaux": Niveau,
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
    client = InfluxDBClient(host, port, user, pwd, dbname)
    client.write_points(datapoints)
    time.sleep(3)

def main(host, port, configfile):

    config = configparser.ConfigParser()
    config.read(configfile)
    
    markets = json.loads(config.get("common", "markets"))

    USER = config['influx']['USER']
    PASSWORD = config['influx']['PASSWORD']
    DBNAME = config['influx']['DBNAME']

    for market in markets:
        section = "url-"+market
        servers = json.loads(config.get(section, "servers"))
        url = config[section]['url']
        
        for server in servers:
            for page in list(range(1, 60)):


                page_url = url.replace("SERVER",server).replace("PAGE",str(page))
                timeserie2influx(host=host, port=port, user=USER, pwd=PASSWORD, dbname=DBNAME, \
                datapoints=table2timeseries(table=url2table(url=page_url), measurement=server))

if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port, configfile=args.configfile)
