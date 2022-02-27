#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import os

from lib_parameters import sounds_main_dir
from action_on_conf_files_custom_exten import del_cust_ext_from_files
from action_on_db_custom_exten import del_cust_ext_from_db
from dodel_dialogs import del_dialogs


def del_cust_ext_from_all_entities():
    del_dialogs()
    del_cust_ext_from_files()
    del_cust_ext_from_db()
    print('Custom extensions deleted.')


def main():
    print('This is a script deleting custom extensions from the db and conf files.')
    del_cust_ext_from_all_entities()
    os.system('systemctl isolate reboot')


if __name__ == '__main__':
    main()
