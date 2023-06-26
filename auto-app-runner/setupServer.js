const http = require('http');
const fs = require('fs');
const process = require('process');

const port = 8080;

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/submit-repo-url') {
    let body = '';

    req.on('data', (chunk) => {
      body += chunk;
    });

    req.on('end', () => {
      fs.writeFile('REPO_URL', body, (err) => {
        if (err) {
          console.error(err);
          res.statusCode = 500;
          res.end('Error writing to file');
        } else {
          res.statusCode = 200;
          res.end('File written successfully');
          process.exit(0)
        }
      });
    });
  } else if (req.method === 'POST' && req.url === '/exit') {
    process.exit(0)
  } else if (req.method === 'GET' && req.url === '/log') {
    fs.readFile('log.txt', (err, data) => {
      if (err) {
        console.error(err);
        res.statusCode = 500;
        res.end('Error reading file');
      } else {
        res.setHeader('Content-Type', 'text/plain');
        res.statusCode = 200;
        res.end(data);
      }
    });
  } else if (req.method === 'GET') {
    fs.readFile('inputClient.html', (err, data) => {
      if (err) {
        console.error(err);
        res.statusCode = 500;
        res.end('Error reading file');
      } else {
        res.setHeader('Content-Type', 'text/html');
        res.statusCode = 200;
        res.end(data);
      }
    });
  } else {
    res.statusCode = 404;
    res.end('Not found');
  }
});

server.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});