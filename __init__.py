#!/usr/bin/env python
import os
from SCons.Builder import Builder
from SCons.Defaults import DirScanner
from xml.dom import minidom

def GetAndroidPackage(env, fname):
    p = minidom.parse(open(fname))
    m = p.getElementsByTagName('manifest')[0]
    return m.getAttribute('package')

def get_rfile(package):
    return os.path.join(package.replace('.', '/'), 'R.java')

def TargetFromProperties(fname):
    for line in open(fname).readlines():
        line = line.strip()
        if line.startswith('#'):
            continue
        key, val = line.split('=')
        if key == 'target':
            return val.split('-')[1]
    return None

def GetAndroidName(env, fname):
    p = minidom.parse(open(fname))
    m = p.getElementsByTagName('activity')[0]
    return m.getAttribute('android:name')

def GetAndroidTarget(env, fname):
    dp = os.path.join(os.path.dirname(fname), 'default.properties')
    if os.path.exists(dp):
        return TargetFromProperties(dp)
    p = minidom.parse(open(fname))
    m = p.getElementsByTagName('uses-sdk')[0]
    minSdk = m.getAttribute('android:minSdkVersion')
    targetSdk = m.getAttribute('android:targetSdkVersion')
    return targetSdk or minSdk

def NdkBuild(env, library=None, app_root='.',
             manifest='#/AndroidManifest.xml',
            build_dir='.', inputs=[]):
    android_manifest = env.File(manifest)
    verbose = 0 if env.GetOption('silent') else 1
    lib = env.Command(os.path.join(app_root, library), env.Flatten(inputs),
                  '$ANDROID_NDK/ndk-build V=%s -j %s SCONS_BUILD_ROOT=%s APP_PLATFORM=android-$ANDROID_TARGET -C %s' % (
                      verbose,
                      env.GetOption('num_jobs'),
                      env.Dir(build_dir).path, env.Dir(app_root).abspath))
    env.Clean(lib, [os.path.join(app_root, x) for x in ('libs', 'obj')])
    return lib

# monkey patch emit_java_classes to do the Right Thing
# otherwise generated classes have no package name and get rebuilt always
import SCons.Tool.javac
from SCons.Tool.JavaCommon import parse_java_file

default_java_emitter = SCons.Tool.javac.emit_java_classes

def emit_java_classes(target, source, env):
    classdir = target[0]
    tlist, slist = default_java_emitter(target, source, env)
    if env.has_key('APP_PACKAGE'):
        out = []
        sourcedir = source[0]
        for s in slist:
            base = s.name.replace('.java', '.class')
            classname = env['APP_PACKAGE'] + s.name.replace('.java', '')
            jf = sourcedir.File(env['APP_PACKAGE'].replace('.', '/') + '/' + s.name)
            if os.path.exists(jf.abspath):
                version = env.get('JAVAVERSION', '1.4')
                pkg_dir, classes = parse_java_file(jf.rfile().get_abspath(), version)
                for c in classes:
                    t = classdir.File(pkg_dir + '/' + str(c) + '.class')
                    t.attributes.java_classdir = classdir
                    t.attributes.java_sourcedir = s.dir
                    t.attributes.java_classname = str(c)
                    out.append(t)
            else:
                t = classdir.File(env['APP_PACKAGE'].replace('.', '/') + '/' + base)
                t.attributes.java_classdir = classdir
                t.attributes.java_sourcedir = s.dir
                t.attributes.java_classname = classname
                out.append(t)
        return out, slist
    else:
        return tlist, slist


SCons.Tool.javac.emit_java_classes = emit_java_classes


def AndroidApp(env, name, manifest='#/AndroidManifest.xml',
              source='src', resources='#/res',
              resources_depfile=None,
              native_folder='libs'):
    android_manifest = env.File(manifest)

    if not env.has_key('ANDROID_TARGET'):
        env['ANDROID_TARGET'] = env.GetAndroidTarget(android_manifest.abspath)
    env['ANDROID_JAR'] = os.path.join('$ANDROID_SDK','platforms/android-$ANDROID_TARGET/android.jar')
    if not env.has_key('APP_PACKAGE'):
        package = env.GetAndroidPackage(android_manifest.abspath)
    else:
        package = env['APP_PACKAGE']
    rfile = os.path.join('gen', get_rfile(package))
    gen = env.Dir('gen')

    # generate R.java
    r = env.Aapt(rfile, env.Dir(resources),
             MANIFEST=android_manifest.path,
             GEN=gen, RES=env.Dir(resources).abspath,
             AAPT_ARGS='''package -f -m
             -M $MANIFEST
             -S $RES
             -I $ANDROID_JAR
             -J $GEN'''.split())
    env.Depends(r, android_manifest)
    if resources_depfile:
        env.Depends(r, resources_depfile)

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
    ap = env.Aapt(name + '.ap_', [env.Dir(resources)],
                  MANIFEST=android_manifest.path,
                  RES=env.Dir(resources).abspath,
              AAPT_ARGS='''package -f -m
             -M $MANIFEST
             -S $RES
             -I $ANDROID_JAR
             -F $TARGET'''.split())
    env.Depends(ap, android_manifest)
    if resources_depfile:
        env.Depends(ap, resources_depfile)

    # package java -classpath jarutils.jar:androidprefs.jar:apkbuilder.jar com.android.apkbuilder.ApkBuilder
    # >> name-debug-unaligned.apk
    outname = name + '-debug-unaligned.apk'
    finalname = name + '-debug.apk'
    if env['ANDROID_KEY_STORE']:
        UNSIGNED='-u'
        outname = name + '-unsigned.apk'
        finalname = name + '.apk'
    else:
        UNSIGNED = ''
    unaligned = env.ApkBuilder(outname, env.Dir(native_folder),
                   NATIVE_FOLDER=env.Dir(native_folder).path,
                   UNSIGNED=UNSIGNED,
                   DEX=dex,
                   AP=ap,
                   APK_ARGS='''
                   $UNSIGNED
                   -f $DEX
                   -z $AP
                   -nf $NATIVE_FOLDER
                  '''.split())
    env.Depends(unaligned, [dex, ap])
    env.Depends(unaligned, env.subst('$APK_BUILDER_JAR').split())
    if env['ANDROID_KEY_STORE'] and env['ANDROID_KEY_NAME']:
        # jarsigner -keystore $ANDROID_KEY_STORE -signedjar $TARGET $SOURCE $ANDROID_KEY_NAME
        unaligned = env.JarSigner(name + '-unaligned.apk', unaligned)

    # zipalign -f 4 unaligned aligned
    app = env.ZipAlign(finalname, unaligned)
    # installation marker
    adb_install = env.Command(name + '-installed', app,
        ['adb install -r $SOURCE && date > $TARGET'])
    # do not run by default
    env.Ignore(adb_install[0].dir, adb_install)
    env.Alias('install', adb_install)

    if not env.has_key('APP_ACTIVITY'):
        activity = env.GetAndroidName(android_manifest.abspath)
    else:
        activity = env['APP_ACTIVITY']
    run = env.Command(name + '-run', app,
      ['adb shell am start -a android.intent.action.MAIN -n %s/%s%s'%(
          package, package, activity)])
    env.Depends(run, adb_install)
    env.Ignore(run[0].dir, run)
    env.Alias('run', run)

    return app

def GetVariable(env, variable, exit=True):
    if variable in os.environ:
        return os.environ[variable]
    elif variable in env:
        return env[variable]
    elif exit:
        print 'Please set %s. export %s=path' % (variable, variable)
        print "or run `scons %s=path'" % variable
        env.Exit(1)
    return None

def generate(env, **kw):
    ndk_path = GetVariable(env, 'ANDROID_NDK')
    sdk_path = GetVariable(env, 'ANDROID_SDK')

    if 'ANDROID_KEY_STORE' not in env:
        env['ANDROID_KEY_STORE'] = ''

    if 'ANDROID_KEY_NAME' not in env:
        env['ANDROID_KEY_NAME'] = ''

    env.Tool('javac')
    env.Tool('jar')
    env['AAPT'] = '$ANDROID_SDK/platforms/android-$ANDROID_TARGET/tools/aapt'
    env['DX'] = '$ANDROID_SDK/platforms/android-$ANDROID_TARGET/tools/dx'
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
    j = env.Java(target='toolclasses',
             source=['site_scons/site_tools/android/sdklib/ApkBuilderMain.java'],
             JAVACLASSPATH='$APK_BUILDER_CP',
             JAVASOURCEPATH=env.Dir('#site_scons/site_tools').path)
    env['APK_BUILDER_JAR'] = j

    bld = Builder(action='$JAVA -classpath $TOOL_CLASSES_DIR:$APK_BUILDER_CP android.sdklib.ApkBuilderMain $TARGET $APK_ARGS',
                  source_scanner=DirScanner,
                  TOOL_CLASSES_DIR=env.Dir('toolclasses'),
                  suffix='.apk')
    env.Append(BUILDERS = { 'ApkBuilder': bld })

    bld = Builder(action='$ZIPALIGN -f 4 $SOURCE $TARGET')
    env.Append(BUILDERS = { 'ZipAlign': bld })

    bld = Builder(action='$JARSIGNER -keystore $ANDROID_KEY_STORE -signedjar $TARGET $SOURCE $ANDROID_KEY_NAME')
    env.Append(BUILDERS = { 'JarSigner': bld })

    env.AddMethod(AndroidApp)
    env.AddMethod(NdkBuild)
    env.AddMethod(GetAndroidTarget)
    env.AddMethod(GetAndroidPackage)
    env.AddMethod(GetAndroidName)

def exists(env):
    return 1
