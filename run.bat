@echo off
@REM del /s/q WebUI\public\log\*.json
start cmd /k "python ..\main.py --listen"
start cmd /k "cd WebUI\public && forfiles /P pass /s /D -14 /C "cmd /c move @file ../archive" && exit || exit"
start cmd /k "cd WebUI\public && forfiles /P log /s /D -5 /C "cmd /c move @file ../archive" && exit || exit"
timeout -nobreak 40
start cmd /k "cd WebUI\ && node displayImageServer.js"
start cmd /k "cd pythonModule && python python_comfy_api.py"
start cmd /k "cd pythonModule && python tencentcloudCheckSDK.py"
timeout -nobreak 10
start .\WebUI\Display.lnk --kiosk