#
# RTEMS Tools Project (http://www.rtems.org/)
# Copyright 2010-2012 Chris Johns (chrisj@rtems.org)
# All rights reserved.
#
# This file is part of the RTEMS Tools package in 'rtems-tools'.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

#
# Check the defaults for a specific host.
#

import os

import error
import execute
import log
import options
import path
import version

def _notice(opts, text):
    if not opts.quiet() and log.default and not log.default.has_stdout():
        print text
    log.output(text)
    log.flush()


def _check_none(_opts, macro, value, constraint):
    return True


def _check_triplet(_opts, macro, value, constraint):
    return True


def _check_dir(_opts, macro, value, constraint):
    if constraint != 'none' and not path.isdir(value):
        if constraint == 'required':
            _notice(_opts, 'error: dir: not found: (%s) %s' % (macro, value))
            return False
        if _opts.warn_all():
            _notice(_opts, 'warning: dir: not found: (%s) %s' % (macro, value))
    return True


def _check_exe(_opts, macro, value, constraint):

    if len(value) == 0 or constraint == 'none':
        return True

    orig_value = value

    if path.isabspath(value):
        if path.isfile(value):
            return True
        if os.name == 'nt':
            if path.isfile('%s.exe' % (value)):
                return True
        value = path.basename(value)
        absexe = True
    else:
        absexe = False

    paths = os.environ['PATH'].split(os.pathsep)

    if _check_paths(value, paths):
        if absexe:
            _notice(_opts,
                    'warning: exe: absolute exe found in path: (%s) %s' % (macro, orig_value))
        return True

    if constraint == 'optional':
        if _opts.trace():
            _notice(_opts, 'warning: exe: optional exe not found: (%s) %s' % (macro, orig_value))
        return True

    _notice(_opts, 'error: exe: not found: (%s) %s' % (macro, orig_value))
    return False


def _check_paths(name, paths):
    for p in paths:
        exe = path.join(p, name)
        if path.isfile(exe):
            return True
        if os.name == 'nt':
            if path.isfile('%s.exe' % (exe)):
                return True
    return False

def host_setup(opts):
    """ Basic sanity check. All executables and directories must exist."""

    checks = { 'none':    _check_none,
               'triplet': _check_triplet,
               'dir':     _check_dir,
               'exe':     _check_exe }

    sane = True

    for d in opts.defaults.keys():
        try:
            (test, constraint, value) = opts.defaults.get(d)
        except:
            raise error.general('invalid default: %s [%r]' % (d, opts.defaults.get(d)))
        if test != 'none':
            value = opts.defaults.expand(value)
            if test not in checks:
                raise error.general('invalid check test: %s [%r]' % (test, opts.defaults.get(d)))
            ok = checks[test](opts, d, value, constraint)
            if opts.trace():
                if ok:
                    tag = ' '
                else:
                    tag = '*'
                _notice(opts, '%c %15s: %r -> "%s"' % (tag, d, opts.defaults.get(d), value))
            if sane and not ok:
                sane = False

    return sane


def run():
    import sys
    try:
        _opts = options.load(args = sys.argv)
        _notice(_opts, 'RTEMS Source Builder - Check, v%s' % (version.str()))
        if host_setup(_opts):
            print 'Environment is ok'
        else:
            print 'Environment is not correctly set up'
    except error.general, gerr:
        print gerr
        sys.exit(1)
    except error.internal, ierr:
        print ierr
        sys.exit(1)
    except error.exit, eerr:
        pass
    except KeyboardInterrupt:
        _notice(opts, 'abort: user terminated')
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    run()
