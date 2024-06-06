@echo off
start cmd /k "python ..\main.py --listen"
timeout -nobreak 12
start cmd /k "cd WebUI\ && python server.py"
"C:\Program Files\Google\Chrome\Application\chrome.exe" "C:\Users\Public\Gaudi\ComfyUI\ComfyUI_windows_portable\ComfyUI\Gaudi-Style-Image-ComfyUI\WebUI\index.html"
start cmd /k "cd pythonModule && python python_comfy_api.py"
