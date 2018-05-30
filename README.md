# rappelzrankings2influx
Parse rankings from rappelz website and store them to influxdatabase

##Prerequisite

install Python3 then
pip install influxdb
pip install bs4

##Usage

Simply run it in a terminal:
python3 rank2.py --host <HOST> --port <PORT> --configfile <CONFIGFILE>
  
  Default values are
  HOST = localhost
  PORT = 8086
  CONFIGFILE = rappelz-ranking.cfg
