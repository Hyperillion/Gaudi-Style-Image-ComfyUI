@echo off
@REM del /s/q WebUI\public\log\*.json
start cmd /k "python ..\main.py --listen"
timeout -nobreak 20
start cmd /k "cd WebUI\ && node displayImageServer.js"
start cmd /k "cd pythonModule && python python_comfy_api.py"
start cmd /k "cd pythonModule && python tencentcloudCheckSDK.py"
start .\WebUI\Display.lnk --kiosk

