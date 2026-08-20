[app]
title = ADB Scanner Pro
package.name = adbscanner
package.domain = org.vinh
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, ACCESS_WIFI_STATE, ACCESS_NETWORK_STATE

# Cấu hình ép buộc phiên bản ổn định và tự động nhận giấy phép SDK
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
