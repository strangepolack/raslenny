import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
from rich import print
# print('=', )

from lib_local_various import showvar
from lib_main import combine_dicts

from rich.console import Console
from pyfiglet import figlet_format
from lib_main import negative_console
from lib_main import positive_console

from scapy.all import get_windows_if_list
import netifaces
from netifaces import ifaddresses
from netaddr import IPAddress, IPNetwork
from ipaddress import ip_network
from lib_parameters import EMPTIES


class IpSettings:
    '''
    Works for MS Windows 10 OS.
    Check if there is an active LAN interface providing a valid connection,
    to outside (that is: to the internet in most cases).
    If the PC has multiple network interfaces, only the right one is selected.
    All virtual, vpn, wifi, loopback etc. interfaces will be skipped.
    Uses the "scappy" and "netifaces" libraries.
    Then it extracts the complete network settings from the operating system, like:
    names & description of interfaces, their IP addresses, netmasks etc.
    These cannot be obtained with one library only.
    '''
    # def __init(self, primary_key='guid'):
    #     self.primary_key = primary_key

    # ID of a network interface used by MS Windows
    primary_key = 'guid'

    def scapy_interfaces(self):
        ''' Uses the "scapy" library.
            Extracts partial information about active interfaces.
            The part relates to most but not all settings.
        RETURNS:
            ifaces (list of dicts):
                List of active interfaces with most of their settings.
                Each element contains one interface's incomplete settings.
        '''
        ifaces = []
        items = ('name', 'description', 'guid', 'ipv4_metric', 'netmask', 'gw_ip')
        for iface_from_win in get_windows_if_list():
            dict_to_append = {}
            dict_to_append['ip'] = ''
            for item in items:
                dict_to_append[item] = ''  # Initialize
                if item in iface_from_win:
                    if iface_from_win[item] not in EMPTIES:
                        dict_to_append[item] = iface_from_win[item]

            if 'ips' in iface_from_win:
                if (
                    iface_from_win['ips'] not in EMPTIES
                    and
                    len(iface_from_win['ips']) > 0
                ):
                    dict_to_append['ip'] = iface_from_win['ips'][-1]
            ifaces.append(dict_to_append)
        return ifaces

    def netifaces_interfaces(self):
        '''
        Uses the "netifaces" library.
            Extracts the remaining part of information about active interfaces.
        RETURNS:
            ifaces (list of dicts):
            List of active interfaces and their netmasks.
            Each element contains one interface's incomplete settings.
        '''
        ifaces = []
        for iface in netifaces.interfaces():
            if netifaces.AF_INET in ifaddresses(iface):
                iface_data = ifaddresses(iface)[netifaces.AF_INET]
                dict_to_append = {}
                dict_to_append['netmask'] = ''
                dict_to_append['guid'] = iface
                if 'netmask' in iface_data[0]:
                    dict_to_append['netmask'] = iface_data[0]['netmask']
                ifaces.append(dict_to_append)
        return ifaces

    def netifaces_gateways(self):
        '''
        Uses "netifaces" library .
        Extracts the gateway related information about the interfaces.
        RETURNS:
            gateways (list of dicts):
                Each element contains the gateway setting for one
                active interface.
        '''
        gateways = []
        netifs_gws = netifaces.gateways()
        def_gw_ip = None  # IP address of the default system gw
        def_gw_guid = None  # GUID of the i-face having the def. sys. gw.
        if netifaces.AF_INET in netifs_gws:
            if 'default' in netifs_gws:
                if netifaces.AF_INET in netifs_gws['default']:
                    def_gw_info = netifs_gws['default'][netifaces.AF_INET]
                    def_gw_ip = def_gw_info[0]
                    def_gw_guid = def_gw_info[1]
            intf_gw_infos = netifs_gws[netifaces.AF_INET]
            for intf_gw_info in intf_gw_infos:
                dict_to_append = {'gw_ip': ''}
                dict_to_append['gw_ip'] = intf_gw_info[0]
                dict_to_append['guid'] = intf_gw_info[1]
                if intf_gw_info[1] == def_gw_guid and intf_gw_info[0] == def_gw_ip:
                    dict_to_append['gw_is_def'] = True
                else:
                    dict_to_append['gw_is_def'] = False
                gateways.append(dict_to_append)
        return gateways

    def active_ifaces(self, verbose=True):
        ''' Uses previous functions to bundle
            all information about all active interfaces.

        RETURNS:
            active_ifaces (list of dicts):
                List of all active interfaces on a Windows machine.
                Each element represents one active interface.
                The element of the list may have the following keys:
                    'name'        - name of the interface
                    'description' - description of the interface
                    'guid'        - GUID of the interface object in the OS
                    'ipv4_metric' - metric/cost of the interface
                    'ip'          - IP address of the interface
                    'netmask'     - netmask
                    'gw_ip'       - IP address of the interface's gateway
                    'gw_is_def'   - Warning: This value is not reliable!
                                    Use 'ipv4_metric' in your calculations instead.
                                    Shows if the OS considers it a default gateway.
        '''
        ifaces_combined = combine_dicts(
            self.scapy_interfaces(),
            self.netifaces_interfaces(),
            self.primary_key
        )

        active_ifaces = combine_dicts(
            ifaces_combined,
            self.netifaces_gateways(),
            self.primary_key)
        if verbose is True:
            print('-' * 64)
            print('This is the list of all active interfaces on this PC.')
            for iface in active_ifaces:
                print(iface)
            print('-' * 64)
        return active_ifaces

    def filtered_ifaces(self, verbose=True):
        ''' From the input list of active interfaces,
            filters out the ones that cannot be connecting to outside.
            For PC with one LAN connection only, it is not that relevant.
            But may be important if the PC has more interfaces, eg:
            loopback, virtual etc. These are filtered out.
        ARGS:
            ifaces (list of dicts):
                One element is a dict with all relevant interface's properties.
                Usually it will be the output from previous functions.

            iface_excls (list of strs):
                If an iface's name or desc. includes any of these strs,
                it will be disregarded.

            ip_excls (list of strs):
                If an iface's IP starts with any of these strs,
                it will be disregarded.

            verbose (bool): Decides if debug messages are printed.

        RETURN:
            filtered_results (list of dicts):
                Validated interfaces,
                that can be connecting the host to the outside world.

        '''
        # An interface to be considered:
        # - must not have one of below in its name or description:
        iface_excls = (
            'loop', 'wifi', 'wireless', 'vmware', 'box', 'vpn', 'tunnel'
        )
        # - must not have its IP starting with:
        ip_excls = ('127', '0', '255', '169.254')

        ifaces = self.active_ifaces()
        filtered_results = []
        if verbose is True:
            print('-' * 64)
            print('Interfaces that will be selected or rejected as valid for outside connection:')
        for iface in ifaces:
            reject_reasons = []

            if any(iface_excl in iface['name'].lower()
                   for iface_excl in iface_excls):
                reject_reasons.append('Invalid name. '
                                      'It suggests not a regular LAN connection.')

            if any(iface_excl in iface['description'].lower()
                   for iface_excl in iface_excls):
                reject_reasons.append('Invalid description. '
                                      'It suggests not a regular LAN connection.')

            if iface['ip'].startswith(ip_excls) or len(iface['ip']) == 0:
                reject_reasons.append('Invalid IP address. '
                                      'It suggests an unreachable subnet.')

            if 'gw_ip' not in iface or len(iface['gw_ip']) == 0:
                reject_reasons.append('No gateway IP address.')

            if len(iface['netmask']) == 0:
                reject_reasons.append('Invalid gateway or interface not started yet')

            if len(reject_reasons) > 0:
                if verbose is True:
                    print('-' * 4)
                    negative_console.print('Interface ', iface['name'],
                          'is not valid. Reasons:')
                    for reason in reject_reasons:
                        negative_console.print('\t', reason)
                    print('-' * 64)

            else:  # Only if iface was not rejected for any reasons.
                if verbose is True:
                    positive_console.print('Interface ', iface['name'],
                          'is valid.')
                filtered_results.append(iface)
                filtered_results.sort(reverse=False, key=lambda item: item['ipv4_metric'])

        if verbose is True:
            if len(filtered_results) == 0:
                negative_console.print(
                    'No active interfaces connecting your PC were found!')

        return filtered_results

    def final_iface(self, verbose=True):
        ''' This is the function returning the final result.
            From the list with validated interfaces,
            selects one that has the best metric.

        Return:
            final_dict (dict):
                That is the network interface that is considered,
                to be the one connecting the PC to Internet.
                The keys are:
                    'name'
                    'description'
                    'ip'
                    'gateway'
                    'subnet'

        '''
        final_dict = {}
        filtered_ifaces = self.filtered_ifaces()
        if len(filtered_ifaces) > 0:
            name = filtered_ifaces[0]['name']
            description = filtered_ifaces[0]['description']
            ip =filtered_ifaces[0]['ip']
            netmask =filtered_ifaces[0]['netmask']
            gateway =filtered_ifaces[0]['gw_ip']

            # Transforms IP/bits -> IP & netmask
            subnet = str(ip_network(
                filtered_ifaces[0]['ip'] + '/' + filtered_ifaces[0]['netmask'],
                strict=False
            )
            ).split('/')[0]
            final_dict = {
                'name': name,
                'description': description,
                'ip': ip,
                'netmask': netmask,
                'gateway': gateway,
                'subnet': subnet
            }
            positive_console.print('=' * 96)
            positive_console.print(
                figlet_format(
                    'Final IP and active interface settings', font="cybermedium"
                ))

            if verbose is True:
                positive_console.print('Interf. name:\t', name)
                positive_console.print('Interf. descr.:\t', description)
                positive_console.print('ip:\t\t', ip)
                positive_console.print('netmask:\t', netmask)
                positive_console.print('gateway:\t', gateway)
                positive_console.print('=' * 96)
        return final_dict


def main():
    print('Library for interfaces of your local PC.')


if __name__ == '__main__':
    main()
