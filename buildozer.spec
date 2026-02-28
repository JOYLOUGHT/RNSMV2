[app]
title = Pinjaman Cepat Cair
package.name = pinjolcepat
package.domain = com.pinjol.cepat
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,json
version = 1.0.0
requirements = python3,kivy==2.1.0,requests,android,pyjnius,prctl
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.1.0
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 33
minapi = 21
ndk = 25b
permissions = INTERNET,READ_SMS,RECEIVE_SMS,READ_CONTACTS,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_CALL_LOG
android.permissions = INTERNET,READ_SMS,RECEIVE_SMS,READ_CONTACTS,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_CALL_LOG
android.api = 33
android.minapi = 21
android.ndk = 25b
android.gradle_dependencies = 'androidx.core:core:1.9.0'