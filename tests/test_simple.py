#!/usr/bin/env python
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

import sconstester
import os
import base64

# print base64.encodestring(open("filename").read())
# using stock android icon

icon_data = """\
iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAJ1UlEQVRoBe1ZW5AUVxn+untmd5iZ
ZZdd9sIu14VAAJclAbJi0DImIZbltRJCES2txLLUirHUlOVLHqgyLwpqqUmpD0nKkhijFJYxliUv
kAARIiCbDZcQlh0uy7IX9jb3S3f7/T3Ty8xOT89AyPLiX/XP6T7n9H/++/nPGeD/cHs1oFS4fKXz
KiRX8TSz3MxSjEm/SvQQq3KosbX7+fihgUHKwrhOTOUww9bu5+N1EAadQJj3EgObHqnrWLk++Lyh
ZKpgqqUEdqJx832KYaqmJ3X6aOTJg7vHe0goSkwTRagCKMVQNWcFfvjrjz5T16h+O2OkfQVfzdCL
R/UmxoeN3+x46vCzXFKEEIsUuFUpC4jbBFqWKZtbFgZ8plnwDYdmBhRF8V29GNnM1X5BFAuIAAXg
JIBYRSwQnAyHTX8sBdMQ96PoFCSNBKqVWYVqsEYlQBToZgaqIh7oZFyFtOgFHFIUCSkDGTMJr+Jz
pqeqmAwnRXtBYjyHEg9TICs5gVD3mrqhWV5ncEXKUK3W4s76z1EQeRdmTAut8OJ7IhXBRxofhV+b
B2Nq7Pq8dCaJBXX3os63GLqeseh95o7nkBEFWWtk6U49U1aLh2w82kmkgF8nC8gEEawqk1JUYURQ
JOha/BTm+u/ARHQAw9FTuLvt62gKrsJbF36JSGIAn13xHPzeOegbOYA7G76I+bX34Hj/S+ho2YJg
1Ty8dupb0DM6UpkU2oJdWNX8JTT6V8FIk75a7KY0AIQH4SXHE5tCKGUBqsJSuuU24jqGbqA1uJ7M
Po/2hvuR1lNY07INl8aOoL3+fjTVdGIk+j6iqRFqNIlF1PRYLATDNODz1KN/8hhaZ98Df1Uzgp4W
bFz4XfRPHIOmeOg+xtQ6slY+Zp3XYtriqZD9rKan98m7NTmZCiOWmEScaBoqUvok2us+heUNnyYT
rRgKn0HPlT1IG2mOK+i7dhDD4V4kkjEk0jH8u++3CMeG2XcOF0ePUMlVSKYmkM4kLDfsHX6Dz8mp
NWSdfJS1hYccCE9FQpRyIeubNS1bsXRRC7WfRtDXisn4AC5NvI32ufdhU/v3UVPdig0LHkfL7LWY
pdWiY94j9D2PtUpDYBm6Fn6DwiWxtm0b1rRuwTv9r2COfykiqSEGMbDt7lfgVX3YuOjJXFDbvGZb
ldtOb+wqX3YUDuS9FUnEMelrJc47duy/uzo7O1boetH+kUfiw3vUNA3d3T3vrVt311e4ygBxmFiQ
SkvFQI6rPA/M9cx8486DqwtZwcsUJ+3tAKOCtV0FEKbtjHA7BKhEca4CiO+LFgRvF5SLP1cBbKYr
0YQ9d6bbsgLcSguwOKN8LC24uVUC2fnuM12z0K3WvCgjkZlw52jaaDkeXAUQWrYFbkWb1uM4FPqJ
VVuVoyfaT6e5gQaDtTU1NXK4coSyLiQaKKcFR8rTOoUhyyVYRkvZbdMk9YKZ9rxIJIIrV65gYGBA
eBRFO2261pm3gED+i2jAzkT5/Tf6rLFc8PCEmtQjrH3iGEtcYCk9GwFvo8V+xpBSPwsqS1BhfHBw
ULQvnRmCtNkAkqc8KGuBvLk3/KiI4qj5ixOHcGF8H/rDbyOWHsbl04d56KlmSb0eS+bchyUsEK3g
ZlUqrjU6OgoRRICWUgWtCQ5WcBVAtC+mFqLuYLIoq4ZuZIQFWRYedRZ6Bv+IE4O/ZxWbrSgtgahI
3ZRyJoXQ+JsU7E0cUH+KDfO+iZVND/NLHclkEh6Ph0LyDFPoYUVsZMUs6r6xDg+1eXHiCKLpES7q
gYdHRNH6W5d2IpmZJDFZRrV4kRT68YXP4JOLtpM5xgL703oMBy/twHg8RPFUeL1epOi+Q9HTmEhe
dhXB1QKifbFCud1Q5zm52d+J90Zf58HlP6jWanD22t+gqX7xgamAzapFoebfsM7NHLLGFWg8K6h4
tWcrHl71MpavWIaX9j+BsZEI1ESDY/BmaWUvruxnx1aEEHQHGVfQ0bgVzcFO7Dn1GF1IbmKcvwuN
7bPGNLqZgG6mKawPn5j/NNfSMZnohzY3hGoekkLvXo4kEgmJYiFWRNDVAnauLi+AUDaR4UH9zNBf
oZk+ukWcIok78T5s2roqstdMGc4RIR5cspMzDBwMPYuYPo6tq3ejpXoD1IZuNLYxsHKnWycBXGOg
Mu2TLEFyezQ5iPOj+6wgXd24DU2B1QzspHjRNJRQ1zG/5l5sXvpz9I3vx95zTyOuRyUC0D34MtYx
qOW2gnFsa75I+7KuqwVkgkD5LCQCqAhNHECYtxNyTExloowd3kXlLStaloBdMffzWN24BSeuvoh/
nf0Bp0go8yoqN/fk1T/ziFqPet8y9GdOWCxYjDj8uFpA5ttWKNcaVHM4yfMrQ05RvTg78ndci53l
i7hQVuMas9Oa5q9i6ZyHcOjiTgbzAYt5ax3rSURhCtZ8ODm8m7cej5FcngamRLwuiasFhGk7Dq5/
4vwkqcIQd5VtQDGZV7IaNSVANT/uan4c1Z46vDO0CyeH/kKNS+7hHMcthjcgRhjx5DjjYwd+hUed
F2VvWQuU/HLagGgu4OUNBoUWncmvZJeaqjY8tPRn3JA92N+3fSrXmzndZudmVZv/LKx1D+4iDauM
sFcrSqmuFpAaRCwgligPJhbUfgyBqkZebg2jyd+BTYt+hD4G9T/OfMcSycM7VZGuInIUMJ4aw77Q
j12XdhVAvrR935VKbjCgNWFx7QO8XqxH2+wuLr4dY/HzqFIDnFGkvApISgS4X+m4CnAjMaCpvL5k
adDV9j3sOf1lHBt4gT6u8ebZX6EFi+VRxB2te9niMbvHVQB7UrlWrsqvhrtxefIw3Wijlf/HE+ez
pUS5jz/guKsAtu/brdNaKoPt+JXfoWfoT1YFempkN76w/AXejY6xLjrK4L35PCGxUsYA7lnIDmA7
DpxaWWAk/j4ZlVMfmTU1blB/wNrmJ5gh6QK5oL2pVlKsY5q9rspS6uGyWXBiOr/PYPG1ikVcllPZ
AhSWE3txbmwv7/5XcjdOcoy0PgjmWMlRyb7lfl0FkMtV+4xauoWVPtvrH2QMk0smG482C+dG/4nO
5q9B1WgZSUA3gVbesn4sbqeUmi9BqRiQ3JU4fvz4WG9v7yT3AxGUSYHqdQQ5pC/Gu/2v5Y3qiDS8
Th/uQi8tIsVepUBOpTiSP3WNRNQc43cJomM+daIqffU5XM92MbGOKDVwyesNjt1KkH8khelxYoh4
lDhKlOOdjE2BkwAyKNcBsvs0EWcTa4gsXJjYZwZE2wweyGFamB4iyv/EggWuVMqFbA2I1HLnIUSE
+VIxw6FbCpJ7RAj7r1WxRoHm7dVKWUAYFYZFQLuVuTMpgGhaKjkRxG6Lkur/AEiaJNAV7ZR0AAAA
AElFTkSuQmCC
"""

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

def create_variant_build(tester):
    cwd = os.path.normpath(os.getcwd())
    rootdir = os.path.normpath(os.path.join(cwd, '..'))
    tester.write_file('SConstruct','''
from SCons import Tool
Tool.DefaultToolpath.append('%s')
SConscript('main.scons', variant_dir='build', duplicate=0)\n''' % (rootdir))


def create_android_project(tester):
    srcdir = 'src/com/example/android'
    tester.subdir('res/drawable')
    tester.subdir('res/layout')
    tester.subdir('res/values')
    tester.subdir(srcdir)
    tester.write_file('res/drawable/icon.png', base64.decodestring(icon_data))
    tester.write_file('res/values/strings.xml',
                      '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">My Test App</string>
</resources>''')
    tester.write_file(srcdir + '/MyActivity.java',
                      '''
                      package com.example.android;
                      public class MyActivity {}
                      ''')
    tester.write_file('AndroidManifest.xml',
                      '''<?xml version="1.0" encoding="utf-8"?>
<manifest
    xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.android"
    android:installLocation="auto"
    android:versionCode="1"
    android:versionName="1.0" >
    <application
        android:icon="@drawable/icon"
        android:label="@string/app_name">
        <activity
            android:name=".MyActivity"
            android:label="@string/app_name">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>
    <uses-sdk android:targetSdkVersion="10" android:minSdkVersion="4" />
</manifest>
                      ''')
    return srcdir

def create_new_android_ndk_project(tester):
    create_android_project(tester)
    tester.subdir('jni')
    tester.write_file('jni/test.c',
                      '''#include <android/log.h>
                      int not_really_jni(void) { return 1; }''')

def create_android_ndk_project(tester):
    create_new_android_ndk_project(tester)
    tester.write_file('jni/Android.mk',
                      '''
LOCAL_PATH := $(call my-dir)
include $(CLEAR_VARS)
LOCAL_SRC_FILES := test.c
LOCAL_MODULE := test
include $(BUILD_SHARED_LIBRARY)''')

class AndroidSconsTest(sconstester.SConsTestCase):

    def testRuns(self):
        """
        Test the android tool doesn't cause a stacktrace
        """
        cwd = os.path.normpath(os.getcwd())
        rootdir = os.path.normpath(os.path.join(cwd, '..'))
        self.write_file('SConstruct','''
from SCons import Tool
var = Variables(None, ARGUMENTS)
var.AddVariables(('ANDROID_SDK', 'Android SDK path'))
Tool.DefaultToolpath.append('%s')
env = Environment(tools=['android'], variables=var)\n''' % (rootdir))
        out, err, rc = self.run_scons(['ANDROID_SDK='+getSDK()])
        self.assertEquals(0, rc)

    def testBasicBuildDir(self):
        """
        Test that a simple compile works, produces apk file
        """
        create_variant_build(self)
        create_android_project(self)

        self.write_file('main.scons','''
var = Variables(None, ARGUMENTS)
var.AddVariables(('ANDROID_SDK', 'Android SDK path'))
env = Environment(tools=['android'], variables=var)
env.AndroidApp('Test')
''')
        out, err, rc = self.run_scons(['ANDROID_SDK='+getSDK()])
        self.assertEquals(0, rc)
        self.assertTrue(self.exists('Test-debug.apk'))

    def testBasicNdkBuild(self):
        """
        Test that a compile with NDK works, produces apk file
        """
        create_variant_build(self)

        create_android_ndk_project(self)

        self.write_file('main.scons','''
var = Variables('../variables.cache', ARGUMENTS)
var.AddVariables(
    ('ANDROID_NDK', 'Android NDK path'),
    ('ANDROID_SDK', 'Android SDK path'))
env = Environment(tools=['android'], variables=var)
var.Save('variables.cache', env)
lib = env.NdkBuildLegacy('libs/armeabi/libtest.so', ['jni/test.c'])
apk = env.AndroidApp('Test', native_folder='#libs')
env.Help(var.GenerateHelpText(env))
''')
        out, err, rc = self.run_scons(['ANDROID_NDK='+getNDK(), 'ANDROID_SDK='+getSDK()])
        self.assertEquals(0, rc)
        self.assertTrue(self.exists('Test-debug.apk'))
        self.assertTrue(self.exists('libs/armeabi/libtest.so', variant=''))
        self.assertTrue(self.apk_contains('Test-debug.apk', 'lib/armeabi/libtest.so'))
        # check that a rebuild is a no-op
        out, err, rc = self.run_scons()
        self.assertEquals("scons: `.' is up to date.\n", out[4])

    def testGeneratedRes(self):
        create_variant_build(self)
        srcdir = create_android_project(self)
        self.write_file(srcdir + '/MyActivity.java',
                          '''
                          package com.example.android;
                          public class MyActivity {
                              public void onCreate() {
                                // make sure this gets used
                                System.out.println(R.raw.fake);
                              }
                          }
                          ''')
        self.subdir('sounds')
        self.write_file('sounds/fake.wav', '''BAM''')

        self.write_file('main.scons','''
var = Variables('../variables.cache', ARGUMENTS)
var.AddVariables(
    ('ANDROID_SDK', 'Android SDK path'))
env = Environment(tools=['android'], variables=var)
var.Save('variables.cache', env)
env.Command('res/raw/fake.ogg', 'sounds/fake.wav',
    [Mkdir('res/raw'), Copy('$TARGET', '$SOURCE')])
env.AndroidApp('Test', resources=['res','#res'])
''')
        out, err, rc = self.run_scons(['ANDROID_SDK='+getSDK()])
        self.assertEquals(0, rc)
        self.assertTrue(self.exists('Test-debug.apk'))
        self.assertTrue(self.apk_contains('Test-debug.apk', 'res/drawable/icon.png'))
        self.assertTrue(self.apk_contains('Test-debug.apk', 'res/raw/fake.ogg'))
        # check rebuild is a no-op
        out, err, rc = self.run_scons()
        self.assertEquals("scons: `.' is up to date.\n", out[4])
        # check that adding a resource is a rebuild
        self.write_file('sounds/fake.wav', '''BAR''')
        out, err, rc = self.run_scons()
        self.assertEquals('Copy("build/res/raw/fake.ogg", "sounds/fake.wav")\n', out[5])

    def testNewNdkBuild(self):
        """
        Test that a compile with the new NDK build works,
        and is comparable with the legacy Android.mk system
        """
        create_variant_build(self)
        create_android_ndk_project(self)

        self.write_file('main.scons','''
var = Variables('../variables.cache', ARGUMENTS)
var.AddVariables(
    ('ANDROID_NDK', 'Android NDK path'),
    ('ANDROID_SDK', 'Android SDK path'))
env = Environment(tools=['android'], variables=var)
var.Save('variables.cache', env)
lib = env.NdkBuildLegacy('libs/armeabi/libtest.so', ['jni/test.c'])
env.NdkBuild('new/libtest.so', ['jni/test.c'])
apk = env.AndroidApp('Test', native_folder='#libs')
env.Help(var.GenerateHelpText(env))
''')
        out, err, rc = self.run_scons(['ANDROID_NDK='+getNDK(), 'ANDROID_SDK='+getSDK()])
        self.assertEquals(0, rc)
        self.assertTrue(self.exists('Test-debug.apk'))
        self.assertTrue(self.exists('libs/armeabi/libtest.so', variant=''))
        self.assertTrue(self.exists('new/libtest.so'))
        oldsize = len(self.get_file('libs/armeabi/libtest.so', variant='').read())
        newsize = len(self.get_file('new/libtest.so').read())
        self.assertTrue(oldsize >= newsize, '%d >= %d failed' % (oldsize, newsize))

    def testCplusplusNdkBuild(self):
        """
        Test that a compile with the new NDK build works,
        and is comparable with the legacy Android.mk system
        """
        create_variant_build(self)
        create_new_android_ndk_project(self)
        self.write_file('jni/test.cpp',
                        '''#include <android/log.h>
                        class Foo {public: int i;};
                        int do_foo(const Foo &f) {return f.i;}''')

        self.write_file('main.scons','''
var = Variables('../variables.cache', ARGUMENTS)
var.AddVariables(
    ('ANDROID_NDK', 'Android NDK path'),
    ('ANDROID_SDK', 'Android SDK path'))
env = Environment(tools=['android'], variables=var)
lib = env.NdkBuild('libs/armeabi/libtest.so', ['jni/test.cpp'])
apk = env.AndroidApp('Test', native_folder='libs')
''')
        out, err, rc = self.run_scons(['ANDROID_NDK='+getNDK(), 'ANDROID_SDK='+getSDK()])
        self.assertEquals(0, rc)
        self.assertTrue(self.exists('Test-debug.apk'))
        self.assertTrue(self.exists('libs/armeabi/libtest.so'))
        # check the CXX command line has -fno-rtti, -mthumb at least
        compile_line = ''
        for line in out:
            if line.startswith('arm-linux-androideabi-g++'):
                compile_line = line.strip()
                break
        self.assertNotEquals('', compile_line)
        self.assertTrue('-fno-rtti' in compile_line, 'compile line "%s"' % compile_line)
        self.assertTrue('-fno-exceptions' in compile_line, 'compile line "%s"' % compile_line)
        self.assertTrue('-mthumb' in compile_line, 'compile line "%s"' % compile_line)

if __name__ == '__main__':
    sconstester.unittest.main()
