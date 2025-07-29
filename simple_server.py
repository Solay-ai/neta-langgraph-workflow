#!/usr/bin/env python3
"""
Simple HTTP server for Neta LangGraph workflow
No PostgreSQL or Redis required - uses in-memory storage
Completely FREE and self-contained
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from simple_neta import invoke_workflow
import traceback

class NetaHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests to execute workflow"""
        try:
            # Parse the request path
            path = urllib.parse.urlparse(self.path).path
            
            if path == '/threads/test/runs' or path == '/runs':
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                # Extract input
                input_data = request_data.get('input', {})
                assistant_id = request_data.get('assistant_id', '')
                
                print(f"🚀 Received request for assistant: {assistant_id}")
                print(f"📤 Input: {input_data}")
                
                # Execute the workflow
                result = invoke_workflow(input_data)
                
                # Return the result
                response = {
                    "status": "completed",
                    "output": result
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Api-Key')
                self.end_headers()
                
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
                print(f"✅ Response sent: {len(str(response))} characters")
                
            else:
                # Return 404 for unknown paths
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"detail": "Not Found"}).encode('utf-8'))
                
        except Exception as e:
            print(f"❌ Error processing request: {e}")
            traceback.print_exc()
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Api-Key')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests - health check"""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            health_response = {
                "status": "healthy",
                "service": "Neta Social Assistant",
                "version": "1.0.0",
                "assistant_id": "neta-social-assistant"
            }
            self.wfile.write(json.dumps(health_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def start_server(port=2024):
    """Start the simple HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, NetaHandler)
    
    print(f"🌟 Neta LangGraph Server starting on http://localhost:{port}")
    print(f"📋 Assistant ID: neta-social-assistant")
    print(f"🧪 Health check: http://localhost:{port}/health")
    print(f"📤 API endpoint: http://localhost:{port}/runs")
    print("🔄 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()

if __name__ == "__main__":
    start_server()