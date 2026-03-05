[app]
title = Pinjaman Cepat Cair
package.name = pinjolransom
package.domain = org.ransom

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

# Requirements dengan Kivy 3.0.0
requirements = python3,kivy==3.0.0,requests,pycryptodome

orientation = portrait

osx.python_version = 3
osx.kivy_version = 3.0.0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 31
minapi = 21
ndk = 25.2.9519653        # PAKAI NDK 25 VERSI SPESIFIK
sdk = 31

# Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Biarkan buildozer menggunakan Android SDK/NDK dari sistem
android.accept_sdk_license = True

# Biarkan p4a yang handle
p4a.branch = develop

[requirements]
android.api = 31
android.minapi = 21
android.ndk = 25.2.9519653   # HARUS SAMA dengan di atas
android.sdk = 31