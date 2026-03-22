This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

### 1. Environment variables

Copy the example env file and set required values:

```bash
cp .env.example .env
```

Edit `.env` and set at least:

- **`USER_SERVICE_URL`** – Base URL of the user service (e.g. `http://localhost:8000`). Required for user categories and related APIs. Start the user service from the repo root (`user_service/`) if running locally.
- **`NEWSPAPER_SERVICE_URL`** – Base URL of the newspaper service.

Optional (if API routes use MongoDB):

- **`MONGODB_URI`** – MongoDB connection string  
- **`DATABASE_NAME`** – Database name (e.g. `youtube_newspaper`)

### 2. Run the development server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

