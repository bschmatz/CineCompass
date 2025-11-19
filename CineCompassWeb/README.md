# CineCompass Web

A modern web application for personalized movie recommendations with a TikTok-style vertical scrolling interface.

## Features

- **Authentication**: Secure login with JWT tokens
- **Onboarding**: Rate popular movies to personalize your experience
- **Home Feed**: Vertical scrolling movie recommendations with:
  - Full-screen movie cards with poster backgrounds
  - Star rating system (0-5 with 0.5 increments)
  - Debounced rating saves
  - Infinite scroll with automatic pagination
  - Pull-to-refresh functionality
  - Expandable movie descriptions
  - Cast and director information
  - Full-screen poster viewing
- **Profile**: User profile with logout functionality
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and optimized builds
- **React Router** for navigation
- **Tailwind CSS** for styling
- **JWT** for authentication

## Getting Started

### Prerequisites

- Node.js 20.17.0 or higher
- npm or yarn

### Installation

1. Navigate to the project directory:
```bash
cd CineCompassWeb
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Building for Production

```bash
npm run build
```

The production-ready files will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Deployment

### Option 1: Static Hosting (Vercel, Netlify, GitHub Pages)

1. Build the project:
```bash
npm run build
```

2. Deploy the `dist` directory to your hosting provider.

**Vercel:**
```bash
npm install -g vercel
vercel --prod
```

**Netlify:**
```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

**GitHub Pages:**
Add to `vite.config.ts`:
```ts
export default defineConfig({
  base: '/your-repo-name/',
  // ... rest of config
})
```

Then build and push the `dist` directory to the `gh-pages` branch.

### Option 2: Docker

Create a `Dockerfile`:
```dockerfile
FROM node:20-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t cinecompass-web .
docker run -p 80:80 cinecompass-web
```

### Option 3: Node.js Server

Install serve:
```bash
npm install -g serve
```

Build and serve:
```bash
npm run build
serve -s dist -p 3000
```

## API Configuration

The app connects to the CineCompass backend at `https://bschmatz.com/cinecompass`.

To change the API URL, edit `src/utils/api.ts`:
```typescript
const API_BASE_URL = 'https://your-api-url.com';
```

## Project Structure

```
src/
├── components/          # Reusable components
│   ├── Layout.tsx      # Bottom navigation layout
│   └── ProtectedRoute.tsx  # Auth guard
├── pages/              # Page components
│   ├── Login.tsx       # Login page
│   ├── Onboarding.tsx  # Movie rating onboarding
│   ├── Home.tsx        # Main recommendation feed
│   └── Profile.tsx     # User profile
├── utils/              # Utilities
│   ├── api.ts         # API client
│   └── auth.ts        # Authentication helpers
├── types.ts           # TypeScript types
├── App.tsx            # Main app with routing
├── main.tsx           # Entry point
└── index.css          # Global styles
```

## Usage

1. **Login**: Enter your credentials (or register a new account via the backend)
2. **Onboarding**: Rate at least 5 popular movies using the heart rating system
3. **Home**: Swipe through personalized movie recommendations
   - Scroll down or use arrow keys to navigate
   - Drag the slider to rate movies (saves automatically after 500ms)
   - Click on posters to view full-screen
   - Click refresh button to reload recommendations
4. **Profile**: View your profile and logout

## Keyboard Shortcuts

- **Arrow Down**: Next movie
- **Arrow Up**: Previous movie
- **Escape**: Close full-screen poster view

## Development

### Code Style

The project uses TypeScript strict mode and follows React best practices:
- Functional components with hooks
- TypeScript interfaces for type safety
- Tailwind CSS for styling
- Custom hooks for reusable logic

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

This is part of the CineCompass project. See the main repository README for contribution guidelines.

## License

Part of the CineCompass project.
