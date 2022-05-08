#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files

# Script to setup MariaDB remote connection.
# Initially, the Python connector cannot be used to create privileges for the remote MySQL user,
# as it is required, that the privileges are already in place, in order for Python to connect.
# So, these will be set up by passing arguments to the OS CLI.

import os
from lib_parameters import db_user, db_password

def sql_add_privs_to_user(db_user, db_password):
    '''Adds privileges to the user, so they can connect to the db.
    Args:
        user (str): User that connects to the db.

    Returns:
        sql_add_priv (str):
            SQL query, that adds a user@localhost (if not existing before)
            and sets up privileges to the DB.
    '''
    sql_add_priv = "GRANT SELECT, INSERT, UPDATE, DELETE ON *.* TO '" + \
           db_user + "'@localhost IDENTIFIED BY '" + \
           db_password + "';"
    print('==============')
    print('An SQL command was executed to add a DB user with permissions.')
    print(sql_add_priv)
    print('==============')
    return sql_add_priv


os_command_start = 'mysql --user=root --password= --execute='
os_command = os_command_start + '"' + sql_add_privs_to_user(db_user, db_password) + '"'
os.system(os_command)
os.system("echo 'This is how the table with users looks like now:'")
os.system("mysql --user=root --password= --execute='SELECT User FROM mysql.user;'")
