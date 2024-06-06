// server.js
const express = require('express');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
const app = express();
const port = 3000;

const imagesFolder = path.resolve(__dirname, '../pass');
const publicFolder = path.resolve(__dirname, 'public');
console.log('Images folder path:', imagesFolder);
console.log('Public folder path:', publicFolder);

app.use('/pass', express.static(imagesFolder));
app.use(express.static(publicFolder));

app.get('/image-list', (req, res) => {
    fs.readdir(imagesFolder, (err, files) => {
        if (err) {
            console.error('Error scanning folder:', err);
            return res.status(500).send('Unable to scan folder');
        }
        const imageFiles = files.filter(file => /\.(jpg|jpeg|png|gif|webp)$/.test(file));
        res.json(imageFiles);
    });
});

const server = app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

const wss = new WebSocket.Server({ server });

wss.on('connection', ws => {
    console.log('Client connected');

    ws.on('close', () => {
        console.log('Client disconnected');
    });
});

fs.watch(imagesFolder, (eventType, filename) => {
    if (filename && /\.(jpg|jpeg|png|gif|webp)$/.test(filename)) {
        console.log(`${filename} file Changed`);
        const imageFiles = fs.readdirSync(imagesFolder).filter(file => /\.(jpg|jpeg|png|gif|webp)$/.test(file));
        const data = JSON.stringify({ newImage: filename, allImages: imageFiles });
        wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(data);
            }
        });
    }
});
