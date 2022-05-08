#!/usr/bin/python

import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import pathlib

from lib_main import transform_string
from lib_main import ListOps
from lib_main import AlterFileSection
from lib_parameters import local_test_dir
from lib_parameters import asterisk_dir
from lib_parameters import file_exten_addit
from lib_parameters import file_exten_custom
from lib_parameters import sounds_main_dir

upper_dir = pathlib.PurePath(sounds_main_dir).name


def head_cust_dest():
    head = []
    head.append(';--== end of [dialparties-setrvol] ==--;')
    head.append('')
    head.append('')
    return head


def tail_cust_dest():
    tail = []
    tail.append('[macro-parked-call]')
    return tail


def body_cust_dest(list_custom_extens):
    body = []
    body.append('[customdests]')
    body.append('include => customdests-custom')

    for index, elem in enumerate(list_custom_extens):
        ext_name =  elem.ext_name
        body.append(
            'exten => dest-' + str(index + 1) + ',1,Noop(Entering Custom Destination '
            + ext_name + ')'
        )
        body.append(
            'exten => dest-' + str(index + 1) + ',n,Goto,(' + ext_name + ',talk,1)'
        )
        body.append('')

    body.append(';--== end of [customdests] ==--;')
    body.append('')
    body.append('')
    return body


def body_custom_extens(list_custom_extens, sounds_dir=''):
    '''
    ARG:
    list_custom_extens (list of classes):
        each class contains a custom ext obj with values previously calculated
    '''
    lines_to_file_extens_cust = []

    for value in list_custom_extens:
        lines_to_file_extens_cust.append('[' + value.ext_name + ']')
        lines_to_file_extens_cust.append(
            'exten => talk,1,Set(i=${IF($["0${i}"="0' +
            str(value.how_many_dialogs) + '"]?' +
            str(value.jump) + ':$[0${i}+1])})')
        lines_to_file_extens_cust.append(
            'same => n,ExecIf($[${i}=1]?MixMonitor(${STRFTIME(${EPOCH},,'
            '%Y%m%d_%H%M%S)}_' + value.ext_name + '_${CALLERID(name)}.wav))')
        lines_to_file_extens_cust.append(
            'same => n,Playback(' + upper_dir + '/' + sounds_dir + value.ext_name + '/'
            + value.ext_name + '${i})')
        lines_to_file_extens_cust.append(
            'same => n,BackgroundDetect(' + upper_dir + '/' + sounds_dir
            + value.ext_name + '/' + value.background + ',1500)')
    return lines_to_file_extens_cust


class ExtAdditFile:
    '''
        Represents the file with additional extensions,
        for purpose of adding/deleting them.
    '''
    def __init__(self, source_file, section_head, section_tail):
        self.source_file  = source_file
        self.section_head = section_head
        self.section_tail = section_tail

        self.file = AlterFileSection(
            source_file=self.source_file,
            section_head=transform_string(self.section_head),
            section_tail=transform_string(self.section_tail),
        )

    def del_addit_extens(self):
        '''
        Deletes all additional extensions
        '''
        self.file.del_body()
        print('Custom extensions have been deleted from ext. addit. file!')

    def add_addit_extens(self, section_body):
        '''
        ARGS:
            cust_extens (list of strs) - List of custom extens to add.
                Eg: ['Lenny', 'Lenka']
        '''
        # print('section_body====', section_body)
        self.file.insert_body(section_body)
        print('Custom extensions have been added to ext. addit. file!')


class ExtCustomFile:
    def __init__(self, filename):
        self.filename = filename

    def del_custom_extens(self):
        # Just empty the file.
        with open(self.filename, 'w') as file:
            pass
        # ListOps(sequence=['']).list_to_file(filename=self.filename)
        print('Custom extensions have been deleted from the ext. custom file!')

    # There are no tails or heads, simply write all the lines to file.
    def add_custom_extens(self, lines_custom_extens):  # Just empty the file.
        ListOps(sequence=lines_custom_extens).list_to_file(filename=self.filename)
        print('Custom extensions have been added to ext. custom file!')


def del_cust_ext_from_files():
    ExtCustomFile(file_exten_custom).del_custom_extens()
    ExtAdditFile(
        source_file=file_exten_addit,
        section_head=head_cust_dest(),
        section_tail=tail_cust_dest()
    ).del_addit_extens()


def add_cust_ext_to_files(list_custom_extens):
    ext_custom_file = ExtCustomFile(file_exten_custom)
    ext_add_file = ExtAdditFile(
        source_file=file_exten_addit,
        section_head=head_cust_dest(),
        section_tail=tail_cust_dest()
    )
    if len(list_custom_extens) > 0:
        ext_add_file.add_addit_extens(section_body=body_cust_dest(list_custom_extens))
        ext_custom_file.add_custom_extens(body_custom_extens(list_custom_extens))


def main():
    print('This is a script for files related operations on custom extensions.')


if __name__ == '__main__':
    main()
