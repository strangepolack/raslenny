import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import paramiko
from getpass import getpass
from lib_parameters import lenny_dir
from action_local_connect import FabricConnection

RPI_MAC_START = 'b827'


def askconnect():
    host = input('Enter hostname/IP:')
    user = input('Enter username:')
    print('Attention!. No stars (*) will show upon entering password, just a blank space!')
    password = getpass('Enter password:')
    myconn = FabricConnection(host, user, password)
    myconn.keep_connection()


def main():
    askconnect()

if __name__ == '__main__':
    main()


