# rappelzrankings2influx
Parse rankings from rappelz website and store them to influxdatabase

## Prerequisite

###### Install Influxdb

```
apt-get install influxdb
apt-get install grafana
apt-get install python3
apt-get install pip3
```

###### Configure Influxdb

```
Influx
> CREATE USER rappelz WITH PASSWORD 'rappelz'
> CREATE DATABASE rappelz
> GRANT WRITE ON rappelz TO rappelz
```

###### Configure Grafana

add a datasource with at least the following

```
Type = influxDB
URL = http://localhost:8086
Database = rappelz
User = rappelz
Password = rappelz
```

###### Install librarires

```
pip3 install influxdb
pip3 install bs4
```

###### Clone this repo in your workspace

## Usage

Simply run it in a terminal:

```
python3 ranks.py --host **HOST** --port **PORT** --configfile **CONFIGFILE**
```
  
Default values are
```
**HOST** = localhost
**PORT** = 8086
**CONFIGFILE** = rappelz-ranking.cfg
```

### Verify metrics in Influxdb

```
Influx
> use rappelz
> precision rfc3339
> select * from "server_name" order by time desc limit 10
```

## Content of rappelz-config.cfg

```
[common]
markets=array of markets
limit=number of pages to process per server

[influx]
USER=user created in influxdb with write permissions
PASSWORD=password of this user
DBNAME=name of the database created un influxdb

[url-market_as_available_in_the_array_before]
servers=Array of servers name as seen in the original URL
url=http://fr.rappelz.webzen.com/Community/Leaderboard/SERVER/Tout/PAGE#TopRank
```


