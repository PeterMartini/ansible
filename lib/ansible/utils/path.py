# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
from errno import EEXIST
from ansible.errors import AnsibleError
from ansible.utils.unicode import to_bytes, to_str, to_unicode
from ansible.compat.six import PY2

__all__ = ['unfrackpath', 'makedirs_safe']

def unfrackpath(path):
    '''
    Returns a path that is free of symlinks, environment
    variables, relative path traversals and symbols (~)

    :arg path: A byte or text string representing a path to be canonicalized
    :raises UnicodeDecodeError: If the canonicalized version of the path
        contains non-utf8 byte sequences.
    :rtype: A text string (unicode on pyyhon2, str on python3).
    :returns: An absolute path with symlinks, environment variables, and tilde
        expanded.  Note that this does not check whether a path exists.

    example::
        '$HOME/../../var/mail' becomes '/var/spool/mail'
    '''
    canonical_path = os.path.normpath(os.path.realpath(os.path.expanduser(os.path.expandvars(to_bytes(path, errors='strict')))))
    if PY2:
        return to_unicode(canonical_path, errors='strict')
    return to_unicode(canonical_path, errors='surrogateescape')

def makedirs_safe(path, mode=None):
    '''Safe way to create dirs in muliprocess/thread environments.

    :arg path: A byte or text string representing a directory to be created
    :kwarg mode: If given, the mode to set the directory to
    :raises AnsibleError: If the directory cannot be created and does not already exists.
    :raises UnicodeDecodeError: if the path is not decodable in the utf-8 encoding.
    '''

    rpath = unfrackpath(path)
    b_rpath = to_bytes(rpath)
    if not os.path.exists(b_rpath):
        try:
            if mode:
                os.makedirs(b_rpath, mode)
            else:
                os.makedirs(b_rpath)
        except OSError as e:
            if e.errno != EEXIST:
                raise AnsibleError("Unable to create local directories(%s): %s" % (to_str(rpath), to_str(e)))
