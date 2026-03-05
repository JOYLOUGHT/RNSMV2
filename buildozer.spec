[app]
title = Pinjaman Cepat Cair
package.name = pinjolransom
package.domain = org.ransom

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

requirements = python3,kivy==2.1.0,requests,pycryptodome

orientation = portrait

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 31
minapi = 21
ndk = 25
sdk = 31

permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

p4a.branch = develop
android.accept_sdk_license = True

[requirements]
android.api = 31
android.minapi = 21
android.ndk = 25
android.sdk = 31