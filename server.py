#!/usr/bin/env python
import BaseHTTPServer
import json
import os
import subprocess
import tempfile
import time

HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', '8080'))
OSIRIS = '/root/osiris/osiris.py'

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self._send(200, {'status': 'ok', 'service': 'Osiris'})
        else:
            self._send(404, {'error': 'not found'})

    def do_POST(self):
        if self.path != '/analyze':
            self._send(404, {'error': 'not found'})
            return

        try:
            length = int(self.headers.getheader('Content-Length', '0'))
            raw = self.rfile.read(length)
            data = json.loads(raw)
            source = data.get('source')
            contract = data.get('contract')
            timeout = int(data.get('timeout', 120))

            if not source or not isinstance(source, basestring):
                self._send(400, {'error': 'source is required'})
                return

            workdir = tempfile.mkdtemp(prefix='osiris-')
            source_path = os.path.join(workdir, 'contract.sol')
            with open(source_path, 'w') as f:
                f.write(source)

            cmd = ['python', OSIRIS, '-s', source_path]
            if contract:
                cmd.extend(['--contract', str(contract)])

            started = time.time()
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd='/root'
            )
            try:
                output = proc.communicate(timeout=timeout)[0]
            except TypeError:
                # Python 2 subprocess has no timeout argument.
                deadline = time.time() + timeout
                while proc.poll() is None and time.time() < deadline:
                    time.sleep(0.25)
                if proc.poll() is None:
                    proc.kill()
                output = proc.communicate()[0]
            elapsed = time.time() - started

            self._send(200 if proc.returncode == 0 else 422, {
                'ok': proc.returncode == 0,
                'exit_code': proc.returncode,
                'duration_seconds': round(elapsed, 2),
                'output': output
            })
        except Exception as exc:
            self._send(500, {'error': str(exc)})

    def log_message(self, fmt, *args):
        return

if __name__ == '__main__':
    server = BaseHTTPServer.HTTPServer((HOST, PORT), Handler)
    print('Osiris API listening on %s:%s' % (HOST, PORT))
    server.serve_forever()
