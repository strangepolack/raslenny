#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # no '*.pyc' precompiled files
# print('=', )

import re
import ipaddress
from netaddr import IPAddress, IPNetwork
from time import sleep
import os

from lib_parameters import prompt_ip_setings_ready
from lib_parameters import banned_netmasks
from lib_parameters import prompt_gw_ip

from lib_lan import subnet_with_bits
from lib_lan import validate_ip
from lib_lan import validate_netmask
from lib_lan import check_sn_bc

from doipauto import ip_auto

from action_on_net_conf_files import ip_static_net_files


def input_ip_settings():
    ''' An interactive function, where a user inputs setting manually.
    Return:
        lines_to_add (dict): IP settings to be later written to config.
    '''
    exit_code  = None
    final_dict = {}
    ip_setts_exit_codes = {
        'inval_ip': 'You did not enter a valid IP address.',
        'inval_gw': 'You did not enter a valid gateway address.',
        'inval_mask': 'You did not enter a valid subnet mask.',
        'not_in_range': 'The entered IP is not in the valid range.',
        'eq_net': 'The IP entered is the same as its subnet\'s address itself, hence cannot be accepted.',
        'eq_broadcast': 'The IP entered is the same as its subnet\'s broadcast address, hence cannot be accepted.',
        # 'test': 'test',
        'ip_eq_gw': 'The IP address of your Rasberry Pi cannot be the same as the IP of your Gateway.',
        'dns_invalid': 'The entered DNS Server(s) setting are invalid',
        'dns_eq_host': 'The DNS Server(s) IP cannot be the same as the one of your Rpi.',
        'warn_public_ip': 'WARNING!!!\n'
            'You are using public IP addresses for your Raspberry Pi and its network.\n'
            'It is very unlikely, that your network is set up that way.\n'
            'Carry on, only if you know what you are doing.'
    }
    ip_gw = input('Enter the IP of your gateway:')
    if validate_ip(ip_gw) is False:
        exit_code = 'inval_gw'
        final_dict = None
    else:
        final_dict['ip_gw'] = ip_gw

    if exit_code is None:
        netmask = input('Enter Subnet Mask:')
        if (validate_netmask(netmask) is False) or (netmask in banned_netmasks):
            exit_code = 'inval_mask'
            final_dict = None
        else:  # if IP not the same as bc or sn
            mynetwork = IPNetwork(ip_gw + '/' + netmask)
            exit_code = check_sn_bc(ip=ip_gw, subnet=mynetwork)
            if exit_code is not None:
                final_dict = None
            else:
                final_dict['netmask'] = netmask

    if exit_code is None:
        ip_host = input('Enter the IP address of your RPi:')
        if validate_ip(ip_host) is False:
            exit_code = 'inval_ip'
            final_dict = None

        else:
            ip_raspberry = IPAddress(ip_host)
            exit_code = check_sn_bc(ip=ip_raspberry, subnet=mynetwork)
            if ip_raspberry not in mynetwork:
                exit_code = 'not_in_range'
                final_dict = None
            if str(ip_raspberry) == ip_gw:
                exit_code = 'ip_eq_gw'
                final_dict = None

    if exit_code is None:

        # disabled for tests
        dnses = input('Input IP(s) of the DNS server(s), eg. "8.8.8.8 9.9.9.9":')
        ls_dnses = dnses.split(' ')

        if len(ls_dnses) not in (1, 2):
            exit_code = 'dns_invalid'

        else:
            index = 0
            while index < len(ls_dnses) and exit_code is None:
                if validate_ip(ls_dnses[index]) is False:
                    exit_code = 'dns_invalid'
                index += 1

    # Summary checkout
    if exit_code is not None:
        final_dict = None
        print(ip_setts_exit_codes[exit_code])
        print('The network settings will not be changed. Try again.')

    else:  # All settings are valid for a static assignment.
        if ipaddress.ip_address(ip_host).is_private == False:
            exit_code = 'warn_public_ip'
            print(ip_setts_exit_codes[exit_code])
        print('----------------------------------------')
        print('The following network settings will be configured.\n')
        print('IP address of the Raspberry Pi:\t', ip_host)
        print('Subnet Mask:\t\t\t', netmask)
        print('IP address of the Gateway:\t', ip_gw)
        print('DNS Server(s):\t\t\t', dnses)
        print('----------------------------------------')

        if exit_code in (None, 'warn_public_ip'):
            final_dict = {
                'ip_host':  str(ip_host),
                'netmask': str(netmask),
                'ip_gw':   str(ip_gw),
                'dnses':   str(dnses)
                }
        for line in prompt_ip_setings_ready:
            print(line)

    # If provided IP settings are correct
    if final_dict is not None and exit_code in (None, 'warn_public_ip'):
        return final_dict
    else:
        return None

def pass_ip_settings():
    ip_settings = input_ip_settings()
    if ip_settings is None:
        print('You have entered wrong IP settings. Noting will be changed!')
    else:
        ip = ip_settings['ip_host']
        netmask = ip_settings['netmask']
        ip_gw = ip_settings['ip_gw']
        dnses = ip_settings['dnses']
        write_net_setts_to_files(ip, netmask, ip_gw, dnses)
        sleep(0.2)
        os.system("systemctl isolate reboot")


def from_pc_pass_ip_settings(input_args):
    if len(input_args) not in (5, 6):
        print('Missing values for IP settings!')
    else:
        ip_host = input_args[1]
        netmask = input_args[2]
        ip_gw = input_args[3]
        if len(input_args) == 5:
            dnses = input_args[4]
        else:
            dnses = input_args[4] + ' ' + input_args[5]
        write_net_setts_to_files(ip_host, netmask, ip_gw, dnses)
        sleep(0.2)
        os.system("systemctl isolate reboot")


def write_net_setts_to_files(ip, netmask, ip_gw, dnses):
    ip_static_net_files(ip, netmask, ip_gw, dnses)


def main():
    from_pc_pass_ip_settings(input_args=sys.argv)


if __name__ == '__main__':
    main()
