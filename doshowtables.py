#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # no '*.pyc' precompiled files

from lib_mysql import MySqlConnector
from lib_parameters import asterisk_dir
from lib_parameters import lenny_dir
from lib_parameters import db_user
from lib_parameters import db_password
from lib_parameters import dbs_to_dump
from lib_main import ListOps
from lib_parameters import dbs_dump_file

host = 'localhost'

def show_tables():
    all_dbs_results = []
    for database in dbs_to_dump:
        connection_to_database = MySqlConnector(database, db_user, db_password, host)
        print('*' * 40, "connecting to:", database, '*' * 10)
        connection_to_database.connect()
        all_dbs_results.append('*' * 10 + 'DATABASE:' + database + '*' * 60)
        results = connection_to_database.custom_sql_query(
                        query="SHOW TABLES FROM " + database
        )
        # As the result is a list of tuples.
        tables = [result[0] for result in results]
        for table in tables:
            print('-' * 24)
            all_dbs_results.append('-' * 24)
            print('TABLE:', table)
            all_dbs_results.append('')
            all_dbs_results.append('TABLE:' + str(database) + '.' + str(table))
            all_dbs_results.append('--Columns:')
            result_records = connection_to_database.custom_sql_query(
                'SHOW COLUMNS FROM ' + database + '.' + table)
            for elem in result_records:
                print(elem)
                all_dbs_results.append(str(elem))
            all_dbs_results.append('-' * 8)
            all_dbs_results.append('--Records:')
            result_records = connection_to_database.custom_sql_query(
                'SELECT * FROM ' + database + '.' + table)
            print('--Records in the:')
            for elem in result_records:
                print(elem)
                all_dbs_results.append(str(elem))
            all_dbs_results.append('-' * 24)
            print('=' * 10)
        connection_to_database.disconnect()
        print('*' * 70)
        all_dbs_results.append('*' * 70)
    ListOps(sequence=all_dbs_results).list_to_file(filename=lenny_dir+dbs_dump_file)


def main():
    show_tables()


if __name__ == '__main__':
    main()
