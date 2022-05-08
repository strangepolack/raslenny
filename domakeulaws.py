#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files

from lib_parameters import sounds_main_dir
from action_on_sound_files_custom_exten import AudioMainDir

AudioMainDir().make_ulaws()
