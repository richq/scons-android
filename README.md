# A SCons Tool to Build Android Applications

## Installation

The easiest way to use this tool is to clone it into a site_scons/site_tools
directory:

    mkdir -p site_scons/site_tools
    cd site_scons/site_tools
    git clone git://github.com/richq/scons-android.git android

## Basic Usage of the AndroidApp Builder

Add the tool to the Environment in your SConstruct file and use the AndroidApp
builder:

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

In addition, you can incorporate NDK code quite easily (well not really that
easily, but it's not too bad):

    var = Variables(None, ARGUMENTS)
    var.AddVariables(
            PathVariable('ANDROID_NDK', 'Android NDK path', None))
            PathVariable('ANDROID_SDK', 'Android SDK path', None))
    env = Environment(tools=['android'], variables=var)
    lib = env.NdkBuild('libs/armeabi/libmyshared.so', ['jni/my_code.c'])
    apk = env.AndroidApp('MyApp', native_folder='#libs')
    env.Depends(apk, lib)

Sadly, the NdkBuild still requires a complete Android.mk file and really just
passes on the work to `ndk-build`, aka GNU Make.

## Environment Variables

The following environment variables or SCons `Variables` are used to control the build:

* ANDROID_KEY_STORE: Android keystore
* ANDROID_KEY_NAME: Android keyname
* ANDROID_NDK: Android NDK path
* ANDROID_SDK: Android SDK path

The NDK/SDK paths are obvious. The key store and key name are used to create
the final signed release. Without these being set, a debug build is created
using the debug key. See [the official documentation][1] for more details.
To create a release build with your keys in 'my-release-key.keystore' and the
key to be used 'alias_name', you would run:

    scons ANDROID_KEY_STORE=my-release-key.keystore ANDROID_KEY_NAME=alias_name

## Installing to a Device

An `install` target is added which will run `adb install` for your generated
APK file. This means to install on the device, just run:

    scons install

If no changes have been made since the last install, nothing is installed.

## Drawbacks

I am unsure as to whether to remove the requirement of an Android.mk file or
not for NDK builds. Having a self-contained build would give tighter dependency
tracking and less spurious rebuilds. However the ndk-build has a great deal of
features to cover and creating a suitable SCons API is time consuming, error
prone and can become obsolete or broken between NDK releases.

There is no way to create an Android library project, only applications.

The dependency on the native library in an SDK/NDK build has to be added after
the fact, it is currently not autodetected.

[1]: http://developer.android.com/guide/publishing/app-signing.html
