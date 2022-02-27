#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import platform


import os
import subprocess
import re
from rich.console import Console

console_background = "grey70"
negative_console = Console(style="red")
positive_console = Console(style="blue on " + console_background)

def timestamp():
    from datetime import datetime
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")[:-2]


class ListOps:
    ''' Class contains various functions for operations on lists.
    '''
    def __init__(self, sequence=None):
        if sequence is None:
            sequence = []
        self.sequence = sequence

    def file_to_list(self, filename='', condition='True', verbose=False):
        ''' Write all file lines to a new list.
        Args:
            filename (str): path to the source file
            condition (str): Default = True, which means it is disregarded.
                It must be a valid Python statement.
                When a line from the input file,
                falls under this condition,
                it gets added to the output list.
                Otherwise an empty string is added.
                The condition should be related to the line.
                (Eg "line.startswith(string)" or "len(line) < number")
        '''
        self.sequence = []
        if verbose is True:
            print('----')
            print('File to be converted to list:', filename, 'type:', type(filename))
            print('----')
        with open(file=filename, mode='rt', encoding='utf-8') as file:
            for line in file:
                if eval(condition) == True:
                    self.sequence.append(line)
                else:
                    self.sequence.append('')
                    pass
        # For empty files an empty list will be returned.
        if len(self.sequence) > 0:
            # If the last line ends with '\n',
            # a new empty string will be added to the list.
            if self.sequence[len(self.sequence) - 1].endswith('\n'):
                self.sequence.append('')
        # All trailing '\n' chars will be removed from all items.
        # An empty line file will be converted to an empty string.
        for index, item in enumerate(self.sequence):
            # Using items with indexes is a must to modify the list.
            # No comprehensions may be used!
            self.sequence[index] = self.sequence[index].strip('\n')
        if verbose is True:
            print('----')
            print('output sequence=', self.sequence)  # commented for tests
            print('----')
            pass
        return self.sequence

    def list_to_file(self, filename, verbose=False):
        # import time
        '''Creates a file from a list.
        If file exists, it will be overwritten.
        '''
        if verbose is True:
            print('----------------', )
            print('Starting function: "list_to_file"')
            print('The input list has', len(self.sequence), 'elements.')
            print('The path of the destination file is:', )
            print(filename)
            print('----')
        # os.system('touch ' + filename)
        with open(file=filename, mode='wt', encoding='utf-8') as file:
            # for line in sequence:
            for line in self.sequence[:-1]:
                file.write(''.join([line, '\n']))
            file.write(self.sequence[-1])
        if verbose is True:
            print('----')
            print('All lines written to file.')
            print('Ending the "list_to_file" function.')
            print('----------------')


    def regs_vs_list(self, regs, start_elem=0, first=True, verbose=False):
        ''' Check if the input list contains a consecutive sublist,
            that all elements match with all elements of list with regexes.
            In case, that len(regs) == 1 the function will just check,
            if one of the list's elements matches a single pattern.
            Only the first occurrence of the "regs" wil be checked.
            So make sure to select a unique sequence.

        Args:
            regs (list of regs of strs): List of patterns to match.
            sequence (list): List, that will be searched for matching patterns.
            start_elem (init): Index of the input list's element,
                where, the searching should start (by default: start_elem=0)

            first (bool):
                Controls if the index of the first or the last element
                of the input list will be returned.
                    True (default) - return the index of the first element.
                    False  - return the index of last element.
            verbose (bool): Decides if debug messages should be displayed.

        Returns:
            line_matching (int/None):
                Controlled by the "first" variable.
                If a match is found,
                returns the index of the first/last element of the input list.
                If a match is not found, it returns None.
                Example:
                input_list = ['a', 'b', 'c', 'd'] regs = ['b', 'c']
                returns: 1
        '''
        index_sequence = start_elem
        index_regs = 0
        carryon = True
        line_matching = None

        if verbose is True:
            print('----------------')
            print('Starting function: "regs_vs_list"')
            print('The input list contains:', len(self.sequence), 'elements')
            print('The reg list contains:', len(regs), 'elements')
            print('Counting starts from zero!')

        while (
                (
                    index_regs < len(regs)  # end of the reg list.
                    and
                    index_sequence < len(self.sequence)  # end of the input list.
                    and
                    len(regs) <= len(self.sequence)  # Otherwise there cannot be a match.
                    and
                    carryon is True
                )
                and  # Both lists (regs & input) must not be empty.
                (
                        len(regs) > 0
                        and
                        len(self.sequence) > 0
                )
        ):
            if verbose == True:
                print('----')
                xprint('Found regs[', index_regs, ']:')
                print(regs[index_regs])
                xprint('Found str(sequence[', index_sequence, ']):')
                print(str(self.sequence[index_sequence]))
            if (
                len(regs[index_regs]) != 0
                and
                re.findall(regs[index_regs], str(self.sequence[index_sequence])) != []
                or
                len(regs[index_regs]) == 0
                and
                self.sequence[index_sequence] in ('', '\n')
            ):
                if verbose == True:
                    print('The regex and line are matching.')

                # If the matching element is not the last.
                if index_regs < len(regs) - 1:
                    index_regs += 1
                    index_sequence += 1

                # If the last element of regs matches, it is a full match.
                elif index_regs == len(regs) - 1:
                    carryon = False
                    line_matching = index_sequence

                    # if first_or_last == 'first':
                    if first == True:
                        line_matching = line_matching - len(regs) + 1

                    # elif first_or_last == 'last':
                    if first == False:
                        # print('last=', line_matching)
                        return line_matching

            # No full match found.
            else:
                if verbose is True:
                    print('The line is not matching.')
                index_regs = 0
                index_sequence += 1

        if index_sequence > 0 and carryon is True:
            index_sequence -= 1  # If it was incremented above range

        if verbose is True:
            print('--------')
            if line_matching is None:
                print('The sub list was not found in the input list.')
            else:
                print('The sub list matches the input list.')
                print('The index of the line matching=', line_matching)
                print('The final checked line of regex:', )
                print(regs[index_regs])
                print('The final checked line of the input list:', )
                print(str(self.sequence[index_sequence]))
            print('Ending function: "regs_vs_list"')
            print('----------------')
        return line_matching

    def del_matching_items(self, pattern):
        '''
        All items in a list matching a specific pattern will be removed.
        '''
        temp_sequence = [item for item in self.sequence if re.findall(str(pattern), str(item)) == []]
        del self.sequence
        self.sequence = temp_sequence
        # print('now self.sequence=', self.sequence)
        return self.sequence



    def del_sublist(self, starting=None, ending=None, verbose=False):
        ''' It deletes elements from a list,
            from the "starting" element to the "ending" element.
        Args:
            sequence (list): the input list
            starting (int): Index of the first element to be deleted.
                if omitted, items will removed from the beginning.
            ending (int):   Index of the last element to be deleted.
                if omitted, items will removed till the ending.
            Both included in deletion!
        '''
        if starting is None:
            starting = 0
        if ending is None:
            ending = len(self.sequence) - 1
        if verbose is True:
            print('----------------')
            print('Starting function: "del_sublist"')
            print('----')
            print('Starting element has index:', starting)
            print('Ending element has index:', ending)

        if starting <= ending:
            for index in range(starting, ending + 1):
                # print('Deleting element:', self.sequence[index], sep='')
                if verbose is True:
                    print('Deleting element:', self.sequence[starting], sep='')
                del self.sequence[starting]
                index += 1
            # return 'Deletion succeeded!'
            return 'Deletion succeeded!'
        else:
            print('No elements were selected and deleted from the list.')
        if verbose is True:
            print('----')
            print('Ending function: "del_sublist"')
            print('----------------')

    def insert_sublist(self, starting, sublist, verbose=False):
    # def insert_sublist(sequence, starting, sublist, verbose=False):
        ''' It inserts a sublist into the original list.

        Args:
            sequence (list):  The original list.
            starting (int): Right before this index, the sublist will be inserted.
                That is, including the element with the "starting" index,
                all elements of the original list will be shifted down.
                If starting >= len(sequence), the sublist will be appended.
            sublist (list): A new list that is to be inserted into the input list.
        '''
        index = 0
        if starting < 0:
            starting = len(self.sequence)
        for elem in sublist:
            if verbose == True:
                print('element>>', elem, '<<will be inserted into line number:', starting + index)
            self.sequence.insert(starting + index, elem)
            index += 1

    def del_body(self, head=None, tail=None, verbose=False):
        ''' Deletes all list's elements after the head and before the tail.
            Say a list (eg. lines from a text file) contains several elements
            matching "head" sequences of regexes and matching "tail" sequences of regexes.
            All elements between these 2 sublists will be deleted.
            So right after the last head element, the first tail element will be put.
        Example:
            sequence = [
                            'itemA',  'itemB', 'itemC',
                            'delme1', 'delme2',
                            'itemX',  'itemY', 'itemZ'
                        ]
            head = ['itemB', 'itemC'] <- These can also be regexes
            tail = ['itemX', 'itemY'] <- same
            #The result will be:
            result = ['itemA', 'itemB', 'itemC', 'itemX', 'itemY', 'itemZ']

        Args:
            sequence (list): input list to insert the body into
            head (list): items, that must proceed the body to be inserted/deleted
            tail (list): items, that must follow the body to be inserted/deleted

        Returns:
            sequence - all operations will be done on the list in place.
        '''
        if head is None:
            head = []
        if tail is None:
            tail = []
        # if body is None:
        #     body = []
        if '0' == '1':
            pass
        # elif len(head) == 0 or len(body) == 0 or len(tail) == 0:
        elif len(head) == 0 or len(tail) == 0 or len(self.sequence) == 0:
            print('No head, no tail or no valid input. Nothing will be inserted or deleted!')
        else:
            end_of_head = self.regs_vs_list(
                regs=head,
                start_elem=0,
                first=False,
                verbose=verbose
            )
            start_of_tail = self.regs_vs_list(
                regs=tail,
                start_elem=0,
                first=True,
                verbose=verbose
            )
            if end_of_head >= start_of_tail:
                pass
                print('Head overlaps with tail. Wrong input data. Nothing will be deleted.')
            elif end_of_head + 1 == start_of_tail:
                pass
                # print('Tail begins right after head. It is OK but nothing to delete.')
            else:
                self.del_sublist(
                    # sequence=sequence,
                    starting=end_of_head+1,
                    ending=start_of_tail-1,
                    verbose=verbose
            )
        # return sequence

    # def insert_body(sequence, head=None, tail=None, body=None, verbose=False):
    def insert_body(self, head=None, tail=None, body=None, verbose=False):
        ''' Add a new section to the list after the head and before the tail.
        If a list from a text file contains several elements matching head regexes.
        First, it deletes the context in between. (See the "del_body" function.)
        An example, say we have these data:
            sequence = ['itemA',  'itemB', 'itemC',
                        'delme1', 'delme2',
                        'itemX',  'itemY', 'itemZ']
            head = ['itemB', 'itemC']
            body = ['bd1', 'bd2']
            tail = ['itemX', 'itemY']
        The result will be:
            result = ['itemA', 'itemB', 'itemC',
                      'bd1',   'bd2',
                      'itemX', 'itemY', 'itemZ']
        Args:
            sequence (list): Input list to insert the body into.
            head (list): Items, that must proceed the body to be inserted/deleted
            tail (list): Items, that must follow the body to be inserted/deleted
            body (list): Items to be deleted from between head and tail
        '''
        self.del_body(head=head, tail=tail, verbose=verbose)
        #regs_vs_list(self, regs, start_elem=0, first=True, verbose=False)
        end_of_head = self.regs_vs_list(
            regs=head,
            start_elem=0,
            first=False,
            verbose=verbose
        )
        self.insert_sublist(starting=end_of_head+1, sublist=body, verbose=False)


    def del_file_line(self, filename, line_to_remove):
        '''
        Removes all occurrences of a line from a (presumably config) file.
        Only the 1st occurrence is checked.
        :return: None
        '''
        sequence = self.file_to_list(filename=filename)
        # regs = []
        # regs.append(line_to_remove)
        # xprint('=', )
        # xprint('in seq=', seq)
        sequence = self.del_matching_items(pattern=line_to_remove)
        # xprint('in line_num=', line_num)
        # ListOps(seq).del_sublist(starting=line_num, ending=line_num, verbose=True)
        # print('now2 sequence=', sequence)
        ListOps(sequence).list_to_file(filename=filename)


def string_vs_regs(regs, string):
    '''
        Check if a string matches an element of the given regex list.
        (An extended form of re.findall.)
    ARGS:
        regs (list) : list of regexes
        string (str):
    RETURNS:
        matches (list): Items in the regs list matching
    '''
    matches = []
    for index, reg in enumerate(regs):
        if re.findall(reg, string) != []:
            matches.append(index)
    return matches



class AlterFileSection:
    '''
        Set of functions that allow to open a file (presumably with with config),
        then locate a section of the file that:
            - starts with specific sequence of lines (will be called "head")
            - ends with specific sequence of lines (will be called "tail")
            remove or alter lines between head and tail of a section.
        Finally write the list (with the modified section body),
        back to the original file (default) or to another.

    ARGS:
        section_head (list of strs)
        section_tail (list of strs)

    RETURN
        None - all operation are performed on files.

    '''
    def __init__(self, source_file, section_head, section_tail, dest_file=None):
        self.filename     = source_file
        self.section_head = section_head
        self.section_tail = section_tail
        self.dest_file    = dest_file
        if dest_file is None:
            self.dest_file = source_file
        else:
            self.source_file = source_file
        self.sequence = ListOps().file_to_list(filename=source_file)

    def del_body(self):
        ListOps(sequence=self.sequence).del_body(head=self.section_head, tail=self.section_tail)
        ListOps(sequence=self.sequence).list_to_file(filename=self.dest_file )

    def insert_body(self, section_body):
        ListOps(sequence=self.sequence).insert_body(
            head=self.section_head,
            tail=self.section_tail,
            body=section_body
        )
        ListOps(sequence=self.sequence).list_to_file(filename=self.dest_file)



def file_head_only(filename, lines, add_empty_line=False, reset_last_line=False):
    ''' Reads the file and returns only the head of it.
        How many first lines should be left in the new file
        depends from the "lines" parameter.

    Args:
        filename (str):
            Path with filename.
        lines (int): how many beginning lines should left in file.
        reset_last_line (bool) - If True, the last line will be an empty string
    Return: None - all operations are don in place on file.
    '''
    # Make list from a file.
    input_list = ListOps().file_to_list(filename)
    # input_list = file_to_list(filename)
    new_list = []
    # Rewrite the initial list to a new one, without trailing lines.
    for line in input_list[0:lines]:
        new_list.append(line)
    if add_empty_line is True:
        new_list.append('')
    if reset_last_line is True:
        new_list[-1] = ''
    # Write the scaled down list, back to the file.
    ListOps(sequence=new_list).list_to_file(filename)


def list_to_string(input):
    output = ''
    for elem in input:
        output = ''.join([output, elem])
    return output


def transform_string(
        input='',
        # transform=True,
        add_line_begin=False,
        add_line_end=False,
        escaped='$?()[].*'
    ):
    '''
    Args:
        input (str or list of str):
            It can be a string or list of strings to be processed.

        escaped (str):
            String containing special characters,
            that should be escaped. It is pre-assigned.

        add_line_begin (bool): regex '^' should be added at the beginning

        add_line_end (bool): regex '$' should be added at the ending

    Returns:
        The same type as input and analogous content.
        If transform is True,
            the chars, that are in the "escaped" argument
            will be be escaped.
            (Also regex chars for beginning ('^') and ending ('$')
            of the line may be added.
            This depends from: add_line_begin add_line_end)
    '''
    # if '0' == '1':
    #     pass
    #
    # else:
    def esc_str(input_str):
        '''
        Sub-function.
        Args:
            input_str (str):
        Return:
            escaped_str (str):
        '''
        escaped_str = ''
        for element in input_str:
            if element in escaped:
                element = '\\' + element
            escaped_str = ''.join([escaped_str, element])
        if add_line_begin is True:
            escaped_str = ''.join(['^', escaped_str])
        if add_line_end is True:
            escaped_str = ''.join([escaped_str, '$'])
        return escaped_str

    if isinstance(input, str):
        return esc_str(input)
    if isinstance(input, list):
        new_list = []
        for element in input:
            new_list.append(esc_str(element))
        return new_list


def os_command(command):
    '''Executes an OS command.

    Args:
        command (str): An OS command to execute.
    Returns:
        final_command_result (list): output of the command.
    '''
    split_command = command.split(' ')
    try:
        raw_command_result = subprocess.check_output(
            split_command,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        final_command_result = []
        for line in raw_command_result.split('\n'):
            final_command_result.append(line)
    except subprocess.CalledProcessError as err:
        final_command_result = None
        print('Command execution error:', err)
    return final_command_result


def combine_dicts(first_list, second_list, primary, excl_keys=None):
    ''' Updates dictionaries from the first list with dicts from the 2nd list.
    All dicts must have pri keys.
    If a dict from the 1st list has the same pri key as the dict from the 2nd list,
    all keys from the 2nd record will be written into the 1st records.
    If any of the dicts (1st or 2nd) not having pri - do not add it.

    TODO:
        Optimize the code, so it rather uses in place operations on iterables,
        instead of creating new ones.
        Consider using more comprehensions.
        Consider using generators.

    ARGS:
        primary (str): A key that must exist in a dict,
                       or it is disregarded.

        excl_keys: Which keys will be excluded from updating.
            Disregarded if primary keys do not mach.
            Type may vary:
                None:
                    All keys from the 1st dict will be updated (default).

                str: 'non_empty':
                    Only if a key in first dict == '', it will be updated.
                    Non empty keys will be left intact.

                a list:
                    List of keys, that will not be updated.

    '''
    if excl_keys is None:
        excl_keys = []
    dicts_in_first = [
        dicts_in_first for dicts_in_first in first_list
        if (primary in dicts_in_first.keys())]
    dicts_in_sec = [
        dicts_in_sec_orig for dicts_in_sec_orig in second_list
        if (primary in dicts_in_sec_orig.keys())]
    list_with_merged_dicts = []

    primary_vals_in_first = [dict_in_first[primary] for dict_in_first in dicts_in_first]
    for dict_in_first in dicts_in_first:
        for dict_in_sec in dicts_in_sec:
            if dict_in_sec[primary] in primary_vals_in_first:
                if dict_in_first[primary] == dict_in_sec[primary]:
                    if isinstance(excl_keys, list):
                        for key_in_sec in dict_in_sec.keys():
                            if key_in_sec not in excl_keys:
                                dict_in_first[key_in_sec] = dict_in_sec[key_in_sec]
                    if isinstance(excl_keys, str):
                        if excl_keys == 'non_empty':
                            for key_in_sec in dict_in_sec.keys():
                                if dict_in_first[key_in_sec] == '':
                                    dict_in_first[key_in_sec] = dict_in_sec[key_in_sec]
        list_with_merged_dicts.append(dict_in_first)

    # Now, dicts from the 2nd,
    # without matching primary/values will be added to final.
    for dict_in_sec in dicts_in_sec:
        if dict_in_sec[primary] not in primary_vals_in_first:
            list_with_merged_dicts.append(dict_in_sec)
    return list_with_merged_dicts


def findkey(item, dict_of_seqs):
    '''
        Finds an item in a dict of seqs.
        It can be useful when eg when we want the name of the OS command,
        that should be avail. trough several calling ways.
    ARGS:
        dict_of_seqs: dict of iterables
            Eg:
            {'shutdown' : ('shutdown', 'poweroff', 'halt'),
             'exit'     : ('exit',     'logoff',   'logout')}
    RETURNS:
        key (str): key, that we look for, 1st match is returned
            In the example above; if item=='logoff', 'exit' is returned.
    '''
    key = None
    for key, val in dict_of_seqs.items():
        for elem in val:
            if item == elem:
                return key


def append_if_not_in(seq, item):
    if item not in seq:
        seq.append(item)


def split_list(filename, sep='#'):
    ''' Function preparing input for 'multirun'.
    Return:
        final_list (list):
            Every valid input line with a command
            will be returned as a list.
    '''
    final_list = []
    temp_list = ListOps().file_to_list(filename=filename)
    for item in temp_list:
        # Skip empty and commented lines.
        if item != '' and item.startswith(sep) is False:
            split_item = item.split(sep)
            if len(split_item) == 2:
                final_list.append(''.join([split_item[0], split_item[1]]))
            final_list.append(split_item)
    return final_list


def main():
    print('This is the main library.')


if __name__ == '__main__':
    main()

