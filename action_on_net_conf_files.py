#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import os

from lib_parameters import line_in_dhcp_file
from lib_parameters import dhcp_file
from lib_parameters import interface_file
from lib_parameters import dhcp_file
from lib_parameters import line_in_dhcp_file
from lib_main import ListOps
from doipauto import ip_auto


def ip_static_net_files(ip_host=None, netmask=None, ip_gw=None, dnses=None):
    ''' Re-write network settings to the Linux conf files.
    '''
    if (
        ip_host is not None and
        netmask is not None and
        ip_gw is not None and
        dnses is not None
    ):
        # Reset the current IP settings first.
        net_conf_lines = []
        net_conf_lines.append('auto eth0')
        net_conf_lines.append('iface eth0 inet static')
        net_conf_lines.append('    address ' + ip_host)
        net_conf_lines.append('    netmask ' + netmask)
        net_conf_lines.append('    gateway ' + ip_gw)
        net_conf_lines.append('    dns-nameservers ' + dnses)

        # The file exists only if static IP is in place.
        ListOps(sequence=net_conf_lines).list_to_file(filename=interface_file)
        os.system('echo' + ' ' + line_in_dhcp_file + ' ' + '>>' + ' ' + dhcp_file)


def main():
    print('File contains functions to assign static ip settings to your RPi host.')


if __name__ == '__main__':
    main()
