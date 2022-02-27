#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import os

import platform

from lib_parameters import hostname_prefix
from lib_parameters import full_hostname
from lib_parameters import lenny_dir
from lib_parameters import asterisk_dir
from lib_parameters import sounds_main_dir
from lib_parameters import comm_set_hostname
from lib_parameters import comm_make_lenny_dir


adjust_commands = []
adjust_commands.append('hostnamectl set-hostname ' + full_hostname)
adjust_commands.append('mkdir -p ' + lenny_dir)
adjust_commands.append('mkdir -p ' + sounds_main_dir)
adjust_commands.append('chown -R asterisk:asterisk' + ' ' + lenny_dir)
adjust_commands.append('chown -R asterisk:asterisk' + ' ' + asterisk_dir)
adjust_commands.append('chown -R asterisk:asterisk' + ' ' + sounds_main_dir)
adjust_commands.append('mkdir -p /var/www/html/admin/modules/blacklistloser')
adjust_commands.append('chown -R asterisk:asterisk /var/www/html/admin/modules/blacklistloser')
adjust_commands.append('cp -n /etc/dhcpcd.conf /etc/dhcpcd.conf.backup')
adjust_commands.append('dos2unix '  + lenny_dir + '*.sh')
adjust_commands.append('dos2unix '  + lenny_dir + '*.py')
adjust_commands.append('dos2unix '  + lenny_dir + '*.txt')
adjust_commands.append('chmod 755 ' + lenny_dir + '*.sh')
adjust_commands.append('chmod 755 ' + lenny_dir + '*.py')
adjust_commands.append('chmod 744 ' + lenny_dir + '*.txt')

def execute_adjust_commands():
    for command in adjust_commands:
        os.popen(command).read()

def main():
    execute_adjust_commands()
    # print('This is a library for storing various (mainly constant) values,')
    # print('directory or file names, etc.')

if __name__ == '__main__':
    main()
