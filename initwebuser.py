#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files

import re, time
from lib_parameters import asterisk_db
from lib_parameters import ampusers_table
from lib_parameters import db_user
from lib_parameters import db_password
from lib_parameters import host
from lib_parameters import web_admin_name
from lib_parameters import web_admin_sha
from lib_mysql import MySqlConnector


class WebAdminInitiation:
    '''
    Class for automatic creation of an initial web admin user.
    '''
    def __init__(self, asterisk_db, ampusers_table):
        self.asterisk_db = asterisk_db
        self.db_user = db_user
        self.db_password = db_password
        self.host = host
        self.ampusers_table = ampusers_table
        self.web_admin_name = web_admin_name
        self.web_admin_sha = web_admin_sha
        self.connector_to_asterisk_db = MySqlConnector(
            database=self.asterisk_db,
            db_user=self.db_user,
            db_password=self.db_password,
            host=self.host,
        )

    def del_webadmin_from_ampusers_table(self, ampusers_table='ampusers'):
        self.connector_to_asterisk_db.connect()
        self.connector_to_asterisk_db.delete_from_table(table=ampusers_table)
        self.connector_to_asterisk_db.disconnect()

    def add_webadmin_to_ampusers_table(self):
        '''
            Record that needs to be added to or removed from
            the ampusers table.
        '''
        # Del the previous user.
        self.del_webadmin_from_ampusers_table()
        time.sleep(0.5)
        self.connector_to_asterisk_db.connect()
        web_admin_table_fields = []
        web_admin_table_fields.append([
            web_admin_name, web_admin_sha, '', '', '', '*'])
        self.connector_to_asterisk_db.insert_into_table(
            table=ampusers_table, records=web_admin_table_fields)
        self.connector_to_asterisk_db.disconnect()


def main():
    my_class = WebAdminInitiation(asterisk_db, ampusers_table)
    my_class.add_webadmin_to_ampusers_table()
    print('The webuser added.')


if __name__ == '__main__':
    main()
