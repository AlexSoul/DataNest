class DataNest:

    import json
    import importlib
    import logging as log
    
    from os import getcwd as current_path

    #Attribute constants
    class NestAttributes:
        database = "database"
        datasets = "datasets"
        datasets_path = "datasets_path"
        connection = "connection"
        name = "name"
        type = "type"

    #Simple constants
    json_sufix = ".json"
    dot = "."  
    slash = "/"   
     
    #Semi static variables 
    __version__ = 1.006
    __cur_path = current_path()+slash
    __conf_path = f"{__cur_path}conf/"
    

    #Local variables
    __config = None
    __datasets = None
    __db_module = None
    __db_type : str
    __db_attr = None
    __connection = None
    __cursor = None
    __is_connection_opened = False

    # Simple file load to make code more readable
    def _load_file(self,dataset):
        with open (dataset) as _file:
            return self.json.loads (_file.read())
    
    # Iterating thorugh all queries inside sigle dataset, fills up prepaired dataset. key transforms to dataset.query format.
    def __serialize_sub_dataset(self,dataset_name,queries):
        for query, query_value in queries.items():
            self.__datasets[dataset_name+self.dot+query]=query_value

    # Initiating dataset list        
    def __serialize_dataset(self,dataset_name,queries):
        # Fullfille datasets list if not definied previously
        if self.__datasets is None:
            self.__datasets = {dataset_name+self.dot+query: query_value for query, query_value in queries.items()}
        else: 
            self.__serialize_sub_dataset(dataset_name,queries)

    # Loading datasets and it's queries from dataset file
    def __load_datasets(self):
        try:
            datasets_path = self.__cur_path+self.__config[self.NestAttributes.datasets_path]+self.slash
        except (KeyError):
            self.log.warning (f"Unable to determine datasets path! Add argument: {self.NestAttributes.datasets_path}")
            datasets_path = self.__cur_path
        except (TypeError):
            self.log.critical (f"Unable to load main configuration!")
            raise SystemError ("Unable to load main configuration!")
            
        try:
            # Iterating and loading datasets from files
            for dataset_name in self.__config[self.NestAttributes.datasets]:
                queries = self._load_file(datasets_path+dataset_name+self.json_sufix)
                self.__serialize_dataset(dataset_name,queries)
        except (FileNotFoundError): 
            self.log.warning (f"Unable to locate dataset file: {datasets_path+dataset_name+self.json_sufix} Dataset was not loaded!")

    # Open connection to db
    def open(self):   
        if (not self.__is_connection_opened):
            self.__connection = self.__db_module.connect(**self.__db_attr)
            self.__cursor = self.__connection.cursor()
            self.__is_connection_opened=True

    # Commit changes
    def commit(self):
        try:
            self.__connection.commit()    
        except(AttributeError):
            self.log.error ("Open connection first!")

    # Close connection
    def close(self):
        try:
            self.__cursor.close()
            self.__connection.close()
            self.__is_connection_opened=False
        except(AttributeError):
            self.log.error ("Open connection first!")

    # Wrapper that makes function transactional, (Opens connection, executes function, commits changes, closes connection)
    def _transactional(query_func):
        def wrapper (*args, **kwargs):
            args[0].open()
            result = query_func(*args, **kwargs)
            args[0].commit()
            args[0].close()
            return result
        return wrapper
    
    # Executes simple query, safely inserts parameters
    def query (self, query_name:str, params: dict=None):
        try:
            # When params not defined, executing without formating
            if params:
                result = self.__cursor.execute(self.__datasets[query_name],params)
            else:
                result = self.__cursor.execute(self.__datasets[query_name])
            return result
        except(KeyError):
            self.log.error (f"Wrong dataset or query name: {query_name}")
        except(TypeError):
            self.log.error (f"Wrong dataset or query or parameters types: {query_name}") 
        except(AttributeError):
            self.log.error ("Open connection first!")
    
    # Opens a new connection, executes query, and immediately commits and closes connection
    @_transactional
    def execute (self, query_name:str, params: dict=None):
        return self.query(query_name,params)
    

    # Configuring basic logger patter
    def __config_log(self):
        self.log.basicConfig(level=self.log.DEBUG,
            format='%(asctime)s %(levelname)s %(message)s')

    # Loading main configuration
    def __init__(self, config):
        try:
            self.__config_log()
            self.__conf_path+=config+self.json_sufix
            self.__config = self._load_file(self.__conf_path)
            self.__db_type = self.__config[self.NestAttributes.database][self.NestAttributes.type]
            self.__db_attr = self.__config[self.NestAttributes.database][self.NestAttributes.connection]
            self.__db_module = self.importlib.import_module(self.__db_type)
        except (FileNotFoundError):
            self.log.critical (f"Unable to locate conf file: {self.__conf_path}")
        except (ModuleNotFoundError):
            self.log.critical (f"Wrong database module: {self.__config[self.NestAttributes.database]}")
        self.__load_datasets()         