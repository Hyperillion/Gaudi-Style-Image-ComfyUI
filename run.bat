@echo off
@REM del /s/q WebUI\public\log\*.json
start cmd /k "python ..\main.py --listen"
timeout -nobreak 45
start cmd /k "cd WebUI\ && node displayImageServer.js"
start cmd /k "cd pythonModule && python python_comfy_api.py"
start cmd /k "cd pythonModule && python tencentcloudCheckSDK.py"
timeout -nobreak 10
start .\WebUI\Display.lnk --kiosk