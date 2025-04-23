from config.bot_config import db_config
from config.config import *
from config.SQL import *
import psycopg2 as pg, logging
from psycopg2 import Error

logger = logging.getLogger(__name__)

class TEntity:
  def __init__(self, table_name: str):
    self.__name = table_name 
    self.__fields = ['*']
    try:
      self.__connect = pg.connect(**db_config)
    except (Exception, Error) as error:
      logger.error(f'[{self.__name__}.__init__] Create connect not successfull[{type(error)}:{error}]')

  @property
  def Name(self):
    return self.__name
  
  @property
  def Connect(self):
    if self.__connect:
      return self.__connect 
    else: 
      logger.warning(f'[{self.__name__}.Connect] Create connect first]')
      raise Exception
      
  @property
  def Fields(self):
    return self.__fields
  
  @property
  def FieldsCount(self) -> int:
    return 0 if self.__fields[0] == '*' else len(self.__fields)

  def AddField(self, *Name: str):
    for Item in Name:
      try:
        self.__fields.index(Item)
      except:
        self.DelField('*')
        self.__fields.append(Item)

  def SetFieldsFromDB(self):
    with self.Connect.cursor() as Query:
      try:
        SQL = COLUMN_BY_TABLE % self.__name + 'dwadw'
        Query.execute(SQL)
        DataSet = Query.fetchall()
        for item in DataSet:
          self.AddField(item[0]) 
      except:
        logger.error(f'[{self.__class__.__name__}.GetFieldsFromDB] Bad request\n\t{SQL}')
      finally:
        Query.close()
        
  def DelField(self, *Name: str):
    for Item in Name:
      try:
        self.__fields.remove(Item)
        if len(self.__fields) == 0:
          self.AddField('*')
      except: pass


if __name__ == '__main__':
  logging.basicConfig(format = log_pattern, level = log_level, filename = log_path + delimetr + log_file_name)
  User = TEntity('users')
  User.SetFieldsFromDB()
  print(User.Fields)
