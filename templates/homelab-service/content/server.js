# Minimal Node HTTP service — the scaffolded skeleton.
# Replace server.js with your real app; the Dockerfile + CI stay.

const http = require('http');

const port = process.env.PORT || 3000;

http
  .createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Hello from ${{ values.name }}\n');
  })
  .listen(port, () => {
    console.log(`${{ values.name }} listening on :${port}`);
  });
