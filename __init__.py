#!/usr/bin/env python
import os
from SCons.Builder import Builder
from SCons.Defaults import DirScanner
from xml.dom import minidom

def get_rfile(fname):
    p = minidom.parse(open(fname))
    m = p.getElementsByTagName('manifest')[0]
    return os.path.join(m.getAttribute('package').replace('.', '/'), 'R.java')

def TargetFromProperties(fname):
    for line in open(fname).readlines():
        line = line.strip()
        if line.startswith('#'):
            continue
        key, val = line.split('=')
        if key == 'target':
            return val.split('-')[1]
    return None

def GetAndroidTarget(fname):
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
    target = GetAndroidTarget(android_manifest.abspath)
    lib = env.Command(os.path.join(app_root, library), env.Flatten(inputs),
                  '$ANDROID_NDK/ndk-build -j %s SCONS_BUILD_ROOT=%s APP_PLATFORM=android-%s -C %s' % (
                      env.GetOption('num_jobs'),
                      env.Dir(build_dir).path, target, env.Dir(app_root).abspath))
    return lib

def AndroidApp(env, name, manifest='#/AndroidManifest.xml',
              source='src', resources='#/res',
              resources_depfile=None,
              native_folder='libs'):
    android_manifest = env.File(manifest)

    env['ANDROID_TARGET'] = GetAndroidTarget(android_manifest.abspath)
    env['ANDROID_JAR'] = os.path.join('$ANDROID_SDK','platforms/android-$ANDROID_TARGET/android.jar')
    rfile = os.path.join('gen', get_rfile(android_manifest.abspath))
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
    bin_classes = 'bin/classes'
    classes = env.Java(target=bin_classes, source=[source],
                       JAVABOOTCLASSPATH='$ANDROID_JAR',
                       JAVASOURCEPATH=gen.path,
                       JAVACFLAGS='-g -encoding ascii'.split(),
                       JAVACLASSPATH=env.Dir(bin_classes).path)
    env.Depends(classes, rfile)

    # dex file from classes
    dex = env.Dex('classes.dex', classes, DX_DIR=env.Dir(bin_classes).path)

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
    return env.ZipAlign(finalname, unaligned)

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

def exists(env):
    return 1
