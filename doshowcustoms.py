#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # no '*.pyc' precompiled files
from lib_parameters import sounds_main_dir
from action_on_sound_files_custom_exten import AudioMainDir
final_list = AudioMainDir().final_extensions()

if len(final_list) == 0:
    print('There are no custom extensions!')
else:
    for elem in final_list:
        print('-' * 20)
        print('ext_name=', elem.ext_name)
        print('how_many_dialogs=', elem.how_many_dialogs)
        print('jump=', elem.jump)
        print('background=', elem.background)

