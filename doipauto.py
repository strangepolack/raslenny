#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import os
from lib_parameters import line_in_dhcp_file
from lib_parameters import dhcp_file
from lib_parameters import interface_file
from lib_main import ListOps
from time import sleep


def ip_auto(dhcp_file, line_in_dhcp_file, interface_file):
    ''' Restore the default network settings.
        That is, eth0 gets its IP from DHCP.
    '''
    # Reset file content
    with open(file=interface_file, mode='w') as f:
        pass
    os.system("rm -f " + interface_file)  # Delete the intf file
    # Enable dhcp client on the i-face
    ListOps().del_file_line(filename=dhcp_file, line_to_remove=line_in_dhcp_file)
    print("Automatic IP settings will be applied on your RPi.")


def apply_ip_auto():
    '''
    This will be executed only when this file is executed.
    That means, the final purpose is only to apply the auto IP settings.
    Then reboot is the last step.
    '''
    ip_auto(
        dhcp_file=dhcp_file,
        line_in_dhcp_file=line_in_dhcp_file,
        interface_file=interface_file
        )
    sleep(0.2)
    os.system("systemctl isolate reboot")


def main():
    apply_ip_auto()


if __name__ == '__main__':
    main()
