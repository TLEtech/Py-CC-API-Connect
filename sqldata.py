import pyodbc as dbc
import pandas as pd
import yaml
import json

# Variables
with open("config.yml", 'r') as configInfo:
    config = yaml.safe_load(configInfo)
ServerName = config['DBC']['server']
DBname = config['DBC']['DB']
DBuser = config['DBC']['ReadUser']
DBuserPW = config['DBC']['PW']
ReadTable = config['DBC']['ReadTable']
ReadQuery = config['DBC']['ReadQuery']
ReadWhere = (config['DBC']['ReadWhere1'] + config['DBC']['ReadWhere2']
             + config['DBC']['ReadWhere3'] + config['DBC']['ReadWhere4'])
ReadOrderBy = config['DBC']['ReadOrderByStmt']

# Create database connection and cursor
Conn = dbc.connect('DRIVER={SQL Server};SERVER='+ServerName+';DATABASE='+DBname+';UID='+DBuser+';PWD='+DBuserPW)
Cursor = Conn.cursor()

# Assemble query statements
ReadQueryStmt = (ReadQuery+ReadTable+ReadWhere)

# Create Pandas dataframe for testing.
df = pd.read_sql(ReadQueryStmt, Conn)

