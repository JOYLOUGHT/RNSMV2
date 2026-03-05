[app]
title = Pinjaman Cepat Cair
package.name = pinjolransom
package.domain = org.ransom

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

requirements = python3,kivy==2.3.1,requests,pycryptodome  # UBAH KE 2.3.1

orientation = portrait

osx.python_version = 3
osx.kivy_version = 2.3.1  # UBAH JUGA

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 31
minapi = 21
ndk = 25.2.9519653
sdk = 31

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.accept_sdk_license = True

[requirements]
android.api = 31
android.minapi = 21
android.ndk = 25.2.9519653
android.sdk = 31