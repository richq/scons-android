#!/usr/bin/env python
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
"""
Contains helper classes for tests
"""

from subprocess import Popen, PIPE
import errno
import os
import zipfile
import shutil
import tempfile
import unittest

class SConsResult:
    """
    Holds the results of a scons run
    """
    def __init__(self, out, err, return_code):
        self.out = out
        self.err = err
        self.return_code = return_code

class SConsTestCase(unittest.TestCase):
    """
    Helper class for running scons tests. Creates a temporary workspace for the
    test, then deletes it when the test ends.
    """
    def setUp(self):
        self.basedir = tempfile.mkdtemp()

    def tearDown(self):
        self.done()

    def write_file(self, filename, data):
        """
        Write a file inside the temp workspace
        """
        fullname = os.path.join(self.basedir, filename)
        tmpfile = open(fullname, 'w')
        tmpfile.write(data)
        tmpfile.close()

    def subdir(self, name):
        """
        Create a sub-directory in the test workspace
        """
        try:
            os.makedirs(os.path.join(self.basedir, name))
        except OSError, exc:
            if exc.errno != errno.EEXIST:
                raise

    def apk_contains(self, apk, filename, variant='build'):
        """
        Check if an APK file contains the given filename
        """
        apk_final = os.path.join(self.basedir, variant, apk)
        if zipfile.is_zipfile(apk_final):
            try:
                zip_file = zipfile.ZipFile(apk_final)
                files = zip_file.namelist()
                return filename in files
            finally:
                zip_file.close()
        return False

    def exists(self, name, variant='build'):
        """
        Check if a file exists in the test workspace
        """
        filename = os.path.join(self.basedir, variant, name)
        return os.path.exists(filename)

    def filesize(self, name, variant='build'):
        filename = os.path.join(self.basedir, variant, name)
        return os.stat(filename).st_size

    def get_file(self, name, variant='build'):
        """
        Open a file from within the test workspace
        """
        filename = os.path.join(self.basedir, variant, name)
        return open(filename)

    def run_scons(self, args=None):
        """
        Run a scons command on the test workspace using the given arguments.
        Captures stdout, stderr and the return code.
        """
        start = os.getcwd()
        try:
            os.chdir(self.basedir)
            cmd = ['scons']
            if args:
                cmd.extend(args)
            prog = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
            out = prog.stdout.readlines()
            err = prog.stderr.readlines()
            return_code = prog.wait()
            if return_code != 0:
                print ''.join(out), ''.join(err)
            return SConsResult(out, err, return_code)
        finally:
            os.chdir(start)

    def done(self):
        """
        Called at the end of a test, deletes the temporary workspace unless the
        environment variable SCONSTESTER_NOREMOVE is set (useful for debugging)
        """
        if 'SCONSTESTER_NOREMOVE' in os.environ:
            print self.basedir
        else:
            shutil.rmtree(self.basedir)
