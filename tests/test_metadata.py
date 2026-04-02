import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from x_job_monitor.metadata import fetch_external_metadata


class MetadataHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = """
        <html>
          <head>
            <title>Fallback Title</title>
            <meta name="description" content="Meta description">
            <meta property="og:title" content="OG Title">
          </head>
          <body>Hello</body>
        </html>
        """.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


def test_fetch_external_metadata_parses_head_tags():
    server = HTTPServer(("127.0.0.1", 0), MetadataHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        metadata = fetch_external_metadata(
            url=f"http://127.0.0.1:{server.server_address[1]}/",
            timeout_seconds=5,
            user_agent="test-agent",
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert metadata.title == "OG Title"
    assert metadata.description == "Meta description"

