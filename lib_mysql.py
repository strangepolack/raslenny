#!/usr/bin/python
# print('=', )
import sys
#lib_mysql
# No '*.pyc' precompiled files
sys.dont_write_bytecode = True
import mysql.connector
from mysql.connector import Error
# from lib_parameters import lenny_dir_on_pc
# from lib_parameters import asterisk_dir
# from lib_parameters import db_user
# from lib_parameters import db_password
# from lib_parameters import localhost
# from lib_parameters import asterisk_db
# from lib_parameters import sip_table

# def atest():
#     print('aaaa test')

class MySqlConnector:
    '''
    Creates a DB connection object.
    '''
    def __init__(self, database, db_user, db_password, host='localhost'):
        self.host = host
        self.database = database
        self.db_user = db_user
        self.db_password = db_password
        self.connection = None
        self.records = None
        self.db_cursor = None

    def connect(self):
        print('Trying to connect to the db:', self.database)
        if self.connection is None:
            try:
                self.connection = mysql.connector.connect(
                    host=self.host, database=self.database,
                    user=self.db_user, password=self.db_password
                    )
                self.db_cursor = self.connection.cursor(buffered=True)
                print('The connection to the database', str(self.database), 'was successful.')
            except Error as e:
                print('Error connecting to the database:', str(self.database), e)
                self.connection = None
        else:
            print('The connection was already active.')

    def disconnect(self):
        self.db_cursor = None
        print('Trying to disconnect from the database...')
        if self.connection is not None:
            self.connection.close()
            self.connection = None
            print('Disconnected successfully.')
            print('Connection object after:', self.connection)
        else:
            print('There was no active connection.')

    def insert_into_table(self, table, records):
        '''
        Args:
            table:
                The table to be updated.
            records:
                A 2 dimensional iterable (list or tuple)
                One element (record) contains values,
                that will be inserted into the table's field in one record.
                E.g.
                records[0] = ['val_aa', 'val_bb', 'val_cc']
                records[1] = ['val_dd', 'val_ee', 'val_ff']
                Etc...
        Return: None
        '''
        def query_insert_ending(record):
            '''
            This nested function is used to create the ending part of the SQL statement:
            'INSERT INTO'
            It overcomes the issue,
            that the number of fields to be inserted may always vary.
            Params:
                record: (list/tuple)
            Returns:
                query_ending: (str)
                    It is the ending part of the 'INSERT INTO' query.
                    This returns a string with the values in brackets. E.g.:
                    ('aa', 'bb', 'cc');
            '''
            query_ending = ''
            query_ending = ''.join((query_ending, '('))
            query_ending = ''.join((query_ending, '\'', str(record[0]), '\''))
            if len(record) > 1:
                for field in record[1:]:  # As the [0] element was added above
                    query_ending = ''.join((query_ending, ', ', '\'', str(field), '\''))
            query_ending = ''.join((query_ending, ');'))
            return query_ending

        for record in records:
            try:
                sql_command = 'INSERT INTO ' + self.database + '.' + table + ' VALUES ' \
                              + query_insert_ending(record)
                print('Executing the SQL query:', sql_command)
                self.db_cursor.execute(sql_command)
                self.connection.commit()
                print('A record was inserted.')
            except Error as e:
                print('Error inserting the record:')
                print(e)

    def custom_sql_query(self, query):
        '''
        query (str): A custom SQL query
        '''
        output_records = None
        try:
            print('Executing the SQL query:')
            print(query)
            self.db_cursor.execute(query)
            print('Query executed.')
            output_records = self.db_cursor.fetchall()
        except Error as e:
            print('Error selecting the records:')
            print(e)
        return output_records

    def select_from_table(self, table, column='*', condition='', verbose=True):
        '''
        condition: (str)
            An SQL condition
            Examples.: 'id=555' 'number>1'
            (Do not confuse it with a Python condition statement: 'id == 55').
        :return: None
        '''
        output_records = None
        try:
            query_ending = '' if condition == '' else ' WHERE ' + str(condition)
            sql_command = (
                'SELECT ' + column + ' FROM ' + self.database + '.' + table + query_ending + ';'
            )
            if verbose == True:
                print('Executing the SQL query:')
                print(sql_command)
            self.db_cursor.execute(sql_command)
            if verbose == True:
                print('Selecting finished.')
            output_records = self.db_cursor.fetchall()
        except Error as e:
            print('Error selecting the records:')
            print(e)
        return output_records

    def delete_from_table(self, table, condition=None):
        '''
        condition: (str)
            An SQL condition, not a Python condition!
            Examples.:
                'id=555'
                'number>1'
            Default = ''
        :return: None
        '''
        query_ending = '' if condition in ('', None) else ' WHERE ' + str(condition)
        try:
            # sql_command = 'DELETE FROM '  + self.database + '.' + table + ' WHERE ' + str(condition)
            sql_command = 'DELETE FROM ' + self.database + '.' + table + query_ending
            print('Executing the SQL query:', sql_command)
            self.db_cursor.execute(sql_command)
            self.connection.commit()
            print('Deletion finished.')
        except Error as e:
            print('Error deleting the records:')
            print(e)

# mydb = MySqlConnector(database='asterisk', db_user='db_user', db_password='db_password', host='localhost')
# mydb = MySqlConnector(database='asterisk', db_user=db_user, db_password=db_password, host='localhost')
# mydb.connect()
# res=mydb.select_from_table(table='sip', column='*', condition='')
# mydb.disconnect()
# print(res)


# def main():
#     print('This is a library for DB operations.')
# if __name__ == '__main__':
#     main()
