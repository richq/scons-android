# A SCons Tool to Build Android Applications

## Installation

The easiest way to use this tool is to clone it into a `site_scons/site_tools`
directory:

    mkdir -p site_scons/site_tools
    cd site_scons/site_tools
    git clone git://github.com/richq/scons-android.git android

## Basic Usage of the AndroidApp function

Add the tool to the Environment in your SConstruct file and use the AndroidApp
construction function:

    var = Variables(None, ARGUMENTS)
    var.AddVariables(PathVariable('ANDROID_SDK', 'Android SDK path', None))
    env = Environment(tools=['android'], variables=var)
    env.AndroidApp('MyApp')

This assumes a standard layout, with an `AndroidManifest.xml` file, and `src`
and `res` directories. To run the compilation:

    scons ANDROID_SDK=/path/to/sdk

The advantage over a regular ant build is that dependencies are handled better
- instead of regenerating R.java every time, it is only generated when the
resource files change. This means builds do not take as long.

## Using NdkBuild to Build Native Code

In addition, you can incorporate NDK code quite easily:

    var = Variables(None, ARGUMENTS)
    var.AddVariables(
            PathVariable('ANDROID_NDK', 'Android NDK path', None))
            PathVariable('ANDROID_SDK', 'Android SDK path', None))
    env = Environment(tools=['android'], variables=var)
    lib = env.NdkBuild('libs/armeabi/libmyshared.so', ['jni/my_code.c'])
    apk = env.AndroidApp('MyApp', native_folder='#libs')

This will use SCons's SharedLibrary builder to create a shared library from
your code. If you want to use an Android.mk-style build, which requires
creating an Android.mk file, then you can use `NdkBuildLegacy`:

    lib = env.NdkBuildLegacy('libs/armeabi/libmyshared.so', ['jni/my_code.c'])

This is the older way of doing things and scons passes the native compilation
work off to GNU Make. You can use more of the ndk-build features, but at the
cost of extra rebuilds and having to maintain both SCons script and Makefiles.

## Application ABIs

To compile multiple architectures at once, you can use the `app_abis` argument.
This is a list of ABIs or a space-separated string value. Suitable values are
`armeabi`, `armeabi-v7a` and `x86`. The default is `armeabi`.

    libs = env.NdkBuild('libmyshared.so', ['jni/my_code.c'],
                            app_abis='armeabi armeabi-v7a x86')

If you don't specify the explicit output libraries then they are placed in
sensibly named directories for the architecture. In the example above, these
are:

    libs/armeabi/libmyshared.so
    libs/armeabi-v7a/libmyshared.so
    libs/x86/libmyshared.so

You can also specify the full path of each library, but they must match
up with the list of `app_abis`:

    libs = env.NdkBuild(['arm/armeabi/libtest.so', 'intel/x86/libtest.so'],
                        ['jni/test.c'], app_abi='armeabi x86')
    env.AndroidApp('TestArm', native_folder='arm')
    env.AndroidApp('TestIntel', native_folder='intel')

This way you can create multiple APK files each with a single library, rather
than fat APK files with multiple libraries for different architectures.

## AndroidManifest.xml with NdkBuild

In order to determine the minimum target platform the NdkBuild needs to know
where the AndroidManifest.xml file is. The default location is
`'#AndroidManifest.xml'`, which corresponds to an AndroidManifest in the top of
your project. The argument `manifest` can be used to override this:

    env.NdkBuild('arm/armeabi/libtest.so',
                    ['jni/test.c'],
                    manifest='#path/to/AndroidManifest.xml')

This is useful if your project does not use the standard Android layout.

## ProGuard

Enabling ProGuard in your project is done by setting PROGUARD_CONFIG to the
name of the configuration file. This is analogous to the way it is done in the
official build system and lets you make use of the `android` command line tool
to generate the correct configuration. For Android SDK r16 and earlier you
should use a line like this to use the generated configuration file:

    env['PROGUARD_CONFIG'] = 'proguard.cfg'

Prior to Android SDK r17 the `proguard.cfg` file contained all of the
configuration settings needed for Android. This was a bad idea as updates to
the defaults would mean manual steps to regenerate proguard.cfg for every
Android developer. From r17 onwards a default configuration template is
included in the SDK, so your PROGUARD_CONFIG value should look like this:

    # Android SDK r17+
    env['PROGUARD_CONFIG'] = '$ANDROID_SDK/tools/proguard/proguard-android.txt:proguard-project.txt'

This will use the SDK's configuration followed by your own. Note the name
change to proguard-project.txt. You must separate configuration files with
the path seperator symbol ':' or ';'. The `android` tool actually creates an
empty proguard config file now (it just has comments) so there's really no need
to use your own if you are happy with the defaults. In that case, the
PROGUARD_CONFIG value can be:

    # Android SDK r17+, just the defaults
    env['PROGUARD_CONFIG'] = '$ANDROID_SDK/tools/proguard/proguard-android.txt'

ProGuard is only executed when you run a release build, which is only performed
when the ANDROID_KEY_STORE and ANDROID_KEY_NAME variables are set in the
Environment used in `env.AndroidApp()`.

## Native Activity

The native activity feature was new in Android 2.3 and provides a way to create
an Android application without any Java source code. In order to use it, you
have to include a bit of glue code that is distributed in source form in the
Android NDK. The source code is in "NDK Module" form, which sadly depend
heavily on the ndk-build infrastructure and Makefile syntax for their
meta-data.

However, since this is such a simple module you can make some assumptions and
use the following snippet to build the glue code together with your native
activity:

    env.Repository('$ANDROID_NDK/sources')
    glue_code = env.Glob('android/native_app_glue/*.c')
    env['CPPPATH'] = 'android/native_app_glue'
    env.MergeFlags('-llog -landroid')
    env.NdkBuild('libmyactivity.so', ['jni/my_code.c', glue_code])
    env.AndroidApp('MyApp')

Using a Repository means SCons will search for files there as well as in your
local project. This means you don't have to copy the `native_app_glue` code
into your own project.

The Glob call picks up any C code in that directory. This is a bit naughty, as
the real code contents is defined in the `Android.mk` file inside the module.

Setting the CPPPATH to `android/native_app_glue` is another slight compromise,
since again the real "export path" is described in Android.mk.

Adding -llog to the list of link flags is also an assumption based on
inspection of the Android.mk file.

In future versions of this tool, I am toying with adding an NdkImportModule
feature to automate the above snippet. I've had no need for this yet though, so
it isn't high priority.

## Environment Variables

The following environment variables or SCons `Variables` are used to control the build:

* ANDROID\_KEY\_STORE: Android keystore
* ANDROID\_KEY\_NAME: Android keyname
* ANDROID\_NDK: Android NDK path
* ANDROID\_SDK: Android SDK path

The NDK/SDK paths are hopefully obvious. The key store and key name are used to
create the final signed release. Without these being set, a debug build is
created using the debug key. See [the official documentation][1] for more
details.  To create a release build with your keys in 'my-release-key.keystore'
and the key to be used 'alias\_name', you would run the following:

    scons ANDROID_KEY_STORE=my-release-key.keystore ANDROID_KEY_NAME=alias_name

This assumes you are using SCons's `Variables` API to keep track of options.

## Installing to a Device

An `install` target is added which will run `adb install` for your generated
APK file. This means to install on the device, just run:

    scons install

If no changes have been made since the last install, nothing is installed.

## Drawbacks

Not requiring an Android.mk file for NDK builds gives tighter dependency
tracking and less spurious rebuilds. However Android's `ndk-build` has a great
deal of features to cover and creating a suitable SCons API is time consuming,
error prone and can become obsolete or broken between NDK releases.

There is no way to create an Android library project, only applications.

Only compilation on Linux has been tested.

[1]: http://developer.android.com/guide/publishing/app-signing.html
