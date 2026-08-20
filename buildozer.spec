[app]
title = Remote ADB Master
package.name = adbmaster
package.domain = org.vinh
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 2.4
requirements = python3,kivy,charset-normalizer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, ACCESS_WIFI_STATE, ACCESS_NETWORK_STATE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
