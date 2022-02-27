#!/usr/bin/python
import sys
sys.dont_write_bytecode = True  # No '*.pyc' precompiled files
def xprint(*content, sep=''): return (print(*content, sep=sep));  # print with sep='' by def.

# import os
# import subprocess
# import re
from varname import argname
# from varname import NonVariableArgumentError


def showvar(var, inc='', exc=''):
    ''' Function for troubleshooting purposes.
        Prints details of a variable.
        Uses the varname library.
    ARGS:
        variable: name of a variable

        inc/exc (str): include/exclude
            Several specific letters, telling which property
            you want to include or exclude. These are:
                v - value
                t - type
                l - len (lowercase of "L")
                e - elements
        items (bool): enumerate items (where possible)?
    '''
    def show(prop):
        if (
                (inc == '' or prop in inc) and (prop not in exc)
        ):
            return True
        else:
            return False
    # varlen = None
    try:
        xprint('==== Evaluating variable:', argname(var))

        if show('v') is True:
            xprint('Variable value:', repr(var))

        if show('t') is True:
            xprint('Variable type :', type(var))

        if show('l') is True or show('e') is True:
            try:
                varlen = len(var)
            except TypeError:
                varlen = None

            if show('l') is True:
                if varlen is None:
                    ending = 'This type has no "len"'
                else:
                    ending = len(var)
                xprint('Variable len  :', ending)

            if show('e') is True:
                if varlen is None:
                    xprint('Type not iterable, cannot be enumerated.')
                else:
                    print('-' * 2)
                    if isinstance(var, str) is True:
                        for key, val in var.items():
                            xprint('key=', repr(key), '\t\tval=', repr(val))
                    else:
                        for index, val in enumerate(var):
                            xprint('index=', index, '\tval=', repr(val))
    # except:
        # print('Error!')
    except NonVariableArgumentError as error:
        print('This variable cannot be evaluated. Error:', error)
    print('=' * 10)


def main():
    print('This is a local library.')


if __name__ == '__main__':
    main()
