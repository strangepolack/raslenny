import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files

from rich import print
from time import sleep
import os
import socket
import paramiko
from paramiko.ssh_exception import AuthenticationException
from fabric import Connection
from invoke import Responder
from lib_main import findkey
from lib_main import transform_string
from lib_local_factory import factory
from lib_parameters import lenny_dir

banned_start_of_commands = ('cd', 'alias', 'asterisk', 'ping')
banned_commands = ('python',)


class FabricConnection:
    ''' Takes a known host and tries to connect to it with known credentials.
        Also manual connection is possible.
    '''
    dest_dir = lenny_dir
    def __init__(self,
        host, user, password, mac_addr='', hostname='', timeout=1
        ):

        self.host = host
        self.user = user
        self.password = password
        self.mac_addr = mac_addr
        self.hostname = hostname
        self.timeout = timeout  # [s]
        self.conn_object = Connection(
            host=self.host,
            user=self.user,
            connect_kwargs={"password": self.password, "timeout": timeout}
        )

        self.host_info = (
            'IP:'           + self.host +
            '\t\tMAC addr:' + self.mac_addr +
            '\thostname:'   + self.hostname
        )

        self.locals_vs_remotes = []
        self.locals_vs_remotes.append([self.exit, factory(klass='Exit')])
        self.locals_vs_remotes.append([self.shutdown, factory(klass='Shutdown')])
        self.locals_vs_remotes.append([self.reboot, factory(klass='Reboot')])
        self.locals_vs_remotes.append([self.init1, factory(klass='Init1')])
        self.locals_vs_remotes.append([self.init2, factory(klass='Init2')])
        self.locals_vs_remotes.append([self.init3, factory(klass='Init3')])
        self.locals_vs_remotes.append([self.ipauto, factory(klass='IpAuto')])
        self.locals_vs_remotes.append([self.ipstatic, factory(klass='IpStatic')])
        self.locals_vs_remotes.append([self.tshoot, factory(klass='Tshoot')])
        self.locals_vs_remotes.append([self.sendaudios, factory(klass='SendAudios')])
        self.locals_vs_remotes.append([self.makeulaws, factory(klass='MakeUlaws')])
        self.locals_vs_remotes.append([self.addcustoms, factory(klass='AddCustoms')])
        self.locals_vs_remotes.append([self.delcustoms, factory(klass='DelCustoms')])
        self.locals_vs_remotes.append([self.getrecordings, factory(klass='GetRecordings')])
        self.locals_vs_remotes.append([self.delrecordings, factory(klass='DelRecordings')])
        self.locals_vs_remotes.append([self.printmenu, factory(klass='PrintMenu')])

        self.exiting_commands = ()

        self.actions_vs_triggers = {}  # Maps function names to the list of triggers
        self.all_triggers = []
        for item in self.locals_vs_remotes:
            self.actions_vs_triggers[item[0]] = item[1].triggers
            for trigger in item[1].triggers:
                self.all_triggers.append(trigger)


    def init1(self):
        factory(klass='Init1')().action(conn_object=self.multirun)

    def init2(self):
        factory(klass='Init2')().action(conn_object=self.multirun)

    def init3(self):
        factory(klass='Init3')().action(
            conn_object=self.conn_object, singlerun=self.singlerun)

    def exit(self):
        self.conn_object = factory(klass='Exit')().action(conn_object=self.conn_object)

    def shutdown(self):
        self.conn_object = factory(klass='Shutdown')().action(conn_object=self.conn_object)
        self.conn_object = None

    def reboot(self):
        self.conn_object = factory(klass='Reboot')().action(conn_object=self.conn_object)
        self.conn_object = None

    def ipauto(self):
        self.conn_object = factory(klass='IpAuto')().action(conn_object=self.conn_object)
        self.conn_object = None

    def ipstatic(self):
        self.conn_object = factory(klass='IpStatic')().action(conn_object=self.conn_object)
        self.conn_object = None

    def tshoot(self):
        factory(klass='Tshoot')().action(
            conn_object=self.conn_object, singlerun=self.singlerun)

    def sendaudios(self):
        factory(klass='SendAudios')().action(
            conn_object=self.conn_object, singlerun=self.singlerun)

    def makeulaws(self):
        factory(klass='MakeUlaws')().action(conn_object=self.conn_object)

    def addcustoms(self):
        factory(klass='AddCustoms')().action(conn_object=self.conn_object)
        self.conn_object = None

    def delcustoms(self):
        factory(klass='DelCustoms')().action(conn_object=self.conn_object)
        self.conn_object = None

    def getrecordings(self):
        factory(klass='GetRecordings')().action(conn_object=self.conn_object)

    def delrecordings(self):
        factory(klass='DelRecordings')().action(conn_object=self.conn_object)

    def printmenu(self):
        factory(klass='PrintMenu')().action()

    def open(self, verbose=False):
        exit_code = None
        try:
            self.conn_object.open()
        except (
                NameError,
                paramiko.ssh_exception.AuthenticationException,
                paramiko.ssh_exception.SSHException,
                socket.gaierror,
                socket.timeout,
                ConnectionResetError,
                OSError
        ) as error_code:
            exit_code = error_code

        else:
            if verbose is True:
                print('Connected to:', self.host,
                      'MAC addr:', self.mac_addr,
                      'hostname:', self.hostname,
                      )
        return exit_code


    def keep_connection(self):

        print('-' * 96)
        print('-' * 96)
        exit_code = self.open()
        if exit_code is not None:
            print('Failed connecting to:', self.host_info)
            print('Error code:', exit_code)
            self.conn_object = None
        command = None

        while (
            self.conn_object is not None
        ):
            print('-' * 96)
            print('-' * 96)
            print('-' * 96)
            print('-' * 96)
            print('You are connected to the remote host.', self.host_info)
            print(
                'Type "?" for help, "exit" to disconnect, '
                '"shutdown" to shutdown or enter a regular Linux command.'
            )
            command = input('command:>')

            try:
                sleep(0.1)
                if str(command).lower() in ('?', 'help'):
                    self.printmenu()

                elif (str(command).lower().startswith(banned_start_of_commands)
                  or  str(command).lower() in banned_commands
                    ):
                    print('The entered command is banned:', command,
                          ' It will not work with fabric.')

                elif str(command).lower() in self.all_triggers:
                    result = findkey(
                            item=str(command).lower(),
                            dict_of_seqs=self.actions_vs_triggers)
                    if result is not None:
                        result()

                else:
                    command_result = self.singlerun(command)

            except (
                socket.timeout,
                # NameError,
                paramiko.ssh_exception.AuthenticationException,
                paramiko.ssh_exception.SSHException,
                socket.gaierror,
                socket.timeout
                # ConnectionResetError,
                # OSError
                ) as exit_code:
                print('Connection closing. Exit code:', exit_code)

        print('You are now disconnected. Good bye!')
        self.conn_object = None


    def singlerun(self, command, watcher=None, hide=False, warn=True):
        ''' Opens connection and runs one command.
        '''
        result = None
        exit_code = self.open()
        sleep(0.1)
        if exit_code is None and self.conn_object is not None:
            if watcher is None:
                result = self.conn_object.run(
                    command, hide=hide, warn=warn)
            else:
                result = self.conn_object.run(
                    command, hide=hide, warn=warn, watchers=[watcher])

        elif len(command) == 0 and self.conn_object is not None:
            sleep(0.1)

        else:
            print('Cannot re-establish connection and run the command.')
            self.conn_object = None
            exit_code = 'timeout'
        return result


    def multirun(self, commands, hide=False, warn=True):
        '''
        Args:
             commands (list of lists):
        '''
        for command in commands:
            result = None
            print(('-' * 128 + '\n') * 4)
            print('executing command:', command[0])
            watcher = None
            if len(command) in (1, 3):
                if len(command) == 3:
                    pattern = transform_string(
                        input=command[1],
                    )
                    response = command[2] + '\n'
                    watcher = Responder(pattern=pattern, response=response)
                try:
                    self.singlerun(command[0], watcher, hide=hide, warn=warn)
                except (
                    NameError,
                    paramiko.ssh_exception.AuthenticationException,
                    paramiko.ssh_exception.SSHException,
                    socket.gaierror,
                    socket.timeout,
                    ConnectionResetError,
                    OSError
                ) as error_code:
                    exit_code = error_code
                    print('Error executing command(s).')
                    break


def main():
    print('Library for connecting the RPi to your local PC.')


if __name__ == '__main__':
    main()
