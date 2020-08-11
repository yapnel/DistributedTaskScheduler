import pandas
import os
import argparse
import keyring
import logging
import logging.config
from datetime import datetime
import sys
import sqlalchemy as db, sqlalchemy.types
import time

ap = argparse.ArgumentParser(description='This script is used for unpivoting content providers')
man = ap.add_argument_group('Main', 'Mandatory arguements')
man.add_argument("-f", "--file", required=True,help="Excel file")
man.add_argument("-s", "--sheet", required=True,help="Excel sheet")
man.add_argument("-db", "--database", required=True, help="Database to connect to")
man.add_argument("-m", "--mode", required=True, choices=['append','replace'], help="Append or Overwrite the data")
man.add_argument("-t", "--tablename", required=True, help="Table name in Database")

logging.config.dictConfig({
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
      'standard': {
          'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      },
  },
  'handlers': {
      "console":{
              "class": "logging.StreamHandler",
              "formatter": "standard",
              'stream': sys.stdout
      },
      "file": {
              "class": "logging.handlers.WatchedFileHandler",
              "formatter": "standard",
              "filename": os.path.dirname(os.path.realpath(__file__))+'/log/'+datetime.now().strftime("%d-%m-%Y-%H-%M-%S")+'.log',
              "mode": "a",
              "encoding": "utf-8"
      },
  },
  'loggers': {
      '': {
          'level': getattr(logging, 'INFO', None),
          'handlers': ['console','file'],
          'handlers': ['console'],            
          'propagate': True
      }
  }
})
logger = logging.getLogger('unpivot')

def main():
  
  args = vars(ap.parse_args())
  
  filename = os.path.basename(os.path.splitext(args['file'])[0])
  logger.info('Reading excel file')
  df = pandas.read_excel(args['file'],sheet_name=args['sheet'])
  '''
  # remove first empty column
  df.drop(labels='Unnamed: 0',axis=1, inplace=True)
  # get a list of columns
  cols = list(df)
  # move the column to head of list using index, pop and insert
  cols.insert(0, cols.pop(cols.index('Source')))  
  # reorder
  df = df.loc[:, cols]
  '''

  # get a list of columns
  columns = list(df)
  # get the interested header to unpivot
  headers = columns[0:6]
  # get a list of date columns
  months = columns[7:]
  # change all the header columns datatype to object  
  for header in headers:
    df[header] = df[header].astype(object)
  # change all the month columns datatype to float64
  for month in months:
    df[month] = df[month].astype('float64')

  logger.info('Unpivotting data')
  # Unpivot on the headers and create new date and value columns
  df2 = pandas.melt(df,id_vars=headers,value_vars=months,var_name='Date',value_name='Val')

  os.environ["NLS_LANG"]= '.AL32UTF8'
  DbName = args['database']
  connString=keyring.get_password(DbName,DbName) 
  engine=db.create_engine(connString)
  
  dtype1={
  'Outcome': sqlalchemy.types.NVARCHAR(length=255),
  'Sub-outcome':sqlalchemy.types.NVARCHAR(length=255),
  'Scope':sqlalchemy.types.NVARCHAR(length=255),
  'Units':sqlalchemy.types.NVARCHAR(length=5),
  'Definition':sqlalchemy.types.NVARCHAR(length=500),
  'Additional comments':sqlalchemy.types.NVARCHAR(length=500),
  'Source': sqlalchemy.types.NVARCHAR(length=255),  
  'Date':sqlalchemy.types.DATE,
  'Val':sqlalchemy.types.FLOAT
  }
  logger.info('Writing to output')
  start_time = time.time()
  df2.to_sql(args['tablename'], con = engine, if_exists = args['mode'], chunksize = 1000, index = False, dtype=dtype1)
  
  with engine.connect() as connection:
      result = connection.execute("select count(*) as count from "+args['tablename'])
      for row in result:
         count = row['count']

  logger.info('Finished. ' + str(count) + " records inserted and took --- %s seconds ---" % (time.time() - start_time))

if __name__== "__main__":
  main()
