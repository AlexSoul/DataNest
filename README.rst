To use DataNest frist you need to import Datanest module.

i.g 

from datanest import DataNest

Then create configuration file inside %your project's root dicrectory%/conf with .json extension.

For example, MyProject/conf/main.json

{
    "database":{
        "type":"sqlite3",
        "connection":{
            "database":"test.db",
            "username":"test",
            "password":"pass"
        }
    },
    "datasets_path":"mydatasets",
    "datasets": ["auth","reports"]
}


Where database.type stands for database driver (e.g. sqllite3,cx_Oracle,psycopg2,mariadb,etc...) !Don't forget to install the database module, but you don't have to import it into your project!
"database.connection" stands for connection arguments (e.g. TNS, authorization credentials, etc...)

"datasets_path" declares the path to your datasets config files from your project's root directory. For example, "mydatasets" means that DataNest will look up datasets in MyProject/mydatasets/
"datasets": declares a list of dataset configuration files, which must be located inside your "datasets_path" directory, and have .json extension. (i.g. MyProject/mydatasets/reports.json)

The dataset file must have the following json structure:
{
    query_name1:"sql query text $(replacable_parameter)s",
    query_name2:"sql query text $(replacable_parameter)s"
}

Simple dataset for example:

{
    "get_template":"select * from dn_template where name = '%(name)s'",
    "get_templates":"select * from dn_template"
}


____________________________________________________
Operators

To initialize the DataNest module, you must initialize an object.

datanest = DataNest("main") # In this example, "main" goes for your configuration file.

datanest.open() # Opens database connection
datanest.close() # Closes database connection
datanest.query(query_name:str, arguments:dict) # executes sql query, safely replacing all %(param)s with arguments
datanest.commit() # Commits transaction to database
datanest.execute() # Opens a new connection, executes query, and immediately commits and closes connection

____________________________________________________

Simple example of using DataNest in code using dataset above:



from datanest Import DataNest

datanest = DataNest('main')

datanest.open()
template = datanest.query('reports.get_template',{'name':'template_1'})
print (template)
datanest.close()



##############

Yup that's simple =)