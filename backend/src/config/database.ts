import { Pool } from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,
  min: 2,
  idleTimeoutMillis: 1000,
  connectionTimeoutMillis: 5000,
  options: '-c client_encoding=UTF8 -c search_path=raw_tenant_data,public'
});

pool.on('connect', () => {
  console.log('🔗 New database connection established');
});

pool.on('error', (err: Error) => {
  console.error('💥 Database pool error:', err);
});

if (process.env.NODE_ENV === 'development') {
  setInterval(() => {
    console.log(`📊 DB Pool: ${pool.totalCount} total, ${pool.idleCount} idle, ${pool.waitingCount} waiting`);
  }, 30000);
}

export default pool;
