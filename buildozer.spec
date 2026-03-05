[app]

# (String) Title of your application
title = Pinjaman Cepat Cair

# (String) Package name
package.name = pinjolransom

# (String) Package domain (needed for android/ios packaging)
package.domain = org.ransom

# (String) Source code where the main.py live
source.dir = .

# (List) Source files to include (let everything)
source.include_exts = py,png,jpg,kv,atlas,txt

# (List) Application requirements
# python3,kivy,requests,pycryptodome
requirements = python3,kivy==2.1.0,requests,pycryptodome

# (String) Orientation of the application
orientation = portrait

# (List) Supported OS
osx.python_version = 3
osx.kivy_version = 2.1.0

# (String) Android SDK version
android.api = 31
android.minapi = 21
android.ndk = 23b
android.sdk = 31

# (Boolean) Enable AndroidX
android.enable_androidx = True

# (List) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (String) Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# (Boolean) If True, then also try to copy files and resources to Android
android.copy_libs = True

# (Boolean) If True, then build in debug mode
android.debug = False

# (Boolean) If True, then compile python to .pyo
android.pyo = True

# (Boolean) If True, then we try to use the llvm compiler
android.ndk_compiler = clang

# (String) Log level (debug, info, warning, error)
log_level = 2

# (Boolean) If True, then we try to use the --release option
android.release = True

# (String) Architectures to build for
android.arch = arm64-v8a, armeabi-v7a

# (String) Sign the APK
android.sign = True

# (String) Key alias for signing
android.keyalias = mykey

# (String) Key password
android.keyalias.password = android

# (String) Keystore password
android.keystore.password = android

# (String) Keystore file
android.keystore = ~/.android/debug.keystore