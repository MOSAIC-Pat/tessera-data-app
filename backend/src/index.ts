import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import pool from './config/database';
import authRoutes from './routes/auth';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5001;

// Middleware
const allowedOrigins: string[] = process.env.NODE_ENV === 'production'
  ? [process.env.FRONTEND_URL].filter(Boolean) as string[]
  : [process.env.FRONTEND_URL || 'http://localhost:3005'];

app.use(cors({
  origin: allowedOrigins,
  credentials: true
}));
app.use(express.json());

// Health check route
app.get('/api/health', async (_req, res) => {
  try {
    const result = await pool.query('SELECT NOW()');
    res.json({
      message: 'Tessera Data API is running!',
      database: 'Connected',
      timestamp: result.rows[0].now,
      pool: {
        totalConnections: pool.totalCount,
        idleConnections: pool.idleCount,
        waitingConnections: pool.waitingCount
      }
    });
  } catch (error) {
    res.status(500).json({
      message: 'API running but database connection failed',
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Routes
app.use('/api/auth', authRoutes);

// Start server
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
