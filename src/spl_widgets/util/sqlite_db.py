import sqlite3
from sqlite3 import Error, Connection

# wrapper for convenience (ugly but functional)
def errorhandle_sqlite(warn: bool = False):
    def _errorhandle_sqlite(func):
        def _func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Error as e:
                if warn:
                    print(f"[SQLITE_WARN]: {e}")
                else: raise e

        return _func
    return _errorhandle_sqlite

class SQLiteDB:
    path: str
    connection: Connection
    tables: "dict[str, SQLiteTable]"

    @errorhandle_sqlite(warn=True)
    def __init__(self, path: str, silent: bool = False):
        self.path = path
        self.connection = sqlite3.connect(path)
        if not silent:
            print("Connection Successful!")

        self.tables = {}

        for table in self.query_tables():
            self.tables[table] = SQLiteTable(table, self)

    def query_tables(self):
        return [ n[0].lower() for n in self.execute_read_query("""
            SELECT name FROM sqlite_master
            WHERE type='table';
        """)]

    @errorhandle_sqlite(warn=True)
    def execute_query(self, query: str, *args) -> None:
        cursor = self.connection.cursor()

        cursor.execute(query, *args)
        self.connection.commit()

        cursor.close()

    def executemany_query(self, query: str, data: list[tuple]) -> None:
        cursor = self.connection.executemany(query, data)
        self.connection.commit()
        cursor.close()

    @errorhandle_sqlite(warn=True)
    def execute_read_query(self, query: str) -> list|None:
        cursor = self.connection.cursor()

        cursor.execute(query)
        vals = cursor.fetchall()

        cursor.close()
        return vals
    
    def add_table(self, name: str, fields: list[str], exclude_id: bool = False, **kwargs):
        if (name.lower() in self.query_tables()):
            if kwargs.get("warn_exists"):
                print(f"[WARN]: Table with name '{name}' already exists!")
                return None

            raise NameError(f"[ERROR]: Table with name '{name}' already exists!")

        if ("id" not in [*map(lambda n: n[:2], fields)]) and (exclude_id == False):
            fields = [("id INTEGER PRIMARY KEY AUTOINCREMENT"), *fields]
        
        field_str = ',\n'.join(fields)
        self.execute_query(f"CREATE TABLE {name} ({field_str})")

        self.tables[name] = SQLiteTable(name, self)

    def drop_table(self, name: str) -> None:
        if name in self.tables:
            self.tables.pop(name)

        self.execute_query(f"DROP TABLE {name.lower()}")

    def __exit__(self):
        self.connection.close()

class SQLiteTable:
    name: str
    database: SQLiteDB

    def __init__(self, name: str, database: SQLiteDB):
        self.name = name
        self.database = database

    def _execute_query(self, query):
        self.database.execute_query(query)

    @errorhandle_sqlite()
    def get_colnames(self):
        """Return a list of the columns in this table"""
        cursor = self.database.connection.execute(f"SELECT * FROM {self.name}") # get table
        colnames = [n[0] for n in cursor.description]                           # get titles
        cursor.close()                              # close cursor ( prevent memory leak :) )

        return colnames                             # give back list of columns
    
    def get_num_rows(self):
        """Return the number of items in a table"""
        num_rows = self.database.execute_read_query(
            f"SELECT COUNT(*) FROM {self.name}"
        )[0][0]
        return num_rows