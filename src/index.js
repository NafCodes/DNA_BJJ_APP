import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import studentsRouter  from './routes/students.js';
import stripesRouter   from './routes/stripes.js';
import attendanceRouter from './routes/attendance.js';
import waiversRouter   from './routes/waivers.js';

const allowedOrigins = (process.env.CORS_ORIGIN || 'http://localhost:5173')
  .split(',').map(o => o.trim());

const app = express();
app.use(cors({
  origin: (origin, callback) => {
    if (!origin || allowedOrigins.includes(origin)) callback(null, true);
    else callback(new Error('Not allowed by CORS'));
  },
  credentials: true,
}));
app.use(express.json());

app.use('/students',   studentsRouter);
app.use('/stripes',    stripesRouter);
app.use('/attendance', attendanceRouter);
app.use('/waivers',    waiversRouter);

app.get('/health', (req, res) => res.json({ status: 'ok' }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
