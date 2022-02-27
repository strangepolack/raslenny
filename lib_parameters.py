#!/usr/bin/python
#lib_parameters

import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import os
EMPTIES = ('', [], (), {}, set(), None)

# This is a library for storing various (mainly constant) values, usernames,
# directory or file names, etc.
# Also: file headers, extensions, trunk names, sip settings, etc.
import sys
# import platform
import socket

local_lenny_dir = 'D:\\raslenny\\'


hostname_prefix = 'raslenny'
hostname_suffix = '.local'
full_hostname = hostname_prefix + hostname_suffix
default_hostnames = ('raspbx.local', full_hostname)
default_hostname = default_hostnames[0]
default_user = 'root'
default_password = 'raspberry'
tshoot_dir = 'tshoot'

init1_file = 'init1.txt'
init2_file = 'init2.txt'
adjust_file = 'doadjust.py'
ipauto_file = 'doipauto.py'
file_showtables = 'doshowtables.py'
net_script   = 'changeip.py'
comm_set_hostname = 'hostnamectl set-hostname ' + full_hostname
lenny_dir = '/opt/' + hostname_prefix + '/'
comm_make_lenny_dir = 'mkdir -p ' + lenny_dir
# comm_make_lenny_dir = 'mkdir -p ' + '/opt/' + hostname_prefix + '/'

# Files with commands for initialization

# Folder where subfolders with custom audio dialog and background files are located.
# sounds_main_dir = '/var/lib/asterisk/sounds/en/'
sounds_main_dir = '/var/lib/asterisk/sounds/custom/'

#call recordings location
local_recordings_dir = local_lenny_dir + 'recordings' + '\\'
recordings_dir = "/var/spool/asterisk/monitor/"
etc_dir = '/etc/'
asterisk_dir = '/etc/asterisk/'
path_to_ffmpeg = 'ffmpeg'
# path_to_ffmpeg = path_to_ffmpeg_on_rpi


# Dialog/background audios to be sent to rpi from this dir
local_audio_folder = local_lenny_dir + 'audios' + '\\'

# Result recordings to be downloaded to this dir

local_test_dir = local_lenny_dir + 'tests\\'
path_to_ffmpeg_on_pc = 'C:\Programs\\ffmpeg\\bin\\ffmpeg.exe'


dhcp_file = '/etc/dhcpcd.conf'
interface_file = '/etc/network/interfaces.d/eth0'
line_in_dhcp_file = 'denyinterfaces eth0'

exten_num = '33'       # This is your initial extension number.

# Do not edit the parameters below.
# This will not work, due to the salted hash!
exten_pass = 'password'  # This is the password for your initial
                         # extension number.
# The below must was calculated by the FreePBX, do not edit it!
exten_pass_hash = '$2a$08$iviEUwg.WoZN0VREhWEbjONRKIXj1s9lLXJi9iz6wkDfTKvfnptR.'

#############################################
web_admin_name = 'webadmin'
# The pass is: 'webpass' but it is not used in the db, only its hash (below) is.
# Hash for the webadmin's  pass:
web_admin_sha  = '94d33e528aa5c3a4386d3b3f1f0984a177968dec'
db_user        = 'db_user'
db_password    = 'db_password'
localhost      = 'localhost'
host = 'localhost'
asterisk_db    = 'asterisk'
devices_table  = 'devices'
userman_users_table = 'userman_users'
users_table    = 'users'
ampusers_table = 'ampusers'
sip_table      = 'sip'


file_pjsip_trans = asterisk_dir + 'pjsip.transports.conf'
file_exten_addit = asterisk_dir + 'extensions_additional.conf'
file_exten_custom = asterisk_dir + 'extensions_custom.conf'
file_sip_general_addit = asterisk_dir + 'sip_general_additional.conf'
file_net_conf       = 'dhcpcd.conf'
file_pjsip_aor      = 'pjsip.aor.conf',
file_pjsip_auth     = 'pjsip.auth.conf',
file_pjsip_endpoint = 'pjsip.endpoint.conf',
file_pjsip_identify = 'pjsip.identify.conf',
file_sip_add = 'sip_additional.conf'
file_sip_reg = 'sip_registrations.conf'
file_make_ulaws  = 'domakeulaws.py'
file_initwebuser = 'initwebuser.py'
file_initmysql  = "initmysql.py"
dbs_dump_file   = 'aaa_dbs_dump.txt'
report_file     = 'aa_report_file.txt'
file_recordings = 'dodeldialogs.py'
file_addcustoms = 'doaddcustoms.py'
file_delcustoms = 'dodelcustoms.py'
# shutdown_commands = ('poweroff', 'shutdown -s now', 'halt', 'systemctl isolate poweroff')
# reboot_commands = ('reboot', 'shutdown -r now', 'systemctl isolate reboot')


# Config files to download for tshooting purposes
files_to_download = []
files_to_download.append(lenny_dir + dbs_dump_file)
files_to_download.append(etc_dir + file_net_conf)
files_to_download.append(etc_dir + 'amportal.conf')
files_to_download.append(file_exten_addit)
files_to_download.append(file_exten_custom)
files_to_download.append(asterisk_dir + 'pjsip.aor.conf')
files_to_download.append(asterisk_dir + 'pjsip.auth.conf')
files_to_download.append(asterisk_dir + 'pjsip.endpoint.conf')
files_to_download.append(asterisk_dir + 'pjsip.identify.conf')
files_to_download.append(asterisk_dir + 'sip_additional.conf')
files_to_download.append(asterisk_dir + 'sip_registrations.conf')
files_to_download.append(asterisk_dir + 'pjsip.transports.conf')
files_to_download.append(asterisk_dir + 'sip_general_additional.conf')

# Databases that may be needed to dump for tshooting.
dbs_to_dump = []
dbs_to_dump.append('asterisk')

# DBs below are commented for purpose.
# dbs_to_dump.append('asteriskcdrdb')
# dbs_to_dump.append('information_schema')
# dbs_to_dump.append('mysql')
# dbs_to_dump.append('performance_schema')

# Script files that should be transferred from pc to raspberry.
files_to_put = []
# files_to_put.append(local_lenny_dir + '')
files_to_put.append(local_lenny_dir + adjust_file)
files_to_put.append(local_lenny_dir + file_make_ulaws)
files_to_put.append(local_lenny_dir + 'action_ipstatic.py')  # Leave it
files_to_put.append(local_lenny_dir + 'action_on_conf_files_custom_exten.py')
files_to_put.append(local_lenny_dir + 'action_on_db_custom_exten.py')
files_to_put.append(local_lenny_dir + 'action_on_net_conf_files.py')
files_to_put.append(local_lenny_dir + 'action_on_sound_files_custom_exten.py')
files_to_put.append(local_lenny_dir + 'dodeldialogs.py')

files_to_put.append(local_lenny_dir + file_addcustoms)
files_to_put.append(local_lenny_dir + file_delcustoms)
files_to_put.append(local_lenny_dir + 'doipauto.py')
files_to_put.append(local_lenny_dir + 'doshowcustoms.py')
files_to_put.append(local_lenny_dir + file_showtables)
files_to_put.append(local_lenny_dir + file_initmysql)
files_to_put.append(local_lenny_dir + file_initwebuser)
files_to_put.append(local_lenny_dir + 'lib_main.py')
files_to_put.append(local_lenny_dir + 'lib_mysql.py')
files_to_put.append(local_lenny_dir + 'lib_lan.py')

files_to_put.append(local_lenny_dir + 'lib_parameters.py')






# Prompt to provide further IP settings
prompt_dns_setts = []
prompt_dns_setts.append('----------------')
prompt_dns_setts.append('You need to provide the IP adress(es) of the DNS server(s).')
prompt_dns_setts.append('You can provide one or two custom IP address(es) of the DNS server(s).')
prompt_dns_setts.append('If you provide two IPs, they should be separated by space.')
prompt_dns_setts.append('Eg:8.8.8.8')
prompt_dns_setts.append('Or:8.8.8.8 9.9.9.9')


prompt_ip_setings_ready = []

prompt_gw_ip = 'To configure static network settings, enter now the IP address of your Gateway/Router:'

# Prompt says, that the IP settings are being delivered.
prompt_ip_setings_ready.append(
    'The settings have been writen to the network configuration files. '
    'RPi is rebooting...')
    # 'but they are not active yet.')
# prompt_ip_setings_ready.append('In order to activate the settings, you need to reboot your Raspberry Pi.')
# prompt_ip_setings_ready.append('(Eg. by typing:)')
# prompt_ip_setings_ready.append('reboot<ENTER>')
# prompt_ip_setings_ready.append(
#     'If you do not want the settings to become active after reboot, '
#     'run the program again now.')

# These netmasks are invalid to be set for the host.
banned_netmasks = ('0.0.0.0', '255.255.255.254', '255.255.255.255')

def main():
    print('This is a library for storing various (mainly constant) values,')
    print('directory or file names, etc.')

if __name__ == '__main__':
    main()
