#!/usr/bin/env python
# -*- coding: utf-8 -*-
# HORTON: Helpful Open-source Research TOol for N-fermion systems.
# Copyright (C) 2011-2022 The HORTON Development Team
#
# This file is part of HORTON.
#
# HORTON is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# HORTON is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --

import re
import sys


rules = [
    ('setup.py', ['^    version=\'(...+)\',$']),
    ('horton/__init__.py', ['^__version__ = \'(...+)\'$']),
    ('doc/releaseinfo.py', ['    version = \'(...+)\'$']),
    ('doc/user_download_and_install_linux.rst.template', [
        '^    https://github.com/theochem/horton/releases/download/(...+)/horton-(...+).tar.gz$',
        '^    curl -kfLO https://github.com/theochem/horton/releases/download/(...+)/horton-(...+).tar.gz$',
        '^    curl -kfLO https://github.com/theochem/horton/releases/download/(...+)/horton-(...+).tar.gz.md5$',
        '^    md5sum horton-(...+).tar.gz \| diff - horton-(...+).tar.gz.md5 -q \|\| rm -fv horton-(...+).tar.gz$',
        '^    tar -xvzf horton-(...+).tar.gz$',
        '^    cd horton-(...+)$']),
    ('doc/user_download_and_install_mac.rst.template', [
        '^    https://github.com/theochem/horton/releases/download/(...+)/horton-(...+).tar.gz$',
        '^    curl -kfLO https://github.com/theochem/horton/releases/download/(...+)/horton-(...+).tar.gz$',
        '^    curl -kfLO https://github.com/theochem/horton/releases/download/(...+)/horton-(...+).tar.gz.md5$',
        '^    md5 -r horton-(...+).tar.gz \| diff - horton-(...+).tar.gz.md5 -q \|\| rm -fv horton-(...+).tar.gz$',
        '^    tar -xvzf horton-(...+).tar.gz$',
        'cd horton-(...+)$']),
    ('doc/user_download_and_install_windows.rst.template', [
        '^    https://github.com/theochem/horton/releases/download/(...+)/horton-(...+).tar.gz$',
        '^    curl -kfLO https://github.com/theochem/horton/releases/download/(...+)/horton-(...+).tar.gz$',
        '^    curl -kfLO https://github.com/theochem/horton/releases/download/(...+)/horton-(...+).tar.gz.md5$',
        '^    md5sum horton-(...+).tar.gz \| diff - horton-(...+).tar.gz.md5 -q \|\| rm -fv horton-(...+).tar.gz$',
        '^    tar -xvzf horton-(...+).tar.gz$',
        '^    cd horton-(...+)$']),
]


if __name__ == '__main__':
    newversion = sys.argv[1]

    for fn, regexes in rules:
        with open(fn) as f:
            lines = f.readlines()
        for regex in regexes:
            r = re.compile(regex)
            for iline, line in enumerate(lines):
                m = r.match(line)
                if m is not None:
                    for igroup in range(m.lastindex, 0, -1):
                        line = line[:m.start(igroup)] + newversion + line[m.end(igroup):]
                    lines[iline] = line
        with open(fn, 'w') as f:
            f.writelines(lines)
