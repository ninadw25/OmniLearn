const express = require('express');
const path = require('path');
const multer = require('multer');
const axios = require('axios');
const FormData = require('form-data');
const cors = require('cors');

const app = express();
const port = 3000;
const FASTAPI_URL = 'http://localhost:8000';

// Middleware
app.use(express.json());
app.use(cors());
app.use(express.static(path.join(__dirname, 'public')));

// Multer configuration for file uploads
const upload = multer();

// API routes
app.post('/api/chat', async (req, res) => {
    try {
        const response = await axios.post(`${FASTAPI_URL}/chat`, req.body);
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/upload', upload.array('files'), async (req, res) => {
    try {
        const formData = new FormData();
        req.files.forEach((file) => {
            formData.append('files', file.buffer, file.originalname);
        });
        formData.append('session_id', req.body.session_id);

        const response = await axios.post(`${FASTAPI_URL}/upload`, formData, {
            headers: {
                ...formData.getHeaders(),
            },
        });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Serve the main landing page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Serve the document Q&A feature
app.get('/features/document-qa', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'features', 'document-qa.html'));
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});