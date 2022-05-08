#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import os

def del_dialogs():
    os.system('rm -rf /var/lib/asterisk/sounds/custom/*')
    print('Custom extensions deleted.')

def main():
    del_dialogs()

if __name__ == '__main__':
    main()

