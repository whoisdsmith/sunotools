# SUNOSAVE

Save lyrics and prompts for SUNO.AI

## SUNOSAVE Project Overview

This project, named "SUNOSAVE," is a web application designed to save lyrics and prompts, likely intended for use with SUNO.AI. It's built using a modern tech stack, including React for the frontend, Express for the backend, and Prisma ORM for database interaction with PostgreSQL. The project utilizes Vite for fast development builds and hot module replacement, and Tailwind CSS (with daisyUI components) for styling.

**Key Features:**

- **Frontend (Client):**
  - React (v18.3.1) with TypeScript for a robust, type-safe UI.
  - Vite (v6.0.5) for fast development builds and hot reloading.
  - Tailwind CSS (v3.4.17) with daisyUI (v4.12.23) and `@tailwindcss/typography` (v0.5.16) for styling.
  - React Router (v7.1.4) for navigation.
  - Redux Toolkit (v2.5.1) and `react-redux` (v9.2.0) for state management.
  - Firebase (v11.3.0) for authentication (Google Sign-In).
  - Apollo Client (v3.13.1) for interacting with the GraphQL API.
  - Form for creating lyrics.
  - List views for displaying lyrics and prompts.
  - `react-helmet-async` for managing document head tags (SEO).
  - `react-icons` for UI icons.
  - ESLint and Prettier configured for code quality and formatting.
  - Cypress for end-to-end testing.
  - Renovate for automated dependency updates.

- **Backend (Server):** (Information inferred from the project structure and client-side code.)
  - Express.js (implied by usage of proxy configuration in `vite.config.ts` and `.gitignore`)
  - GraphQL API (served at `/graphql`, uses Apollo Server)
  - Prisma ORM for database interactions.
  - PostgreSQL database (managed via `docker-compose.yml`).

- **Data Model (Inferred):**
  - `Lyrics`: Contains an `id`, `userId`, `lyrics` text, `createdAt`, `updatedAt`, and related `prompts`.
  - `Prompts`: Contains an `id`, `genre`, and `prompt` text.
  - `User` (Inferred): Likely includes `id`, `email`, and `name` managed by Firebase auth and potentially extended/synced with a database.

- **Authentication:**
  - Firebase Authentication with Google Sign-In.
  - User data (UID, email, display name, photo URL) is stored in the Redux store.
  - Firebase user ID is used as a bearer token for authorization with the GraphQL API.

- **Development Workflow:**
  - `npm run dev` (client): Starts the Vite development server.
  - `npm run build` (client): Builds the production-ready client application.
  - `npm run lint` (client): Runs ESLint for code quality checks.
  - `npm run preview` (client): Serves a preview of the built application.
  - `npm run test` (client): Opens Cypress for end-to-end testing.
  - Server-side scripts (inferred from `package.json` in the root folder and README):
    - `npm run generate`: Generates the Prisma client.
    - `npm run migrate`: Applies Prisma database migrations.
    - `npm run studio`: Opens Prisma Studio for database management.
    - `npm run start`: Starts the Express server.
  - Database is managed using Docker Compose.

- **Environment Variables (Client):**
  - `VITE_SERVICE_NAME`: The name of the application.
  - `VITE_FIREBASE_APIKEY`, `VITE_FIREBASE_AUTHDOMAIN`, `VITE_FIREBASE_DATABASEURL`, `VITE_FIREBASE_PROJECTID`, `VITE_FIREBASE_STORAGEBUCKET`, `VITE_FIREBASE_MESSAGINGSENDERID`, `VITE_FIREBASE_APPID`, `VITE_FIREBASE_MEASUREMENTID`: Firebase configuration settings.
  - `VITE_GRAPHQL_URL`: The URL of the GraphQL API endpoint.

**Setup Process (Summary):**

1. **Database:** Start the PostgreSQL container using `docker-compose up -d`.
2. **Server:**
    - Navigate to the `server` directory (not included in the provided files, but mentioned in README).
    - Install dependencies (`npm install`).
    - Configure environment variables (copy `.env.example` to `.env`).
    - Generate Prisma client (`npm run generate`).
    - Run migrations (`npm run migrate`).
    - Seed the database (optional) (`npx prisma db seed`)
    - Start the server (`npm run start`).
3. **Client:**
    - Navigate to the `client` directory.
    - Install dependencies (`npm install`).
    - Configure environment variables (copy `.env.local.example` to `.env.local` and fill in Firebase credentials).
    - Start the development server (`npm run dev`).

**Key Improvements & Considerations:**

- **Type Safety:** Extensive use of TypeScript throughout the project enhances code quality and maintainability.
- **Modern Frontend:** Utilizes React 18 with functional components and hooks.  Vite provides a fast and efficient development experience.
- **State Management:** Redux Toolkit simplifies state management, including handling authentication status.
- **Firebase Integration:**  Provides a quick and easy way to implement user authentication. The code handles user synchronization with the backend.
- **GraphQL API:** The use of GraphQL allows for efficient data fetching and avoids over-fetching.  The client uses Apollo Client.
- **UI Components:**  daisyUI offers pre-built Tailwind CSS components, accelerating UI development.
- **Testing** Includes configurations for Eslint, Prettier, and Cypress, indicating a focus on maintainable and tested code.
- **Docker Compose:** Simplifies database setup and management.
- **Error Handling:** The `CreateLyricsForm` component includes basic error handling for the mutation. The `AuthInitializer` handles errors that occur while attempting to upsert the user.
- **Code Splitting (Lazy Loading):**  The components are lazy-loaded using `React.lazy` and `Suspense`, which improves initial load time by only loading components when they are needed.

**Possible Enhancements/Missing Pieces (Based on provided files):**

- **Server-Side Code:** The provided file paths and content _only_ cover the client-side.  The server-side code (Express, Prisma schema, resolvers) is not included, so a complete understanding of the backend is not possible.
- **Detailed Error Handling:** While basic error handling is present, more robust error handling and user feedback (e.g., displaying user-friendly error messages) could be added throughout the application.
- **Form Validation:** Client-side and server-side validation should be implemented for the "Create Lyrics" form.
- **Data Persistence:**  While there are queries and mutations for lyrics and prompts, the provided code snippets don't show how other data (songs, artwork) is managed.  Presumably, there are additional GraphQL queries and mutations, and corresponding database models, to handle those.
- **UI/UX:** The provided UI is fairly basic.  More polish and user experience improvements could be added.
- **Security:** Consider implementing more robust security measures, such as input sanitization, CSRF protection, and secure storage of sensitive data.  While Firebase handles authentication, authorization (who can access what data/operations) on the backend needs to be carefully implemented.
- **Testing:**  While Cypress is set up, no actual test files are provided.  Adding comprehensive tests (unit, integration, and end-to-end) is crucial for a production-ready application.
- **Deployment:** The README doesn't include deployment instructions.  A deployment strategy (e.g., to platforms like Netlify, Vercel, Heroku, or a cloud provider) would be necessary.

Overall, this project provides a solid foundation for a web application using a popular and effective tech stack.  It demonstrates good practices like type safety, component-based architecture, state management, and authentication. However, it's more of a starting point/prototype and needs further development in terms of server-side implementation, error handling, security, testing, and deployment to be considered a fully functional, production-ready application.

---

## Prerequisites

- Node.js
- Docker Desktop
- npm or yarn

## Project Structure

## Features

- Save prompts
- Save lyrics

## Views

- Dashboard
- Save prompt form

## Form

- Title - _required_
- Prompt - _required_
- Lyrics - _optional_

## Data

```
const SUNOSAVE = {
  id: number,
  title: string,
  prompt: string,
  lyrics: string,
  date: date,
}
```

## Tech Stack

- Prisma ORM
- Postgres

- React
- Express

## Setup Instructions

1. Start the Database:

```bash
# Start PostgreSQL container
docker-compose up -d
```

2. Server Setup:

```bash
# Navigate to server directory
cd server

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Generate Prisma client
npm run generate

# Run database migrations
npm run migrate

# Seed the database with initial data
npx prisma db seed

# Start the server
npm run start
```

3. Client Setup:

```bash
# In a new terminal, navigate to client directory
cd client

# Install dependencies
npm install

# Start the development server
npm run dev
```

## Available Scripts

### Server

- `npm run generate` - Generate Prisma client
- `npm run migrate` - Run database migrations
- `npm run studio` - Open Prisma Studio
- `npm run start` - Start the server

### Client

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## GraphQL API

The GraphQL playground is available at `http://localhost:3000/graphql` when the server is running.

## Database Management

- Prisma Studio: `http://localhost:5555` (run `npm run studio` in server directory)
- PostgreSQL Database: `localhost:5432`
