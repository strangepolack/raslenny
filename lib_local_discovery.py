import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
from rich import print

import re
from time import ctime
from socket import gaierror, gethostbyname, gethostbyaddr
from netaddr import IPAddress
from scapy.all import ICMP, IP, sr, srp, TCP, Ether, ARP

from lib_lan import validate_subnet, validate_ip
from lib_main import combine_dicts
from lib_parameters import default_hostnames
from lib_main import ListOps
from lib_local_various import showvar

import ipaddress
import lib_local_ifaces
import socket


class Discover:
    '''
        Having the given local LAN settings, now the hosts will be discovered,
        according to given criteria.
        (Eg. mac_start = 'b827' means that Raspberry Pi boxes will be discovered.
    TODO
        ip_se to improve.
        Should be clearer with calling for ip and mask.
    '''
    def __init__(self, host='', mac_start=''):
        pass
        self.ip_settings = self.ip_setts()

        # self.mac_start = mac_start,

    def host_passed(self, mac_addr, ip_addr, mac_start=''):
        ''' Auxiliary function.
            Filters out results. Passes further, only under the following conditions:
            - mac_start == '' which means no filtering on MAC address
            or
            - mac_addr starts with mac_start
            &
            - ip_addr is not same as the one of the current host
        Returns:
            passed (bool): If True, the host is passed further
        '''
        passed = False
        sanitized_mac = re.sub('[^0-9A-Fa-f]', '', mac_addr)
        if (
            (mac_start == '' or sanitized_mac.lower().startswith(mac_start))
            and
            (ip_addr != self.ip_settings['ip'])
        ):
            passed = True
        return passed

    def get_ip(self, host, verbose=False):
        ''' Gets IP address from the input hostname.
        Args:
            host (str): hostname, that IP you look for.
        Return:
            ip (str/None): IP of resolved host.
        '''
        ip = None
        try:
            ip = gethostbyname(host)
        except gaierror as err:
            pass
            if verbose is True:
                print('The IP of the host:', host, ' not found.')# Error code:', err)
        return ip

    def get_hostname(self, host, verbose=True):
        ''' Gets hostname from the input IP address.
        Args:
            host (str): IP address, that hostname you look for
        Return:
            hostname (str/None): hostname, that you look for
        TODO test: ?change initial hostname to None?
        '''
        hostname = ''
        try:
            get_host = gethostbyaddr(host)
            hostname = get_host[0].lower()
            if '.' not in hostname:
                hostname = ''.join([hostname, '.local'])
        except socket.herror as err:
            pass
            if verbose is True:
                print('The hostname of the IP:', host, ' not found')
        return hostname

    def current_subnet(self):
        ''' Define current subnet in the IP/CIDR form.
        '''
        result_subnet = None
        if self.ip_settings is not None:
            result_subnet = str(
                ipaddress.IPv4Network(
                    self.ip_settings['ip'] + '/' +
                    self.ip_settings['netmask'],
                    strict=False))
        return result_subnet

    def ip_setts(self):
        '''
        Initial evaluation.
        Check if an active and valid network interface exists on your PC.
        '''
        result_settings = None
        input_settings = lib_local_ifaces.IpSettings().final_iface()
        if (
            len(input_settings) > 0
            and
            'ip' in input_settings
            and
            'netmask' in input_settings
        ):
            if 1 == 1:
                result_settings = {
                    'ip': input_settings['ip'],
                    'netmask': input_settings['netmask'],
                }
        else:
            print('No valid connection found. No scanning will be performed.')
        return result_settings

    def eval_input(self, host=''):
        '''
        Check whether IP, subnet or hostname was entered.

        ARGS:
            host (str): The data, that type is to be verified.

        RETURNS:
            evaled_host:
        '''
        evaled_host = None
        current_sn = self.current_subnet()
        if current_sn is not None:
            if host == '':
                    evaled_host = current_sn
            elif validate_subnet(host) is True:  # means IP or subnet
                evaled_host = host
            # hostname to resolve
            elif isinstance(host, str) is True:
                evaled_host = self.get_ip(host)  # Also None may be returned here.
        return evaled_host

    def arpscan(self, host='', mac_start='', verbose=False):
        '''
        ARGS:
            host (str): host, IP or subnet to be scanned.
                default value = '' means,
                the entire current subnet will be scanned.
            mac_start (str): filter on mac addr.

        Returns:
            arp_scan_results (list of dicts):
            One element contains info about a host gathered during the scan.
            The keys are:
                'ip_addr'
                'mac_addr'
                'ssh_open': False - Not relevant yet,
                    just to build the proper dict structure.
                'hostname'
                    Relevant if the scanned host sends out mDNS info.
            If a single host was scanned,
            only an empty or a single element list can be returned.
        '''
        arp_scan_results = []
        hostname = ''
        host_after_eval = self.eval_input(host)
        if host_after_eval is not None:  # valid ip settings
            if verbose is True:
                print('ARP-scanning host:', host_after_eval)
            request = Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=host_after_eval)
            responses, _ = srp(request, timeout=1, retry=1, verbose=verbose)
            if len(responses) > 0:
                print(
                    'Here is the list of all local hosts discovered on your LAN.\n'
                    'Please keep in mind!\n'
                    'Only the ones matching your criteria will be added to the final results.\n'
                    'All discovered hosts:'
                )
                for response in responses:
                    ip_addr, mac_addr = response[1].psrc, response[1].hwsrc
                    sanitized_mac = re.sub('[^0-9A-Fa-f]', '', mac_addr)
                    result = {
                        'ip_addr' : ip_addr,
                        'mac_addr': mac_addr,
                        'ssh_open': None,
                        'hostname': hostname
                    }
                    print(
                        '->IP:', ip_addr,
                        '\t->MAC address:', mac_addr,
                        '\t->Discovered hostname:', hostname,
                    )
                    if self.host_passed(
                        mac_addr=mac_addr,
                        ip_addr=ip_addr,
                        mac_start=mac_start
                    ) is True:
                        if result not in arp_scan_results:
                            arp_scan_results.append(result)
                    else:
                        pass
        return arp_scan_results

    def tcpscan(self, host, dport=22, verbose=False):
        '''
        Uses scapy to test TCP connection,
        for port 22 (ssh)
        '''
        result = False
        if verbose is True:
            print('TCP-scanning host:', host, 'on port:', dport)
        try:
            responses, _ = sr(
                IP(dst=host)/TCP(dport=dport, flags="S"),
                timeout=1, verbose=verbose
            )
            if len(responses) > 0:
                result = True
        except socket.gaierror as err:
            print('Error, hostname not found:', err)
        return result

    def fullscan(self, host='', mac_start='', resolve=True):
        '''
        Performs ARP scan first on a selected host or subnet.
        Then performs SSH scans but only for hosts
        returned from the previous scan.
        ARGS:
            hosts (dict): See arpscan.
            mac_start (str): See arpscan.
            resolve (bool): decides if program should try to resolve IP to hostname
        Returns:
            hosts (list of dicts):
                One element contains info about an active host,
                that responds to ssh.
        '''
        result_hosts = self.arpscan(host, mac_start=mac_start)
        if len(result_hosts) > 0:
        # if result_hosts is not None:
            for host in result_hosts:
                host['ssh_open'] = self.tcpscan(host['ip_addr'])
            for host in result_hosts:
                if resolve is True:
                    hostname = self.get_hostname(host['ip_addr'])
                    host['hostname'] = hostname

        return result_hosts


def main():
    print('Library for discovery of hosts.')


if __name__ == '__main__':
    main()
