import http.server
import socketserver

# 设置服务器端口
PORT = 8000

# 使用SimpleHTTPRequestHandler创建一个简单的HTTP请求处理器
Handler = http.server.SimpleHTTPRequestHandler

# 创建一个服务器，并绑定到指定的端口
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    # 开始监听并处理请求
    httpd.serve_forever()
