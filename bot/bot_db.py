from typing import Any
from config.bot_config import db_config
from config.config import *
from config.SQL import *
import psycopg2 as pg, logging
from psycopg2 import Error

logger = logging.getLogger(__name__)

class TFields:
  def __init__(self, aParams):
    self.__params = aParams
    self.__fields_name = self.GetParamByIndex(0, aParams)
    self.__fields_type = self.GetParamByIndex(1, aParams)
  
  def __str__(self) -> str:
    return str(self.__params)
  
  def __getitem__(self, item):
    return self.__params[item]

  @property
  def Params(self):
    return self.__params

  @property
  def Names(self):
    return self.__fields_name
  
  @property
  def Types(self):
    return self.__fields_type
  
  @property
  def Count(self):
    return len(self.__fields_name)
  
  def IndexOf(self, Name):
    try:
      return self.Names.index(Name)
    except:
      return -1
  
  def GetParamByIndex(self, aIndex, aParams):
    if len(aParams[0]) >= aIndex:
      return [field[aIndex] for field in aParams]
    else:
      raise IndexError('Index out of range')
    

  
class TEntity:
  __connect = None
  __name = ''
  __fields= None
  def __init__(self, table_name: str):
    self.__name = table_name 
    self.__connect = self.GetConnect(db_config)
    self.__fields = TFields(self.GetFieldsByTable(table_name))

  def __del__(self):
    self.__connect.close()
    
    
  @property
  def Name(self):
    return self.__name
  
  @property
  def Connect(self):
    if self.__connect:
      return self.__connect 
    else: 
      logger.warning(f'[{self.__class__.__name__}.Connect] Create connect first]')
      raise Exception('Connect dont create')
      
  @property
  def Fields(self):
    return self.__fields
  
  
  def GetConnect(self, config):
    logger.info('Create connect...')    
    try:
      return pg.connect(**config)
    except (Exception, Error) as error:
      logger.error(f'[{self.__class__.__name__}.__init__] Create connect not successfull[{type(error)}:{error}]')     
      return None


  def GetFieldsByTable(self, tbl_name):
    logger.info(f'Get fields by table[{tbl_name}]...') 
    with self.Connect.cursor() as Query:
      try:
        SQL = COLUMN_BY_TABLE % tbl_name
        Query.execute(SQL)
        return Query.fetchall()
      except:
        logger.error(f'[{self.__class__.__name__}.GetFieldsByTable] Bad request\n\t{SQL}')
      finally:
        Query.close()

  # def AddField(self, *Name: str):
  #   for Item in Name:
  #     try:
  #       self.__fields.index(Item)
  #     except:
  #       self.DelField('*')
  #       self.__fields.append(Item)
        
  # def DelField(self, *Name: str):
  #   for Item in Name:
  #     try:
  #       self.__fields.remove(Item)
  #       if len(self.__fields) == 0:
  #         self.AddField('*')
  #     except: pass


if __name__ == '__main__':
  logging.basicConfig(format = log_pattern, level = log_level, filename = log_path + delimetr + log_file_name)
  User = TEntity('users')
  # print(User.Fields.Names)
  # print(User.Fields.Types)
  # print(User.Fields.IndexOf('hashtag'))
  # print(User.Fields.IndexOf('hash'))
  # print(User.Fields.Params)
  print(User.Fields[1])
  print(User.Fields)
