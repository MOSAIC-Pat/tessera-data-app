# Tessera Data App

A full-stack web application with authentication built with Node.js, TypeScript, PostgreSQL, and React.

## Features

- **User Authentication**: Secure login system with JWT tokens and bcrypt password hashing
- **Responsive Design**: Mobile-first approach with 90% width standard containers
- **Modern UI**: Clean gradient-based design system consistent across the application
- **TypeScript**: Full type safety on both frontend and backend

## Tech Stack

### Backend
- Node.js with TypeScript
- Express.js
- PostgreSQL with connection pooling
- JWT for authentication
- bcrypt for password hashing

### Frontend
- React 19 with TypeScript
- Functional components with Hooks
- CSS modules with custom styling
- localStorage for session persistence

## Project Structure

```
tessera-data-app/
├── backend/
│   ├── src/
│   │   ├── config/
│   │   │   └── database.ts
│   │   ├── routes/
│   │   │   └── auth.ts
│   │   └── index.ts
│   ├── schema.sql
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.tsx
│   │   │   └── Login.css
│   │   ├── config/
│   │   │   └── api.ts
│   │   ├── App.tsx
│   │   └── App.css
│   └── package.json
└── README.md
```

## Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- PostgreSQL (v12 or higher)
- npm or yarn

### Database Setup

1. Create a PostgreSQL database:
```bash
createdb tessera_db
```

2. Run the schema file to create tables:
```bash
psql tessera_db < backend/schema.sql
```

3. Create a demo user (you'll need to hash the password first):
```bash
# In Node.js or use an online bcrypt tool
const bcrypt = require('bcryptjs');
bcrypt.hash('password', 10).then(hash => console.log(hash));
```

Then update the INSERT statement in schema.sql with the hashed password.

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Update `.env` with your database credentials:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/tessera_db
JWT_SECRET=your_secure_random_secret_here
NODE_ENV=development
PORT=5001
FRONTEND_URL=http://localhost:3000
```

5. Build and start the server:
```bash
npm run build
npm start
```

For development with auto-reload:
```bash
npm run dev
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

## Demo Credentials

- **Email**: user@example.com
- **Password**: password

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/users` - Get all users

### Health Check
- `GET /api/health` - API and database health check

## Design Standards

### CSS Container Pattern
All main component containers use:
```css
.component-container {
  width: 90%;
  margin: 0 auto;
  padding: 20px;
}
```

### Color Scheme
- Primary gradient: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`
- Background: `#f8f9fa`
- Text: `#333` (primary), `#666` (secondary)

### Component Structure
```typescript
interface ComponentProps {
  // Define all props with types
}

const Component: React.FC<ComponentProps> = ({ prop }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DataType | null>(null);

  // Component logic
};
```

## Development

### Running Tests
```bash
# Backend
cd backend && npm test

# Frontend
cd frontend && npm test
```

### Building for Production
```bash
# Backend
cd backend && npm run build

# Frontend
cd frontend && npm run build
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

ISC
