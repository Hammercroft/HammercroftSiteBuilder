#!/usr/bin/env python3
"""
Simple Local HTTP Server
Serves files from the current directory over HTTP.
"""

import http.server
import socketserver
import sys
import os

# Configuration
DEFAULT_PORT = 8000
HOST = "localhost"

def main():
    # Get port from command line argument or use default
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            print(f"Usage: {sys.argv[0]} [port]")
            sys.exit(1)
    
    # Create server
    handler = http.server.SimpleHTTPRequestHandler
    
    try:
        with socketserver.TCPServer((HOST, port), handler) as httpd:
            print(f"Server running at http://{HOST}:{port}/")
            print(f"Serving files from: {os.getcwd()}")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except OSError as e:
        if e.errno == 98 or e.errno == 48:  # Address already in use
            print(f"Error: Port {port} is already in use.")
            print("Try a different port or stop the process using that port.")
            sys.exit(1)
        else:
            raise

if __name__ == "__main__":
    main()
