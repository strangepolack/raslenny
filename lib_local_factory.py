#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import os


from rich import print

from lib_main import positive_console
from lib_main import split_list

from doadjust import adjust_commands

from lib_parameters import files_to_put
from lib_parameters import lenny_dir
from lib_parameters import init1_file
from lib_parameters import init2_file
from lib_parameters import file_showtables
from lib_parameters import report_file
from lib_parameters import tshoot_dir
from lib_parameters import files_to_download
from lib_parameters import ipauto_file
from lib_parameters import sounds_main_dir
from lib_parameters import local_lenny_dir
from lib_parameters import local_audio_folder
from lib_parameters import local_recordings_dir
from lib_parameters import recordings_dir
from lib_parameters import file_make_ulaws
from lib_parameters import file_initwebuser
from lib_parameters import file_initmysql
from lib_parameters import file_addcustoms
from lib_parameters import file_recordings
from lib_parameters import file_delcustoms
from lib_main import timestamp
from action_ipstatic import input_ip_settings
from time import sleep


def factory(klass=None):


    class Exit:
        triggers = ('exit', 'quit', 'q', 'leave', 'abandon',)
        description = 'Type one of these to logoff:', triggers

        def action(self, conn_object):
            conn_object.run('exit', hide=False, warn=True)

    if klass == 'Exit':
        return Exit


    class Shutdown:

        triggers = ('shutdown', 'halt',
                    'shutdown -h now',
                    'systemctl isolate shutdown'
                    )

        description = 'Type one of these to shutdown:', triggers

        def action(self, conn_object):
            conn_object.run('systemctl isolate shutdown', hide=False, warn=True)

    if klass == 'Shutdown':
        return Shutdown


    class Reboot:

        triggers = ('reboot', 'shutdown -r now',
                    'systemctl isolate reboot', 'restart',
                    'reload')

        description = 'Type one of these to restart:', triggers

        def action(self, conn_object):
            conn_object.run('systemctl isolate reboot', hide=False, warn=True)

    if klass == 'Reboot':
        return Reboot


    class Init1:
        triggers = ('init1',)
        description = 'Update the raspbx box. Type it for the 1st time and once per month.'

        def action(self, conn_object):
            filename = init1_file
            conn_object(commands=split_list(filename))

    if klass == 'Init1':
        return Init1


    class Init2:
        triggers = ('init2',)
        description = 'Use it to install additional software. Run once, at the beginning.'

        def action(self, conn_object):
            filename = init2_file
            conn_object(commands=split_list(filename))

    if klass == 'Init2':
        return Init2


    class Init3:
        triggers = ('init3',)
        description = 'Run this from time to time and everytime something changes.'

        def action(self,conn_object, singlerun):
            for adjust_command in adjust_commands:
                singlerun(adjust_command)
            for file in files_to_put:
                print('Putting file:', file, 'to:', lenny_dir)
                conn_object.put(file, lenny_dir)
            for adjust_command in adjust_commands:  # Redundant but needed
                singlerun(adjust_command)
            singlerun(lenny_dir + file_initmysql)
            singlerun(lenny_dir + file_initwebuser)

    if klass == 'Init3':
        return Init3


    class Tshoot:
        triggers = ('tshoot',)
        description = 'Download files for troubleshooting purposes'
        def action(self, conn_object, singlerun):
            ''' Function to prepare and download a bundle of files for troubleshooting.
                The bundle will include:
                    - a txt file with information about relevant config files
                    - copied relevant config files
                    - txt file with dump of relevant databases
                It will be then copied to a timestamped folder on your local PC.
            '''
            conn_object.run(lenny_dir + file_showtables)
            conn_object.run('touch' + ' ' + lenny_dir + report_file)
            conn_object.run(lenny_dir + "initmysql.py")
            conn_object.run(lenny_dir + "initwebuser.py")
            local_path = os.path.join(
                local_lenny_dir, tshoot_dir, timestamp() + os.path.sep)
            os.mkdir(local_path)
            sleep(0.1)
            singlerun('echo "start"' + ' > ' + lenny_dir + '/' + report_file)
            for file in files_to_download:
                try:
                    print('line with file to add:', file)
                    singlerun('ls -la ' + file + ' >> ' + lenny_dir + '/' + report_file)
                except:
                    print('Cannot write to the report file.')
            singlerun('echo "end"' + ' >> ' + lenny_dir + '/' + report_file)

            files_to_download.append(lenny_dir + report_file)
            for file in files_to_download:
                print('file:', file)
                try:
                    print('Downloading file:', file)
                    conn_object.get(local=local_path, remote=file)

                except FileNotFoundError:
                    print('File not found:', file)

    if klass == 'Tshoot':
        return Tshoot


    class IpAuto:
        triggers = ('ipauto',)
        description = 'Set automatic IP settings (DHCP will be used)'

        def action(self, conn_object):
            command = lenny_dir + ipauto_file
            conn_object.run(command, hide=False, warn=True)


    if klass == 'IpAuto':
        return IpAuto


    class IpStatic:

        triggers = ('ipstatic', 'ipstat')
        description = 'Set static IP settings'

        def action(self, conn_object):
            ip_settings = input_ip_settings()
            if ip_settings is not None:
                ip = ip_settings['ip_host']
                netmask = ip_settings['netmask']
                ip_gw = ip_settings['ip_gw']
                dnses = ip_settings['dnses']
                ip_settings_to_pass = ip + ' ' + netmask + ' ' + ip_gw + ' ' + dnses

                command = 'python' + ' ' + lenny_dir + 'action_ipstatic.py' + ' ' + ip_settings_to_pass
                conn_object.run(command, hide=False, warn=True)
            else:
                print('Wrong IP settings have been entered!')

    if klass == 'IpStatic':
        return IpStatic


    class DelRecordings:

        triggers = ('delrecordings', 'delrecs')

        description = 'Delete all custom recordings/monologs.'

        def action(self, conn_object):
            command = lenny_dir + file_recordings
            conn_object.run(command, hide=False, warn=True)

    if klass == 'DelRecordings':
        return DelRecordings


    class SendAudios:

        triggers = ('sendaudios', 'sendau')

        description = 'First step to create custom extensions. Send the custom audios (monologs and background) to the RPi. All existing monologs will be deleted.'

        def action(self, conn_object, singlerun):

            command = lenny_dir + file_recordings
            conn_object.run(command, hide=False, warn=True)

            for obj in os.scandir(local_audio_folder):
                if obj.is_dir():
                    print('Folder in the local sounds dir:', obj.name)
                    new_remote_dir = sounds_main_dir + obj.name
                    singlerun('mkdir -p ' + new_remote_dir)
                    for sub_obj in os.scandir(obj.path):
                        if sub_obj.is_file():
                            print('file:', sub_obj.path)
                            print('new_remote_dir:', new_remote_dir)
                            conn_object.put(sub_obj.path, new_remote_dir)
                            if sub_obj.path.endswith('.txt'):
                                singlerun(
                                    'dos2unix ' + new_remote_dir + '/' +
                                    os.path.basename(sub_obj.path)
                                    )

    if klass == 'SendAudios':
        return SendAudios


    class MakeUlaws:

        triggers = ('makeulaws', 'makeu')

        description = 'Second step to create custom extensions. Make ulaw files from the audios you sent.'

        def action(self, conn_object):
            command = lenny_dir + file_make_ulaws
            conn_object.run(command, hide=False, warn=True)

    if klass == 'MakeUlaws':
        return MakeUlaws


    class AddCustoms:

        triggers = ('addcustoms', 'addcust')

        description = 'Third and final step to create custom extensions.'

        def action(self, conn_object):
            command = lenny_dir + file_addcustoms
            conn_object.run(command, hide=False, warn=True)

    if klass == 'AddCustoms':
        return AddCustoms


    class DelCustoms:

        triggers = ('delcustoms', 'delcust')

        description = 'Use this option to delete all custom extensions. All custom monologs will be deleted as well.'

        def action(self, conn_object):
            command = lenny_dir + file_delcustoms
            conn_object.run(command, hide=False, warn=True)

    if klass == 'DelCustoms':
        return DelCustoms


    class GetRecordings:

        triggers = ('downloadrecs', 'downrec')

        description = 'Download result audios, recorded during monologs. (eg with Lenny)'

        def action(self, conn_object):
            '''
            '''
            recordings = []
            recordings = [item for item in recordings if item not in ('', ' ', None)]
            for file in recordings:
                try:
                    print('Downloading recorded file:', file)
                    conn_object.get(
                        local=local_recordings_dir,
                        remote=os.path.join(recordings_dir, file)
                        )
                except FileNotFoundError:
                    print('File not found.:', file)

    if klass == 'GetRecordings':
        return GetRecordings



    list_klasses = []
    list_klasses.append(Exit)
    list_klasses.append(Reboot)
    list_klasses.append(Init1)
    list_klasses.append(Init2)
    list_klasses.append(Init3)
    list_klasses.append(Tshoot)
    list_klasses.append(IpAuto)
    list_klasses.append(IpStatic)
    list_klasses.append(SendAudios)
    list_klasses.append(MakeUlaws)
    list_klasses.append(AddCustoms)
    list_klasses.append(DelCustoms)
    list_klasses.append(GetRecordings)
    list_klasses.append(DelRecordings)

    class PrintMenu:
        triggers = ('?', 'm', 'menu', 'help')
        description = 'Prints help menu. (What you actually see now.)'

        def action(self):
            # global list_klasses
            print('*' * 60)
            print('****************', ' Your options are:', '****************')
            print('*' * 60)
            for klass in list_klasses:
                positive_console.print('Description:', klass.description)
                print('Enter one of these commmands:')
                print(', '.join(klass.triggers))
                print('-' * 10)
            print('Typing:', self.triggers[0], '...displays this menu')
            print('-' * 20)
            print('Anything else ---> Regular Linux command, eg.: ls -la /')

    if klass == 'PrintMenu':
        return PrintMenu


    if klass is None:
        return list_klasses


def main():
    print('Library with commands to execute on the remote host.')



if __name__ == '__main__':
    main()
