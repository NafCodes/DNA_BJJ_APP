import 'dotenv/config';
import express from 'express';

const app = express();
app.use(express.json());

// Routes go here (once built)

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));