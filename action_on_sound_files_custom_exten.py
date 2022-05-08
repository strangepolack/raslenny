#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
import os
import re
import platform
import natsort
from lib_main import ListOps
from lib_main import string_vs_regs
from lib_main import append_if_not_in
from lib_parameters import sounds_main_dir
from lib_parameters import path_to_ffmpeg
from lib_parameters import path_to_ffmpeg_on_pc
from lib_parameters import local_audio_folder

if 'Linux' not in platform.system():
    sounds_main_dir = local_audio_folder

jump_line_start = '^jump='
jump_line_end = '[1-9][0-9]?$'  # So 'jump' value must be 1-99

# Common audio file formats
common_audio_file_exten = '(m4a|mp3|wav)'

# Format/type of file, that can be played
output_end = 'ulaw'

list_extensions = []
list_audiosubdirs = []

def bckgrds_file_patts(ext_name, re_end):
    '''
        RETURNS:
        patterns (list):
            Can be used for:
            - patterns for filenames
            - calculating order for sorting another list
    '''
    patterns = []
    patterns.append('^' + 'Background' + ext_name        + '\.' + re_end + '$')
    patterns.append('^' + 'Background' + ext_name        + '\.' + re_end + '$')
    patterns.append('^' + 'background' + ext_name        + '\.' + re_end + '$')
    patterns.append('^' + 'Background' + ext_name + '.*' + '\.' + re_end + '$')
    patterns.append('^' + 'background' + ext_name + '.*' + '\.' + re_end + '$')
    patterns.append('^' + 'Background' +            '.*' + '\.' + re_end + '$')
    patterns.append('^' + 'background' +            '.*' + '\.' + re_end + '$')
    patterns.append('^' + 'Background' +                   '\.' + re_end + '$')
    patterns.append('^' + 'background' +                   '\.' + re_end + '$')
    return patterns

def settings_file_patterns(ext_name):
    '''
    RETURNS:
        patterns (list):
            Can be used for:
            - patterns for filenames
            - calculating order for sorting another list
    '''
    patterns = []
    patterns.append('^' + 'Settings' + ext_name         + '\.txt' + '$')
    patterns.append('^' + 'Settings' + ext_name.lower() + '\.txt' + '$')
    patterns.append('^' + 'settings' + ext_name         + '\.txt' + '$')
    patterns.append('^' + 'settings' + ext_name.lower() + '\.txt' + '$')

    patterns.append('^' + 'Settings' + ext_name         + '.*' + '\.txt' + '$')
    patterns.append('^' + 'Settings' + ext_name.lower() + '.*' + '\.txt' + '$')
    patterns.append('^' + 'Settings' + ext_name         + '.*' + '\.txt' + '$')
    patterns.append('^' + 'Settings' + ext_name.lower() + '.*' + '\.txt' + '$')

    patterns.append('^' + 'Settings'             + '.*' + '\.txt' + '$')
    patterns.append('^' + 'settings'             + '.*' + '\.txt' + '$')
    patterns.append('^' + 'Settings'                    + '\.txt' + '$')
    patterns.append('^' + 'settings'                    + '\.txt' + '$')
    return patterns


class AudioSubDir:
    '''
        This represents a sub dir of the dir with custom extension.
        It may/does contain:
        - audio files in common format
        - ulaw files (special audio files used by asterisk)
        - text files containing settings
        These are corresponding to a specific custom extension.
        Common audio files in such a folder will be converted
        to files type 'ulaw' that are playable by asterisk.
        These will be played when a custom extension is called.
        Also objects/values calculated for this class will be put
        into Aterisk conf files and dbs.
    ARGS:
        settings_files_with_jumps (list of strs): Text files with settings.

        input_audios (list of strs): Common audio files,
            that will be converted to dialog 'ulaw' files.

        output_audios (list of strs): Files of type 'ulaw'
            that are already present in the audio subdir.

        input_backgrounds (list of strs): Common audio files,
            that will be converted to background 'ulaw' files.

        output_backgrounds (list of strs): # Files of type 'ulaw',
            where one of them will be the background sound.

        jumps (list): jumps in files

        jump (int): Number of audio file,
            that should be played again after playing the last audio.
    '''
    def __init__(
            self,
            dir_name,
            common_audio_dialog_files=None,
            common_audio_background_files=None,
            ulaw_audio_dialog_files=None,
            ulaw_audio_background_files=None,
            settings_files=None,
            settings_with_jumps=None,
            final_ulaw_background_file=None,
            final_jump_file=None,
            final_jump_value=None,
            # valid=True
    ):
        if re.findall(' ', dir_name):
            new_dirname = dir_name.replace(' ', '_')
            src = os.path.join(sounds_main_dir, dir_name + os.sep)
            dst = os.path.join(sounds_main_dir, dir_name.replace(' ', '_') + os.sep)
            print('The dir name:', src, 'will be renamed to:', dst, '\n'
                'No spaces allowed in the dir name.')
            os.rename(src=src, dst=dst)
            dir_name = new_dirname

        self.dir_name = dir_name
        self.common_audio_dialog_files = common_audio_dialog_files
        self.common_audio_background_files = common_audio_background_files
        self.ulaw_audio_dialog_files = ulaw_audio_dialog_files
        self.ulaw_audio_background_files = ulaw_audio_background_files
        self.settings_files = settings_files
        self.settings_with_jumps = settings_with_jumps
        self.final_ulaw_background_file = final_ulaw_background_file
        self.final_jump_file = final_jump_file
        self.final_jump_value = final_jump_value
        self.valid = True

        if self.common_audio_dialog_files is None:
            self.common_audio_dialog_files = []
        if self.common_audio_background_files is None:
            self.common_audio_background_files = []
        if self.ulaw_audio_dialog_files is None:
            self.ulaw_audio_dialog_files = []
        if self.ulaw_audio_background_files is None:
            self.ulaw_audio_background_files = []
        if self.settings_files is None:
            self.settings_files = []
        if self.settings_with_jumps is None:
            self.settings_with_jumps = []
        self.current_dir = os.path.join(sounds_main_dir, self.dir_name)

    def _find_jump_in_file(self, filepath):
        '''
            Auxiliary function.
            The purpose is to find the 'jump' value in the settings file.

        RETURN:
            jump: (integer/None):
                tells which recording the program jumps to,
                after playing the last one.
                If a correct value cannot be retrieved, None is returned
        '''
        # jump = None
        obj_setts = ListOps()
        list_setts = obj_setts.file_to_list(filepath)

        # Number of line where a valid "jump=n" phrase is found.
        no_of_line = ListOps(list_setts).regs_vs_list(
            regs=[jump_line_start + jump_line_end]
        )
        if no_of_line == None:
            return None
        else:
            jump = int(re.sub(jump_line_start, '', list_setts[no_of_line]))
            return jump

    def _custom_sort_aux_files(self, input_list, ext_name, what_files):
        ''' Auxiliary function.
            It sorts the list of files, arbitrary.
            Only files with: 'settings', 'common_audio_bckgrs', 'ulaw_audio_bckgrs'
            For list with other files, a normal natsort is utilized.
        ARGS:
            what_files (str): List with which filenames should be sorted.
            The options are:
                'settings'
                'common_audio_bckgrs'
                'ulaw_audio_bckgrs'
        '''
        if what_files == 'settings':
            patterns = settings_file_patterns(ext_name)

        elif what_files == 'common_audio_bckgrs':
            patterns = bckgrds_file_patts(ext_name, re_end=common_audio_file_exten)

        elif what_files == 'ulaw_audio_bckgrs':
            patterns = bckgrds_file_patts(ext_name, re_end=output_end)

        templist = []
        for file in input_list:
            for reg_index, regex in enumerate(patterns):
                if re.findall(patterns[reg_index], file):
                    templist.append((file, reg_index))
                    break
        templist.sort(key=lambda elem: elem[1])
        output_list = [item[0] for item in templist]
        return output_list

    def _check_order(self, ext_name, list_of_files):
        ''' Checks if the file names are consecutive.
        '''
        result = True
        for index, filename in enumerate(list_of_files):
            if os.path.splitext(filename)[0] != ext_name + str(index+1):
                result = False
                break
        return result


    def final_check(self):
        ''' Function checks if all files and settings are in place
            and the audio subfolder may serve as a custom extension.

        RETURNS:
            self.valid (bool):
        '''
        self.valid = True

        if len(self.ulaw_audio_dialog_files) == 0:
            self.valid = False

        if self._check_order(
            ext_name=self.dir_name,
            list_of_files=self.ulaw_audio_dialog_files
            ) is False:
            self.valid = False

        if self.final_ulaw_background_file is None:
            self.valid = False

        return self.valid


    def find_final_jump(self):
        '''
        From the list of all settings files, one will be selected and the jump val taken from it.
        If no valid settings file exists or the jump value is incorrect,
        a default value is returned.
        '''
        jump = None
        how_many_dialogs = len(self.ulaw_audio_dialog_files)


        def _defult_jump_val():
            ''' If no valid jump value can de calculated from settings files,
                or no valid settings file exist,
                calculate a default jump according to the number of dialogs.
            '''
            jump = None
            if how_many_dialogs == 0:
                jump = None
            elif how_many_dialogs == 1:
                jump = 1
            elif how_many_dialogs == 2:
                jump = 1
            elif how_many_dialogs == 3:
                jump = 2
            else:
                jump = 3
            return jump

        if how_many_dialogs in (0, 1) or len(self.settings_with_jumps) == 0:
            jump = _defult_jump_val()

        else:
            for item in self.settings_with_jumps:
                if item['jump'] is not None:
                    if item['jump'] <= how_many_dialogs:
                        jump = item['jump']
                        break
                jump = _defult_jump_val()

        return jump


    def evaluate(self):
        ''' Function operates on real dirs and files on disc,
            therefore no arguments are taken or returned.
        ARGS: None
        RETURNS: None
        '''
        for sub_obj in os.scandir(self.current_dir):
                if sub_obj.is_file():

                    # obj is a txt file with settings
                    # which means: its name is suitable for a settings file
                    if (string_vs_regs(
                            regs=settings_file_patterns(
                                self.dir_name),
                                string=str(sub_obj.name))
                        ) != []:
                        append_if_not_in(
                            seq=self.settings_files,
                            item=sub_obj.name
                            )
                    elif re.findall(common_audio_file_exten, sub_obj.name):
                        regs = bckgrds_file_patts(
                            ext_name=self.dir_name,
                            re_end=common_audio_file_exten
                            )

                        if (
                            string_vs_regs(
                            regs=regs, string=str(sub_obj.name)) != []
                        ):
                            append_if_not_in(
                                seq=self.common_audio_background_files,
                                item=sub_obj.name)

                        else:
                            append_if_not_in(
                                seq=self.common_audio_dialog_files,
                                item=sub_obj.name
                                )

                    elif sub_obj.name.endswith('.ulaw'):
                        if os.path.isfile(
                            os.path.join(
                                sounds_main_dir,
                                self.dir_name,
                                sub_obj.name.replace(' ', '_')
                                )
                            ) is False and 1==1:
                            os.rename(
                                src=os.path.join(self.current_dir,
                                    sub_obj.name),
                                dst=os.path.join(self.current_dir,
                                    sub_obj.name.replace(' ', '_'))
                                )

                        if string_vs_regs(
                            regs=bckgrds_file_patts(
                                ext_name=str(self.dir_name),
                                re_end=output_end),
                                string=str(sub_obj.name)
                                ) != []:
                            append_if_not_in(
                                seq=self.ulaw_audio_background_files,
                                item=sub_obj.name
                                )

                        else:
                            append_if_not_in(
                                seq=self.ulaw_audio_dialog_files,
                                item=sub_obj.name
                            )
                            append_if_not_in(
                                seq=self.ulaw_audio_dialog_files,
                                item=sub_obj.name
                            )

        # Sorting section
        templist = natsort.natsorted(
            self.common_audio_dialog_files, key=lambda elem: os.path.splitext(elem)[0]
            )
        self.common_audio_dialog_files = templist

        templist = natsort.natsorted(
            self.ulaw_audio_dialog_files, key=lambda elem: os.path.splitext(elem)[0]
            )
        self.ulaw_audio_dialog_files = templist

        # for common audio background files
        templist = self._custom_sort_aux_files(
            input_list=self.common_audio_background_files,
            ext_name=self.dir_name,
            what_files='common_audio_bckgrs')
        self.common_audio_background_files = templist

        # for ulaw audio background files
        templist = self._custom_sort_aux_files(
            input_list=self.ulaw_audio_background_files,
            ext_name=self.dir_name,
            what_files='ulaw_audio_bckgrs')
        self.ulaw_audio_background_files = templist

        # for settings files
        templist = self._custom_sort_aux_files(
            input_list=self.settings_files,
            ext_name=self.dir_name,
            what_files='settings'
        )
        self.settings_files = templist
        del templist

        # Create the dictionary with settings files and their corresponding jump values
        for item in self.settings_files:
            append_if_not_in(
                seq=self.settings_with_jumps,
                item={
                    'file': item,
                    'jump': self._find_jump_in_file(
                            filepath=self.current_dir + os.sep + item
                            )
                    }
            )
        self.final_jump_value = self.find_final_jump()
        if len(self.ulaw_audio_background_files) > 0:
            self.final_ulaw_background_file = self.ulaw_audio_background_files[0].rstrip(
                '.ulaw')
        self.final_check()


    def createulaw(self, common_audio_file, ulaw_audio_file):
        ''' Makes a ulaw file from a common format audio file.
        '''
        print("Converting file:", common_audio_file, "to ulaw format:", ulaw_audio_file)
        os.system(path_to_ffmpeg + ' -y -i ' + common_audio_file +
            ' -af "highpass=f=300, lowpass=f=3400" -ar 8000 -ac 1 -ab 64k -f mulaw '
            + ulaw_audio_file)


    def del_dialog_ulaws(self):
        self.evaluate()
        for filename in self.ulaw_audio_dialog_files:
            current_file = os.path.join(self.current_dir, filename)
            print('A ulaw dialog file:', str(filename), 'is being deleted!')
            if os.path.isfile(current_file):
                os.remove(current_file)
        self.evaluate()


    def del_background_ulaws(self):
        self.evaluate()
        for filename in self.ulaw_audio_background_files:
            current_file = os.path.join(self.current_dir, filename)
            print('A ulaw background file:', str(filename), 'is being deleted!')
            if os.path.isfile(current_file):
                os.remove(current_file)
        self.evaluate()


    def makeulaws(self):
        '''
        Function makes ulaw files from common audio files.
        (Both: dialog and background)
        Before creating new ulaw files, existing ulaw dialogs may be deleted.
        (Existing ulaw background files will be always left intact.
        That will happen, only for dirs, where there are common audio dialog files.
        Otherwise, no action will be performed.
        So if there are only ulaws (and maybe setting-txt),
        these files are assumed to remain and serve as final dialog files.
        This is for a case when you put a folder,
        containing only already prepared ulaws.
        (eg. Original Lenny files).
        It would make no sense to delete ulaws,
        in order to start converting non existing common audios.
        '''
        self.evaluate()
        if len(self.common_audio_dialog_files) > 0:
            self.del_dialog_ulaws()
            self.ulaw_audio_dialog_files = []
            for index, filename in enumerate(self.common_audio_dialog_files):
                newfilename = self.dir_name + str(index + 1) + '.ulaw'
                # '"' is to embrace filenames with spaces
                self.createulaw(
                    common_audio_file='"' + os.path.join(self.current_dir, filename) + '"',
                    ulaw_audio_file=os.path.join(self.current_dir, newfilename))
                append_if_not_in(
                    seq=self.ulaw_audio_dialog_files,
                    item=newfilename
                    )
        else:
            print('No common format audio files present in the dir:', self.dir_name,
                  'no dialog ulaws will be deleted or created.')

        for filename in self.common_audio_background_files:
            # Replace spaces in the output filenames with "_"s.
            newfilename = os.path.splitext(
                filename.replace(' ', '_'))[0] + '.ulaw'
            if os.path.isfile(newfilename) == False:
                self.createulaw(
                    # '"' is to embrace filenames with spaces
                    common_audio_file='"' + os.path.join(self.current_dir, filename) + '"',
                    ulaw_audio_file=os.path.join(self.current_dir, newfilename)
                )
                append_if_not_in(
                    seq=self.ulaw_audio_background_files,
                    item=newfilename
                )
        self.evaluate()


class AudioMainDir:
    '''
        Class to represent the directory,
        with subdirs where the final custom audios will be made
        out of common audio files and put into.
        These are audio files used during dialogs.
        So, finally these folders will contain final audio files
        and their corresponding setting files.
        Eg.: the dir 'Lenny' will contain files like:
            'Lenny1.ulaw', 'Lenny2.ulaw', etc.
             and one file named like:
            'Settings_Lenny.txt' or 'Settings.txt' or "settings.txt'
    '''
    def __init__(self):
        self.sounds_main_dir = sounds_main_dir
        self.list_audiosubdirs = self.enumerate_subdirs()
        self.list_final_extensions = []

    def enumerate_subdirs(self):
        for obj in os.scandir(sounds_main_dir):
            if obj.is_dir():
                klass = AudioSubDir(obj.name)
                klass.evaluate()
                if str(klass.dir_name) not in [item.dir_name for item in list_audiosubdirs]:
                    list_audiosubdirs.append(klass)
        return list_audiosubdirs


    def del_ulaws(self):
        for item in list_audiosubdirs:
            item.del_dialog_ulaws()
            item.del_background_ulaws()


    def make_ulaws(self):
        for item in list_audiosubdirs:
            item.makeulaws()


    def final_extensions(self):
        '''
            Function, operates on elements of the list from evaluation,
            not on real dirs and files.
            It calculates/validates the settings retrieved
            from each dir with custom audio files.
            Also it validates, that the 'ulaw' files are in order.
            Eg. if the checked folder contains only 4 'ulaw' files named:
            'Lenny1.ulaw', 'Lenny2.ulaw', 'Lenny4.ulaw'
            They should not be valid as 'Lenny3.ulaw' is missing.

        RETURNS:
            final_settings (list): List of classes type 'FinalExtension'.
        '''
        # list_audiosubdirs = self.enumerate_subdirs()
        # Add a valid extension to the final class
        for item in self.list_audiosubdirs:
            if item.valid is True:
                self.list_final_extensions.append(
                    FinalExtension(
                        ext_name=item.dir_name,
                        how_many_dialogs=len(item.ulaw_audio_dialog_files),
                        jump=item.final_jump_value,
                        background=item.final_ulaw_background_file
                    ))
        return self.list_final_extensions


class FinalExtension:
    ''' This class will be passed to the script,
        that writes settings to asterisk config files and dbs.
    PROPERTIES:
        ext_name (str):
        how_many_dialogs (int): Should be less than 99
        jump (init): To which recording, the call jumps after the last one is played.
        background (str):
            Name (without extension and path) of the background file.
            As of now it is suggested to use a silence-like background recording.

    Example: below are listed properties of 2 instances:
            ext_name = 'Lenny'
            how_many_dialogs = 16
            jump = 3
            backgound = 'backgroundnoise'

            ext_name = 'Lenka'
            how_many_dialogs = 12
            jump = 4
            backgound = 'backgrounLenka'
    '''
    def __init__(
        self,
        ext_name,
        how_many_dialogs,
        jump,
        background
            ):

        self.ext_name = ext_name
        self.how_many_dialogs = how_many_dialogs
        self.jump = jump
        self.background = background


def main():
    print('Action on custom exten. conf. files.')


if __name__ == '__main__':
    main()
