import 'dotenv/config';
import express from 'express';
import cors from 'cors';

const app = express();

app.use(cors({
  origin: [
    'http://localhost:5173',
    'https://your-vercel-url.vercel.app' // TODO: replace with actual Vercel URL after frontend is deployed
  ]
}));

app.use(express.json());

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Routes go here (once built)

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));