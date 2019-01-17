#!/usr/bin/env python
# -*- coding: utf-8 -*-
# HORTON: Helpful Open-source Research TOol for N-fermion systems.
# Copyright (C) 2011-2019 The HORTON Development Team
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


import importlib, os
from glob import glob
from cStringIO import StringIO

from common import write_if_changed


def discover():
    # find packages
    packages = {'horton': []}
    for fn in glob('../horton/*/__init__.py'):
        subpackage = fn.split('/')[2]
        if subpackage == 'test':
            continue
        packages['horton.%s' % subpackage] = []
    # find modules
    for package, modules in packages.iteritems():
        stub = package.replace('.', '/')
        for fn in sorted(glob('../%s/*.py' % stub) + glob('../%s/*.so' % stub)):
            module = fn.split('/')[-1][:-3]
            if module == '__init__':
                continue
            modules.append(module)
        for fn in sorted(glob('../%s/*.h' % stub)):
            module = fn.split('/')[-1]
            modules.append(module)

    return packages


def get_first_docline(module):
    m = importlib.import_module(module)
    if m.__doc__ is not None:
        lines = m.__doc__.split('\n')
        if len(lines) > 0:
            return lines[0]
    return 'FIXME! Write module docstring.'


def get_first_doxygenline(fn_h):
    with open('../%s' % fn_h) as f:
        for line in f:
            if line.startswith('// UPDATELIBDOCTITLE:'):
                return line[21:].strip()
        raise IOError('UPDATELIBDOCTITLE missing in %s' % fn_h)


def underline(line, char, f):
    print >> f, line
    print >> f, char*len(line)
    print >> f


def write_disclaimer(f):
    print >> f, '..'
    print >> f, '    This file is automatically generated. Do not make '
    print >> f, '    changes as these will be overwritten. Rather edit '
    print >> f, '    the documentation in the source code.'
    print >> f


def main():
    packages = discover()

    # Write new/updated rst files if needed
    fns_rst = []
    for package, modules in sorted(packages.iteritems()):
        # write the new file to a StringIO
        f1 = StringIO()
        write_disclaimer(f1)
        underline('``%s`` -- %s' % (package, get_first_docline(package)), '#', f1)
        print >> f1
        print >> f1, '.. automodule::', package
        print >> f1, '    :members:'
        print >> f1
        print >> f1, '.. toctree::'
        print >> f1, '    :maxdepth: 1'
        print >> f1, '    :numbered:'
        print >> f1

        for module in modules:
            f2 = StringIO()
            write_disclaimer(f2)
            if module.endswith('.h'):
                #full = package + '/' + module
                fn_h = package.replace('.', '/') + '/' + module
                underline('``%s`` -- %s' % (fn_h, get_first_doxygenline(fn_h)), '#', f2)
                print >> f2, '.. doxygenfile::', fn_h
                print >> f2, '    :project: horton'
                print >> f2
                print >> f2
            else:
                full = package + '.' + module
                underline('``%s`` -- %s' % (full, get_first_docline(full)), '#', f2)
                print >> f2, '.. automodule::', full
                print >> f2, '    :members:'
                print >> f2
                print >> f2
            # write if the contents have changed
            rst_name = 'mod_%s_%s' % (package.replace('.', '_'), module.replace('.', '_'))
            fn2_rst = 'lib/%s.rst' % rst_name
            fns_rst.append(fn2_rst)
            write_if_changed(fn2_rst, f2.getvalue())
            print >> f1, '    %s' % rst_name

        # write if the contents have changed
        fn1_rst = 'lib/pck_%s.rst' % package.replace('.', '_')
        fns_rst.append(fn1_rst)
        write_if_changed(fn1_rst, f1.getvalue())


    # Remove other rst files
    for fn_rst in glob('lib/*.rst'):
        if fn_rst not in fns_rst:
            print 'Removing %s' % fn_rst
            os.remove(fn_rst)


if __name__ == '__main__':
    main()
