import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
from rich import print
# print('=', )

from lib_parameters import lenny_dir
from lib_local_discovery import Discover
from action_local_connect import FabricConnection

from rich.console import Console
from pyfiglet import figlet_format
from lib_main import negative_console
from lib_main import positive_console

user = 'root'
password = 'raspberry'

RPI_MAC_START = 'b827'

# def show_hosts(mac_start='', resolve=True):
def show_hosts(mac_start=RPI_MAC_START, resolve=True):
    ''' It shows all discovered_hosts connected.
    '''
    discovered_hosts = Discover().fullscan(host='', mac_start=mac_start, resolve=resolve)
    print('=' * 64)
    print('=' * 64)
    if len(discovered_hosts) == 0:
        negative_console.print('No discovered hosts found in your network!')
    else:
        positive_console.print('=' * 96)
        # positive_console.print(
        #     figlet_format(
        #         'These are the discovered Raspberry PI hosts, '
        #     'found in your network:', font="cybermedium"
        #     ))
        # positive_console.print(
        #     figlet_format(
        #         'These are the discovered Raspberry PI hosts, '
        #     'found in your network:', font="cybermedium"
        #     ))

        positive_console.print(figlet_format(
            'These are the discovered Raspberry PI hosts,',
            font="cybermedium"))
        positive_console.print(figlet_format('found in your network:',
            font="cybermedium"))
        # positive_console.print(figlet_format('',
        #     font="cybermedium"))



        # print(
        #     'These are the discovered Raspberry PI hosts, '
        #     'found in your network:'
        # )
        for index, discovered_host in enumerate(discovered_hosts):
            print('Host number:', index,
                '  --IP address: ', discovered_host['ip_addr'],
                '  --MAC address: ', discovered_host['mac_addr'],
                '  --Login with ssh possible: ', discovered_host['ssh_open'],
                '  --Discovered hostname: ', discovered_host['hostname']
            )
        positive_console.print('=' * 96)
    return discovered_hosts


def select_host(user, password, mac_start, auto=False, resolve=True):
    final_host = None
    discovered_hosts = show_hosts(mac_start, resolve=resolve)
    if len(discovered_hosts) == 0:
        print('No matching host found to login. Good Bye!')
    elif len(discovered_hosts) == 1:
        print('There is only one matching host found. '
              'You will be logged to it.'
        )
        final_host = discovered_hosts[0]
    else:
        if auto is False:
            option = input('Select the number of the host, you want to log into:')
            if option in [str(elem) for elem in (range(0, len(discovered_hosts)))]:
                final_host = discovered_hosts[int(option)]
                print('Selected:', option)
        else:
            # print('here3')
            final_host = discovered_hosts[0]

    if final_host != None:
        # pass
        host = final_host['ip_addr']
        mac_addr = final_host['mac_addr']
        hostname = final_host['hostname']
        myconn = FabricConnection(host, user, password, mac_addr, hostname)
        myconn.keep_connection()


def autoconnect(host='raspbx.local', user='root', password='raspberry'):
    myconn = FabricConnection(host, user, password)
    myconn.keep_connection()


def main():
    user = 'root'
    password = 'raspberry'
    # show_hosts(mac_start=RPI_MAC_START, resolve=True)
    select_host(user, password, mac_start=RPI_MAC_START, auto=True, resolve=True)
    # select_host(user, password, mac_start=RPI_MAC_START, auto=True, resolve=False)

if __name__ == '__main__':
    main()


