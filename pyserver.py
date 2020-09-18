#!/usr/bin/env python3
"""
파이썬 웹서버
작성자: actionshin@gmail.com
작성일: 2020-09-17
"""
import os
import re
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote


class S(BaseHTTPRequestHandler):
    post_data = None

    def __init__(self, request, client_address, server):
        # 아래 server_class의 인수로 클래스가 전달되므로 super()을 사용하면 S를 가르키게 된다.
        # 따라서 BaseHTTPRequestHandler를 직접 지정한다.
        # super().__init__(self, request, client_address, server) # <-- class S
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def _set_response(self, status):
        self.send_response(status)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        # favicon.ico - 404 Not Found 무시
        if self.path.endswith('favicon.ico'):
            return
        # 환영 및 홈페이지 링크
        if self.path == '/':
            self._set_response(200)
            self.wfile.write(b"<ul>")
            self.wfile.write("<li>GET request for {}, {}</li>".format(self.path, self.post_data).encode('utf-8'))
            self.wfile.write(
                "<li><a href='./static/html/index.html'>index.html</a></li>".format(self.path, self.post_data).encode(
                    'utf-8'))
            self.wfile.write(b"</ul>")
        else:
            base_path = os.getcwd()
            req_path = re.sub(r'^/', '', self.path)
            try:
                with open(os.path.join(base_path, req_path), 'rb') as file:
                    # logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                    #             str(self.path), str(self.headers), post_data.decode('utf-8'))
                    logging.info("POST request,\nPath: %s\nBody:\n%s\n", str(self.path), self.post_data)
                    self._set_response(200)
                    self.wfile.write(file.read())
            except FileNotFoundError as err:
                print(err, req_path)
                self._set_response(404)
                self.wfile.write("[에러] {}를 찾을 수 없습니다.".format(req_path).encode('utf-8'))
            except IsADirectoryError as err:
                print(err, req_path)
                self._set_response(500)
                self.wfile.write("[에러] {}는 디렉토리입니다.".format(req_path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        # %ED%95%9C%EA%B8%80 -> 한글
        self.post_data = unquote(self.rfile.read(content_length).decode('utf-8'))  # <--- Gets the data itself
        self.do_GET()


def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
