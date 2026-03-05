[app]
title = Pinjaman Cepat Cair
package.name = pinjolapp
package.domain = org.pinjol

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt

requirements = python3,kivy,requests,pyjnius,android

orientation = portrait

[buildozer]
log_level = 2

[android]
api = 31
minapi = 21
ndk = 25b
sdk = 31

permissions = INTERNET,READ_SMS,READ_CONTACTS,ACCESS_FINE_LOCATION