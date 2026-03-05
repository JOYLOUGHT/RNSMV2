[app]
title = Pinjaman Cepat Cair
package.name = pinjolransom
package.domain = org.ransom

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

requirements = python3,kivy==2.1.0,requests,pycryptodome

orientation = portrait

osx.python_version = 3
osx.kivy_version = 2.1.0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 31                    # PAKSA API 31
minapi = 21                  # Minimal Android 5.0
ndk = 23b
sdk = 31

permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.accept_sdk_license = True
android.ndk_path = 
android.sdk_path = 

[requirements]
android.api = 31
android.minapi = 21
android.ndk = 23b
android.sdk = 31