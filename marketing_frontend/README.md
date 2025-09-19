# UnHook Marketing Frontend

A Next.js landing page application for UnHook - a platform for curated daily articles focused on mindful technology use and digital wellness.

## Features

### Pages
- **Landing Page (`/`)**: Features a main article with clear CTA to join the waitlist
- **Dashboard Preview (`/dashboard`)**: Shows a preview of today's articles with teaser content
- **About Page (`/about`)**: Explains the product's purpose and philosophy
- **Waitlist Page (`/waitlist`)**: Simple form to join the waitlist

### Components
- **Header**: Navigation with theme toggle
- **ArticleCard**: Reusable component for displaying articles (featured and preview variants)
- **CTAButton**: Styled call-to-action buttons with multiple variants
- **InfoIcon**: Links to the about page

### Styling & Theming
- **Tailwind CSS**: Modern, utility-first styling
- **Theme Switching**: Toggle between default and Vipassana-inspired themes
- **Responsive Design**: Mobile-first approach with desktop optimizations
- **Dark Mode**: Built-in dark mode support

### API Endpoints
- **`/api/articles/main`**: Returns the featured article for the landing page
- **`/api/newspaper/[id]`**: Returns articles for a specific newspaper (used for dashboard preview)

### Data & Caching
- Mock data for development and testing
- Built-in caching with Next.js revalidation
- Fast loading with optimized API responses

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Available Scripts

- `npm run dev` - Start development server with Turbopack
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── api/               # API routes
│   │   ├── articles/      # Article endpoints
│   │   └── newspaper/     # Newspaper endpoints
│   ├── about/             # About page
│   ├── dashboard/         # Dashboard preview
│   ├── waitlist/          # Waitlist signup
│   ├── layout.tsx         # Root layout with theme provider
│   ├── page.tsx           # Landing page
│   └── globals.css        # Global styles and theme definitions
├── components/            # Reusable React components
│   ├── ArticleCard.tsx    # Article display component
│   ├── CTAButton.tsx      # Call-to-action button
│   ├── Header.tsx         # Navigation header
│   └── InfoIcon.tsx       # Info icon component
├── lib/                   # Utility libraries
│   └── theme-context.tsx  # Theme management context
└── types/                 # TypeScript type definitions
    └── index.ts           # Shared types
```

## Theming

The application supports two themes:

### Default Theme
- Clean, modern design with blue accents
- Standard light/dark mode support

### Vipassana Theme
- Warm, earthy color palette
- Pale yellow background with warm wood tones
- Inspired by mindfulness and meditation practices

Toggle between themes using the theme switcher in the header.

## Customization

### Colors and Typography
- Modify theme colors in `src/app/globals.css`
- Adjust typography using Tailwind classes
- Customize component styles in individual component files

### Content
- Update mock data in API route files
- Modify page content in respective page components
- Customize metadata in `layout.tsx`

### Styling
- All styling uses Tailwind CSS classes
- Custom CSS can be added to `globals.css`
- Component-specific styles are co-located with components

## Deployment

The application is ready for deployment on platforms like:
- Vercel (recommended for Next.js)
- Netlify
- Railway
- Any Node.js hosting platform

Build the application:
```bash
npm run build
```

## Development Notes

- Uses Next.js 15 with App Router
- TypeScript for type safety
- Tailwind CSS v4 for styling
- React 19 for UI components
- Built-in caching and optimization

## Future Enhancements

- Real API integration
- User authentication
- Personalized content recommendations
- Advanced analytics
- Email newsletter integration
- Social sharing features