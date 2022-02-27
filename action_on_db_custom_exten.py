#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
# print('=', )

database = 'asterisk'
table = 'kvstore_FreePBX_modules_Customappsreg'
host = 'localhost'


from lib_mysql import MySqlConnector
from lib_parameters import db_user
from lib_parameters import db_password


class CustExtsDb:
    '''
    Represents the DB with all custom extensions.
    Only the names of the custom extensions are significant.
    Eg. 'Lenny', Lenka', etc.
    '''
    def __init__(self, host, db_user, db_password, database, table):

        self.database = database
        self.db_user = db_user
        self.db_password = db_password
        self.host = host
        self.table = table
        self.db_connector = MySqlConnector(
                                            self.database,
                                            self.db_user,
                                            self.db_password,
                                            self.host)
        self.db_connector.connect()

    def del_custom_extens_from_db(self):
        ''' Delete all custom extensions from the db.
        '''
        self.db_connector.delete_from_table(table)

    def add_last_record_to_db(self, index=0):
        '''
            There is one last specific record that must be always added.
        ARG:
            index (int): number of the last element added previously
        '''
        key = 'currentid'
        val = index + 1
        typing = 'NULL'  # Instead of using a built-in 'type' name.
        id = 'noid'
        records = []
        records.append([key, val, typing, id])
        self.db_connector.insert_into_table(table, records)

    def insert_custom_extens_to_db(self, names_of_custom_extens):
        '''
        First, delete all custom extensions from the database.
        Then, write all custom extensions to the database.
        (No functionality for adding custom extensions one by one!)
        Args:
            names_of_custom_extens (list of strs):
            Each str is a name of a custom extension.
            Eg: names_of_custom_extens = ['Lenka', 'Lenny', 'Leon']
        '''
        records = []
        self.del_custom_extens_from_db()

        # A while loop with index must be used,
        # as index is needed also after loop.
        index = 0
        while index < len(names_of_custom_extens):
            ext_name = names_of_custom_extens[index]
            ext_num = index + 1
            key = str(index + 1)
            val = (
                '{\\"destid\\":' + str(ext_num) +
                ',' + '\\"target\\":\\"'           + ext_name +
                ',talk,1\\",\\"description\\":\\"' + ext_name +
                '\\",\\"notes\\":\\"\\",\\"destret\\":\\"0\\",\\"dest\\":\\"NULL\\"}'
                )
            typing = 'json-arr'
            id = 'dests'
            index += 1
            ###
            records.append([key, val, typing, id])
        self.db_connector.insert_into_table(self.table, records)

        # Adding the last element
        self.add_last_record_to_db(index)



def del_cust_ext_from_db():
    CustExtsDb(
        host=host,
        db_user=db_user,
        db_password=db_password,
        database=database,
        table=table
                ).del_custom_extens_from_db()


def add_cust_ext_to_db(list_custom_extens):
    names_of_custom_extens = [item.ext_name for item in list_custom_extens]
    # names_of_custom_extens = []
    CustExtsDb(
        host=host,
        db_user=db_user,
        db_password=db_password,
        database=database,
        table=table
                ).insert_custom_extens_to_db(names_of_custom_extens)


def main():
    print('This is a script for db related operations on custom extensions.')
    add_cust_ext_to_db(list_custom_extens)


if __name__ == '__main__':
    main()
