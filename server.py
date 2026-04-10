#!/usr/bin/env python3
"""
Coastal Peak Renovations — Local Development Server
Handles static file serving + POST /submit-lead to save leads to leads.json

Usage: python3 server.py
Then open http://localhost:8080/
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json, os, datetime

PORT = 8080
LEADS_FILE = 'leads.json'


class CPRHandler(SimpleHTTPRequestHandler):

    def do_POST(self):
        if self.path == '/submit-lead':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length).decode('utf-8')
                data = json.loads(body)
                data['_timestamp'] = datetime.datetime.now().isoformat()
                data['_ip'] = self.client_address[0]

                # Load existing leads
                leads = []
                if os.path.exists(LEADS_FILE):
                    with open(LEADS_FILE, 'r') as f:
                        leads = json.load(f)

                leads.append(data)

                with open(LEADS_FILE, 'w') as f:
                    json.dump(leads, f, indent=2)

                print(f"[LEAD] New lead saved: {data.get('name')} — {data.get('service')}")

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'message': 'Lead saved.'}).encode())

            except Exception as err:
                print(f"[ERROR] Failed to save lead: {err}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(err)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def log_message(self, fmt, *args):
        # Suppress noisy GET logs; keep POST/error output
        if args and (str(args[1]) == '200' and args[0].startswith('GET')):
            return
        super().log_message(fmt, *args)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('localhost', PORT), CPRHandler)
    print(f'CPR local dev server running at http://localhost:{PORT}/')
    print(f'Lead submissions will be saved to: {os.path.abspath(LEADS_FILE)}')
    print('Press Ctrl+C to stop.\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')
