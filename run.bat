@echo off
start cmd /k "python ..\main.py --listen"
timeout -nobreak 12
start cmd /k "cd WebUI\ && python server.py"
start http://127.0.0.1:8000/
start cmd /k "cd pythonModule && python python_comfy_api.py"
