"""
HyperGraphQL API Server

Simple HTTP server for HyperGraphQL API endpoints.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs

from .hypergraphql.endpoints import GraphQLEndpoint, RESTEndpoints


class HyperGraphQLHandler(BaseHTTPRequestHandler):
    """HTTP request handler for HyperGraphQL API."""
    
    graphql_endpoint = GraphQLEndpoint()
    rest_endpoints = RESTEndpoints()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # Extract query parameters
        params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        
        if path.startswith('/api/organizations/'):
            org_id = path.split('/')[-1]
            response = self.rest_endpoints.get_organization(org_id)
            self._send_json_response(response)
        elif path == '/api/organizations':
            response = self.rest_endpoints.list_organizations(
                org_type=params.get('type'),
                parent_org_id=params.get('parentOrgId')
            )
            self._send_json_response(response)
        elif path == '/health':
            self._send_json_response({'status': 'healthy'})
        else:
            self._send_json_response(
                {'error': 'Not found'},
                status_code=404
            )
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json_response(
                {'error': 'Invalid JSON'},
                status_code=400
            )
            return
        
        # Route to appropriate endpoint
        if path == '/graphql':
            response = self.graphql_endpoint.handle_http_request(data)
            self._send_json_response(response)
        elif path == '/api/organizations':
            response = self.rest_endpoints.create_organization(data)
            self._send_json_response(response)
        elif path == '/api/github/sync/from':
            response = self.rest_endpoints.sync_from_github(data)
            self._send_json_response(response)
        elif path == '/api/github/sync/to':
            response = self.rest_endpoints.sync_to_github(data)
            self._send_json_response(response)
        elif path == '/api/github/init':
            response = self.rest_endpoints.create_repo_structure(data)
            self._send_json_response(response)
        elif path == '/api/hypergraph/compress':
            response = self.rest_endpoints.compress_hypergraph(data)
            self._send_json_response(response)
        elif path == '/api/hypergraph/expand/org':
            response = self.rest_endpoints.expand_to_org_level(data)
            self._send_json_response(response)
        else:
            self._send_json_response(
                {'error': 'Not found'},
                status_code=404
            )
    
    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_json = json.dumps(data, indent=2, ensure_ascii=False)
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        print(f"{self.address_string()} - {format % args}")


def run_server(port: int = 8080, host: str = '0.0.0.0'):
    """
    Run the HyperGraphQL API server.
    
    Args:
        port: Port to listen on
        host: Host to bind to
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, HyperGraphQLHandler)
    
    print(f"HyperGraphQL API Server running on http://{host}:{port}")
    print(f"GraphQL endpoint: http://{host}:{port}/graphql")
    print(f"Health check: http://{host}:{port}/health")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
