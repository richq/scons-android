#!/usr/bin/env python
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php
"""
SCons Tool to Build Android Applications
"""

import os
from SCons.Builder import Builder
from SCons.Defaults import DirScanner, Copy
from xml.dom import minidom

def get_android_package(fname):
    """ Get the value of the package from <manifest package='foo'> """
    parsed = minidom.parse(open(fname))
    manifest = parsed.getElementsByTagName('manifest')[0]
    return manifest.getAttribute('package')

def get_rfile(package):
    """ Retuns the path to the R.java resource file """
    return os.path.join(package.replace('.', '/'), 'R.java')

def target_from_properties(fname):
    """ Get a target value from a properties file """
    for line in open(fname).readlines():
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        key, val = line.split('=')
        if key == 'target':
            return val.split('-')[1]
    return None

def get_android_name(fname):
    """ Get the android activity name from <activity android:name='foo'> """
    parsed = minidom.parse(open(fname))
    activity = parsed.getElementsByTagName('activity')[0]
    return activity.getAttribute('android:name')

def get_android_target(fname):
    """
    Get the minimum SDK version and the target SDK version.
    fname is the AndroidManifest.xml file.
    Checks the manifest and also default.properties (if it exists)
    """
    properties = os.path.join(os.path.dirname(fname), 'default.properties')
    parsed = minidom.parse(open(fname))
    uses_sdk = parsed.getElementsByTagName('uses-sdk')[0]
    minSdk = uses_sdk.getAttribute('android:minSdkVersion')
    targetSdk = uses_sdk.getAttribute('android:targetSdkVersion')
    if os.path.exists(properties):
        targetSdk = target_from_properties(properties)
    return (minSdk, targetSdk or minSdk)

def add_gnu_tools(env):
    """ Add the NDK GNU compiler tools to the Environment """
    gnu_tools = ['gcc', 'g++', 'gnulink', 'ar', 'gas']
    for tool in gnu_tools:
        env.Tool(tool)
    toolchain = 'toolchains/arm-linux-androideabi-4.4.3/prebuilt/linux-x86/bin'
    arm_prefix = os.path.join('$ANDROID_NDK', toolchain,
                              'arm-linux-androideabi-')
    env['CC'] =  arm_prefix+'gcc'
    env['CXX'] = arm_prefix+'g++'
    env['AS'] = arm_prefix+'as'
    env['AR'] = arm_prefix+'ar'
    env['RANLIB'] = arm_prefix+'ranlib'
    env['OBJCOPY'] = arm_prefix+'objcopy'
    env['STRIP'] = arm_prefix+'strip'

def NdkBuild(env, library=None, inputs=None):
    """ Use the NDK to build a shared library from the given inputs. """
    # ensure ANDROID_NDK is set
    get_variable(env, 'ANDROID_NDK')
    target_platform = '$ANDROID_NDK/platforms/android-$ANDROID_MIN_TARGET'
    env['CPPPATH'] = ['$CPPPATH', target_platform + '/arch-arm/usr/include']
    if 'CPPDEFINES' not in env:
        env['CPPDEFINES'] = []
    env['CPPDEFINES'] += ['-DANDROID']

    android_cflags = '''-Wall -Wextra -fpic -mthumb-interwork
    -ffunction-sections -funwind-tables -fstack-protector -fno-short-enums
    -Wno-psabi -march=armv5te -mtune=xscale -msoft-float -mthumb -Os
    -fomit-frame-pointer -fno-strict-aliasing -finline-limit=64
    -Wa,--noexecstack'''.split()
    android_cxxflags = '''-fno-rtti -fno-exceptions'''.split()
    env['CFLAGS'] = ['$CFLAGS', android_cflags]
    env['CXXFLAGS'] = ['$CXXFLAGS', android_cflags, android_cxxflags]

    if 'LIBPATH' not in env:
        env['LIBPATH'] = []
    env['LIBPATH'] += [target_platform + '/arch-arm/usr/lib']
    shflags = '''-Wl,-soname,${TARGET.file}
        -shared
        --sysroot=%s/arch-arm
        -Wl,--no-undefined -Wl,-z,noexecstack''' % (target_platform)
    env['SHLINKFLAGS'] = shflags.split()

    lib = env.SharedLibrary('local/'+library, inputs, LIBS=['$LIBS', 'c'])
    env.Command(library, lib, [Copy('$TARGET', "$SOURCE"),
                               '$STRIP --strip-unneeded $TARGET'])
    return lib

def NdkBuildLegacy(env, library=None, inputs=None, app_root='#.',
            build_dir='.'):
    """ Use ndk-build to compile native code. """
    # ensure ANDROID_NDK is set
    get_variable(env, 'ANDROID_NDK')
    verbose = 0 if env.GetOption('silent') else 1
    jobs = env.GetOption('num_jobs')
    build_path = env.Dir(build_dir).path
    app_path = env.Dir(app_root).abspath
    cmd = ('$ANDROID_NDK/ndk-build V=%s -j %s SCONS_BUILD_ROOT=%s '
           'APP_PLATFORM=android-$ANDROID_MIN_TARGET -C %s') % (
               verbose, jobs, build_path, app_path)
    lib = env.Command(os.path.join(app_root, library), env.Flatten(inputs), cmd)
    env.Clean(lib, [os.path.join(app_root, x) for x in ('libs', 'obj')])
    return lib

# monkey patch emit_java_classes to do the Right Thing
# otherwise generated classes have no package name and get rebuilt always
import SCons.Tool.javac
from SCons.Tool.JavaCommon import parse_java_file

_DEFAULT_JAVA_EMITTER = SCons.Tool.javac.emit_java_classes

def emit_java_classes(target, source, env):
    """
    Set correct path for .class files from generated java source files
    """
    classdir = target[0]
    tlist, slist = _DEFAULT_JAVA_EMITTER(target, source, env)
    if env.has_key('APP_PACKAGE'):
        out = []
        for entry in slist:
            classname = env['APP_PACKAGE'] + entry.name.replace('.java', '')
            java_file = source[0].File(os.path.join(
                    env['APP_PACKAGE'].replace('.', '/'), entry.name))
            if os.path.exists(java_file.abspath):
                version = env.get('JAVAVERSION', '1.4')
                pkg_dir, classes = parse_java_file(
                                java_file.rfile().get_abspath(), version)
                for output in classes:
                    class_file = classdir.File(
                                os.path.join(pkg_dir, str(output) + '.class'))
                    class_file.attributes.java_classdir = classdir
                    class_file.attributes.java_sourcedir = entry.dir
                    class_file.attributes.java_classname = str(output)
                    out.append(class_file)
            else:
                class_file = classdir.File(os.path.join(
                        env['APP_PACKAGE'].replace('.', '/'),
                        entry.name.replace('.java', '.class')))
                class_file.attributes.java_classdir = classdir
                class_file.attributes.java_sourcedir = entry.dir
                class_file.attributes.java_classname = classname
                out.append(class_file)
        return out, slist
    else:
        return tlist, slist


SCons.Tool.javac.emit_java_classes = emit_java_classes


def AndroidApp(env, name,
               manifest='#/AndroidManifest.xml',
               source='src',
               resources='#/res',
               native_folder=None):
    """ Create an Android application from the given inputs. """
    android_manifest = env.File(manifest)

    if not env.has_key('ANDROID_TARGET'):
        min_target, target = get_android_target(android_manifest.abspath)
        env['ANDROID_MIN_TARGET'] = min_target
        env['ANDROID_TARGET'] = target
    env['ANDROID_JAR'] = os.path.join('$ANDROID_SDK',
                              'platforms/android-$ANDROID_TARGET/android.jar')
    if not env.has_key('APP_PACKAGE'):
        package = get_android_package(android_manifest.abspath)
    else:
        package = env['APP_PACKAGE']
    rfile = os.path.join('gen', get_rfile(package))
    gen = env.Dir('gen')

    # generate R.java
    resource_dirs = [env.Dir(r) for r in env.Flatten([resources])]
    abs_resources = [r.abspath for r in resource_dirs]
    res_string = ''
    aapt_args = 'package -f -m -M $MANIFEST -I $ANDROID_JAR -J $GEN'
    for tmp in range(0, len(abs_resources)):
        res_string += ' -S ${RES[%d]}' % tmp
    aapt_args += res_string
    generated_rfile = env.Aapt(rfile, resource_dirs,
             MANIFEST=android_manifest.path,
             GEN=gen, RES=abs_resources,
             AAPT_ARGS=aapt_args.split())
    env.Depends(generated_rfile, android_manifest)

    # compile java to classes
    bin_classes = name.replace('-','_')+'_bin/classes'
    classes = env.Java(target=bin_classes, source=[source],
                       JAVABOOTCLASSPATH='$ANDROID_JAR',
                       JAVASOURCEPATH=gen.path,
                       JAVACFLAGS='-g -encoding ascii'.split(),
                       JAVACLASSPATH=env.Dir(bin_classes).path)
    env.Depends(classes, rfile)

    # dex file from classes
    dex = env.Dex(name+'classes.dex', classes, DX_DIR=env.Dir(bin_classes).path)

    # resources
    aapt_args = 'package -f -m -M $MANIFEST -I $ANDROID_JAR -F $TARGET '
    aapt_args += res_string
    tmp_package = env.Aapt(name + '.ap_', resource_dirs,
                  MANIFEST=android_manifest.path,
                  RES=abs_resources,
                  AAPT_ARGS=aapt_args.split())
    env.Depends(tmp_package, android_manifest)

    # package java -classpath jarutils.jar:androidprefs.jar:apkbuilder.jar \
    #           com.android.apkbuilder.ApkBuilder
    # >> name-debug-unaligned.apk
    outname = name + '-debug-unaligned.apk'
    finalname = name + '-debug.apk'
    if env['ANDROID_KEY_STORE']:
        unsigned_flag = '-u'
        outname = name + '-unsigned.apk'
        finalname = name + '.apk'
    else:
        unsigned_flag = ''
    apk_args = "$UNSIGNED -f $SOURCE -z $AP"
    native_path = None
    if native_folder:
        apk_args += ' -nf $NATIVE_FOLDER'
        native_path = env.Dir(native_folder).path

    unaligned = env.ApkBuilder(outname, dex,
                   NATIVE_FOLDER=native_path,
                   UNSIGNED=unsigned_flag,
                   AP=tmp_package,
                   APK_ARGS=apk_args.split())
    if native_folder:
        sofiles = env.Glob(native_folder + '/armeabi/*.so')
        sofiles.extend(env.Glob(native_folder + '/armeabi-v7a/*.so'))
        env.Depends(unaligned, env.Flatten([dex, tmp_package, sofiles]))
    else:
        env.Depends(unaligned, [dex, tmp_package])
    env.Depends(unaligned, env.subst('$APK_BUILDER_JAR').split())
    if env['ANDROID_KEY_STORE'] and env['ANDROID_KEY_NAME']:
        unaligned = env.JarSigner(name + '-unaligned.apk', unaligned)

    # zipalign -f 4 unaligned aligned
    app = env.ZipAlign(finalname, unaligned)
    # installation marker
    adb = os.path.join('$ANDROID_SDK','platform-tools/adb')
    adb_install = env.Command(name + '-installed', app,
        [adb + ' install -r $SOURCE && date > $TARGET'])
    # do not run by default
    env.Ignore(adb_install[0].dir, adb_install)
    env.Alias('install', adb_install)

    if not env.has_key('APP_ACTIVITY'):
        activity = get_android_name(android_manifest.abspath)
    else:
        activity = env['APP_ACTIVITY']
    run = env.Command(name + '-run', app,
      [adb + ' shell am start -a android.intent.action.MAIN -n %s/%s%s'%(
          package, package, activity)])
    env.Depends(run, adb_install)
    env.Ignore(run[0].dir, run)
    env.Alias('run', run)

    return app

def get_variable(env, variable, do_exit=True):
    """
    Extract a variable from the environment if it exists.
    Optionally exits the run
    """
    if variable in os.environ:
        return os.environ[variable]
    elif variable in env:
        return env[variable]
    elif do_exit:
        print 'Please set %s. export %s=path' % (variable, variable)
        print "or run `scons %s=path'" % variable
        env.Exit(1)
    return None

def generate(env, **kw):
    """ SCons tool entry point """
    # ensure ANDROID_SDK is set
    get_variable(env, 'ANDROID_SDK')

    if 'ANDROID_KEY_STORE' not in env:
        env['ANDROID_KEY_STORE'] = ''

    if 'ANDROID_KEY_NAME' not in env:
        env['ANDROID_KEY_NAME'] = ''

    env.Tool('javac')
    env.Tool('jar')
    add_gnu_tools(env)
    env['AAPT'] = '$ANDROID_SDK/platform-tools/aapt'
    env['DX'] = '$ANDROID_SDK/platform-tools/dx'
    env['ZIPALIGN'] = '$ANDROID_SDK/tools/zipalign'
    env['JARSIGNER'] = 'jarsigner'

    bld = Builder(action='$AAPT $AAPT_ARGS', suffix='.java',
                  source_scanner=DirScanner)
    env.Append(BUILDERS = { 'Aapt': bld })

    bld = Builder(action='$DX --dex --output=$TARGET $DX_DIR', suffix='.dex')
    env.Append(BUILDERS = { 'Dex': bld })
    env['JAVA'] = 'java'

    cpfiles = os.pathsep.join(os.path.join('$ANDROID_SDK', 'tools/lib', jar)
                              for jar in 'androidprefs.jar sdklib.jar'.split())

    env['APK_BUILDER_CP'] = cpfiles
    base = os.path.join(os.path.dirname(__file__))
    j = env.Java(target='toolclasses',
             source=[base + '/sdklib/ApkBuilderMain.java'],
             JAVACLASSPATH='$APK_BUILDER_CP',
             JAVASOURCEPATH=env.Dir('#site_scons/site_tools').path)
    env['APK_BUILDER_JAR'] = j

    apk_builder = ('$JAVA -classpath $TOOL_CLASSES_DIR:$APK_BUILDER_CP '
                   'android.sdklib.ApkBuilderMain $TARGET $APK_ARGS')
    bld = Builder(action=apk_builder,
                  source_scanner=DirScanner,
                  TOOL_CLASSES_DIR=env.Dir('toolclasses'),
                  suffix='.apk')
    env.Append(BUILDERS = { 'ApkBuilder': bld })

    bld = Builder(action='$ZIPALIGN -f 4 $SOURCE $TARGET')
    env.Append(BUILDERS = { 'ZipAlign': bld })

    jarsigner_cmd = ('$JARSIGNER -keystore $ANDROID_KEY_STORE'
                     ' -signedjar $TARGET $SOURCE $ANDROID_KEY_NAME')
    env.Append(BUILDERS = { 'JarSigner': Builder(action=jarsigner_cmd) })

    env.AddMethod(AndroidApp)
    env.AddMethod(NdkBuild)
    env.AddMethod(NdkBuildLegacy)

def exists(env):
    """ NOOP method required by SCons """
    return 1
