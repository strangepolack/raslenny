#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import os

# When ulaws are in place, the extensions will be conf-ed.

from action_on_sound_files_custom_exten import AudioMainDir
from action_on_conf_files_custom_exten import add_cust_ext_to_files
from action_on_db_custom_exten import add_cust_ext_to_db


def add_cust_exten_to_all_entities():
    list_custom_extens = AudioMainDir().final_extensions()
    if len(list_custom_extens) > 0:
        print('-' * 32)
        for item in list_custom_extens:
            print('A custom extension will be added.')
            print('name:', item.ext_name)
            print('how_many_dialogs:', item.how_many_dialogs)
            print('jump:', item.jump)
            print('background:', item.background)
            print('-' * 8)
        add_cust_ext_to_files(list_custom_extens)
        add_cust_ext_to_db(list_custom_extens)
        os.system('sleep 1')
        # print('Now restarting Asterisk...')
        os.system('systemctl isolate reboot')
    else:
        print('Some ulaw audio or background files may be missing. '
              'No custom extension(s) are to be created!')

def main():
    # print('This is a script adding custom extensions to a db and conf files.')
    add_cust_exten_to_all_entities()



if __name__ == '__main__':
    main()
