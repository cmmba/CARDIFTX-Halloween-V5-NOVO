[app]

title = CARDIFTX Halloween V5
package.name = cardiftxhalloween
package.domain = org.cardiftx

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,wav,mp3,ttf

version = 5.0

requirements = python3,kivy

orientation = portrait
fullscreen = 1


[buildozer]

log_level = 2


[android]

android.api = 35
android.accept_sdk_license = True
p4a.branch = develop
android.minapi = 23
android.archs = arm64-v8a,armeabi-v7a
