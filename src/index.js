import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import studentsRouter  from './routes/students.js';
import stripesRouter   from './routes/stripes.js';
import attendanceRouter from './routes/attendance.js';

const app = express();
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
  credentials: true,
}));
app.use(express.json());

app.use('/students',   studentsRouter);
app.use('/stripes',    stripesRouter);
app.use('/attendance', attendanceRouter);

app.get('/health', (req, res) => res.json({ status: 'ok' }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
