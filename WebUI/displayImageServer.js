const express = require('express');
const fs = require('fs');
const path = require('path');
const WebSocket = require('ws');
const multer = require('multer');
const crypto = require('crypto');

const app = express();
const port = 3000;

// Generate a random filename
const generateRandomFilename = (originalname) => {
    const randomBytes = crypto.randomBytes(16).toString('hex');
    const timestamp = Date.now();
    const extension = path.extname(originalname);
    return `${timestamp}${randomBytes}${extension}`;
};

const uploadFolder = path.resolve(__dirname, '../preCheck');
const imagesFolder = path.resolve(__dirname, 'public/pass');
const publicFolder = path.resolve(__dirname, 'public');
console.log('Images folder path:', imagesFolder);
console.log('Public folder path:', publicFolder);

app.use('/pass', express.static(imagesFolder));
app.use(express.static(publicFolder));

// Set up storage engine using multer
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadFolder);
    },
    filename: (req, file, cb) => {
        cb(null, generateRandomFilename(file.originalname));
    }
});

const upload = multer({ storage: storage });

// Route to handle image upload
app.post('/upload', upload.single('image'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ message: 'No file uploaded' });
    }
    res.status(200).json({ message: 'File uploaded successfully' });
});

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
