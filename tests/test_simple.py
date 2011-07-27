#!/usr/bin/env python
import sconstester
import os

def getNDK():
    if 'ANDROID_NDK' in os.environ:
        return os.environ['ANDROID_NDK']
    else:
        return os.path.expanduser('~/tools/android-ndk-r6')

def getSDK():
    if 'ANDROID_SDK' in os.environ:
        return os.environ['ANDROID_SDK']
    else:
        return os.path.expanduser('~/tools/android-sdk-linux_86')

class AndroidSconsTest(sconstester.SConsTestCase):

    def testRuns(self):
        cwd = os.path.normpath(os.getcwd())
        rootdir = os.path.normpath(os.path.join(cwd, '..'))
        self.write_file('SConstruct','''
from SCons import Tool
var = Variables('variables.cache', ARGUMENTS)
var.AddVariables(
    ('ANDROID_NDK', 'Android NDK path'),
    ('ANDROID_SDK', 'Android SDK path'))
Tool.DefaultToolpath.append('%s')
env = Environment(tools=['android'], variables=var)\n''' % (rootdir))
        out, err, rc = self.run_scons(['ANDROID_NDK='+getNDK(), 'ANDROID_SDK='+getSDK()])
        self.assertEquals(0, rc)

if __name__ == '__main__':
    sconstester.unittest.main()
