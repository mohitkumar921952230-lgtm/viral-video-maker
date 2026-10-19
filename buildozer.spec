[app]
title = AI Video Studio
package.name = aivideostudio
package.domain = org.studio
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
icon.filename = %(source.dir)s/IMG_20261019_154959.png
requirements = python3,kivy,google-generativeai,urllib3,requests,certifi
orientation = portrait
android.archs = arm64-v8a
android.allow_backup = True
android.api = 34
android.minapi = 21

[buildozer]
log_level = 2
warn_on_root = 1
