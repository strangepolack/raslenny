import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
from rich import print
# print('=', )

import os
import iptools
import ipaddress
from netaddr import IPAddress, IPNetwork
from ipaddress import ip_network, IPv4Network
from ipaddress import (AddressValueError, NetmaskValueError)
import re

# from scripts.lib_main import file_to_list, list_to_file
# from lib_main import ListOps


def validate_subnet(ip):
    '''
    Validates subnet address, with or without mask bits.
    Both examples are valid:
    '10.10.10.0'
    '10.10.10.0/24'
    Return: (bool):
    '''
    result = True
    try:
        ipaddress.ip_network(ip, strict=False)
    except (ValueError):
        result = False
    return result


def validate_ip(ip):
    '''
    Validates IP address, no mask eg:
    '10.10.10.0' is valid
    '10.10.10.0/24' is not valid
    Return: (bool):
    '''
    result = True
    try:
        ipaddress.IPv4Address(ip)
    except ipaddress.AddressValueError:
        result = False
    return result


def validate_netmask(netmask):
    netmask = str(netmask)
    result = False
    if validate_ip(netmask) is True:
        result = iptools.ipv4.validate_netmask(netmask)
    return result


def check_sn_bc(ip, subnet):
    '''Check if provided IP address
        is not the IP of the subnet itself or broadcast.
    Returns:
        exit_code (str/None):
    '''
    if IPAddress(ip) == IPAddress(subnet.network):
        exit_code = 'eq_net'
    elif IPAddress(ip) == subnet.broadcast:
        exit_code = 'eq_broadcast'
    else:
        exit_code = None
    return exit_code


def subnet_with_bits(ip, netmask):
    '''
    ARGS:
        ip (str): IP address in x.x.x.x format.
            Eg.: '10.10.10.1'
        netmask (str): Netmask address in x.x.x.x format.
            Eg.: '255.255.255.0'

    RETURN:
        subnet (str): Subnet address in the format of IP/bits notation.
            Eg.: '10.10.10.0/24'

    '''
    subnet = str(ip_network(ip + '/' + netmask, strict=False))
    return subnet


def ip_from_net_addr(net_addr):
    '''
    ARGS:
        net_addr (str): Subnet address in one of these form:
        10.10.10.10/255.255.0.0
        172.16.2.1/24
    RETURNS:
        ip (str): IP address of the network, where the input IP is.
                Eg for the input are the examples above the results will be:
                10.10.0.0
                172.16.2.0
    '''
    subnet = str(IPv4Network(net_addr, strict=False).network_address)
    # maskbits = str(
    #     IPAddress(str(IPv4Network(net_addr, strict=False).netmask)).netmask_bits()
    # )
    return subnet

def maskbits_from_net_addr(net_addr):
    '''
    ARGS:
        net_addr (str): Subnet address in one of these form:
        10.10.10.10/255.255.0.0
        172.16.2.1/24
    RETURNS:
        maskbits (str): netmask converted to bits.
                Eg:
                the result maskbits = 24
                if the octet netmask is: 255.255.255.0 
    '''
    # subnet = str(IPv4Network(ip_plus_nm, strict=False).network_address)
    maskbits = str(
        IPAddress(str(IPv4Network(net_addr, strict=False).netmask)).netmask_bits()
    )
    return maskbits

def main():
    print('This is the lan library.')
    #print(maskbits_from_net_addr('1.1.1.1/24'))
    #print(maskbits_from_net_addr('1.1.1.1/255.255.128.0'))
    #print(ip_from_net_addr('10.10.10.10/255.255.0.0'))
    #print(ip_from_net_addr('172.16.2.1/24'))


if __name__ == '__main__':
    main()
