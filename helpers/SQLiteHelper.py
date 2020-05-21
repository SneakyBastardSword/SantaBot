import sqlite3
from sqlite3 import Error

class SQLiteHelper():
    def __init__(self, connection_path: str):
        self.__connection_path = connection_path
        self.__connection = None

    def create_connection(self):
        try:
            if(self.__connection == None):
                self.__connection = sqlite3.connect(self.__connection_path)
            print("Connection to SQLite DB successful")
        except Error as e:
            print("The error '{0}' occurred".format(e))

    def execute_query(self, query):
        if(self.__connection == None):
            print("Connection has not been created")
        
        cursor = self.__connection.cursor()
        try:
            cursor.execute(query)
            self.__connection.commit()
            print("Query executed successfully")
            return True
        except Error as e:
            print("The error '{0}' occurred".format(e.with_traceback))
            return False

    def create_table(self, table_name: str, table_format: str):
        '''
        example_usage -->

        ex_table_name = "users"

        ex_table_format = "(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            nationality TEXT
        )"

        ~~~

        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            age INTEGER,

            gender TEXT,

            nationality TEXT

        );
        '''
        table_query = """
        CREATE TABLE IF NOT EXISTS {0} {1};
        """.format(table_name, table_format)
        return self.execute_query(table_query)


    def insert_records(self, table_name: str, column_list: str, values: list):
        '''
        example usage -->
        
        ex_table_name = "users",
        
        ex_column_list = "(name, age, gender, nationality)",
        
        ex_values = ["('James', 25, 'male', 'USA')", "('Leila', 32, 'female', 'France')"]

        ~~~

        INSERT INTO users (name, age, gender, nationality)

        VALUES
        
            ('James', 25, 'male', 'USA'),
            
            ('Leila', 32, 'female', 'France');
        '''
        value_str = ",".join(values)
        table_query = """
        INSERT INTO
            {0} {1}
        VALUES
            {2};
        """.format(table_name, column_list, value_str)

        return self.execute_query(table_query)

    def execute_read_query(self, query):
        cursor = self.__connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print("Problem reading - the error '{0}' occurred".format(e))

    def execute_delete_query(self, table_name: str, conditions: str):
        delete_query = "DELETE FROM {0} WHERE {1}".format(table_name, conditions)
        return self.execute_query(delete_query)

    def execute_update_query(self, table_name: str, new_column_data: str, conditions: str):
        update_query = """
        UPDATE
            {0}
        SET
            {1}
        WHERE
            {2}
        """.format(table_name, new_column_data, conditions)
        return self.execute_query(update_query)