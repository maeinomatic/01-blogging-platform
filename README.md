# Blogging Platform

A full-stack blogging application with user authentication, rich text editor, comments, and search functionality.

## Features

- User Authentication (JWT)
- Create, Read, Update, Delete blog posts
- Rich text editor (TinyMCE/Slate)
- Comments system
- Search and filtering
- User profiles
- Like/bookmark posts

## Tech Stack

- **Frontend:** React, Tailwind CSS
- **Backend:** Node.js, Express
- **Database:** MongoDB
- **Authentication:** JWT
- **Editor:** React-Quill or TinyMCE

## Project Structure

```
├── client/              # React frontend
├── server/              # Express backend
├── README.md
└── package.json
```

## Getting Started

### Prerequisites
- Node.js 16+
- MongoDB

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env` file in server folder:
   ```
   MONGODB_URI=your_mongo_uri
   JWT_SECRET=your_jwt_secret
   PORT=5000
   ```

4. Run development server:
   ```bash
   npm run dev
   ```

## API Endpoints

- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `GET /api/posts` - Get all posts
- `POST /api/posts` - Create post
- `GET /api/posts/:id` - Get single post
- `PUT /api/posts/:id` - Update post
- `DELETE /api/posts/:id` - Delete post
- `POST /api/posts/:id/comments` - Add comment

## Deployment

- Frontend: Vercel
- Backend: Heroku/Railway

## License

MIT
