# 🎯 Ratowanie 100 - Frontend

Production-grade React + TypeScript frontend for qualified sports betting matches.

## 🚀 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Super fast build tool
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - High-quality components
- **React Query** - Data fetching & caching
- **Zustand** - State management
- **React Router** - Navigation
- **Lucide Icons** - Beautiful icons

## 📦 Installation

```bash
cd frontend
npm install
```

## 🛠️ Development

```bash
# Start dev server (http://localhost:3000)
npm run dev

# Backend API proxy configured to http://localhost:5000/api
```

## 🏗️ Build for Production

```bash
# TypeScript compilation + Vite build
npm run build

# Output: ../public/ (served by Express backend)
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable components
│   │   ├── ui/           # shadcn/ui base components
│   │   ├── layout/       # Header, Navigation, Layout
│   │   ├── MatchCard.tsx
│   │   ├── FilterBar.tsx
│   │   └── ...
│   ├── pages/            # Route pages
│   │   ├── Dashboard.tsx
│   │   ├── MatchesList.tsx
│   │   └── ...
│   ├── hooks/            # Custom hooks
│   │   └── useApi.ts
│   ├── lib/              # Utilities
│   │   ├── api.ts        # Axios client
│   │   └── utils.ts      # Helper functions
│   ├── store/            # Zustand stores
│   │   └── filterStore.ts
│   ├── types/            # TypeScript types
│   │   └── index.ts
│   ├── App.tsx           # Root component
│   ├── main.tsx          # Entry point
│   └── index.css         # Global styles
├── public/               # Static assets
├── index.html            # HTML shell
├── vite.config.ts        # Vite configuration
├── tailwind.config.js    # Tailwind configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies

```

## 🎨 Features

### ✅ Implemented
- Responsive design (mobile-first)
- Dark/light mode support (Tailwind variables)
- Real-time data fetching with React Query
- Persistent filters with Zustand + localStorage
- Beautiful glassmorphism UI
- Sport-specific badges and colors
- Bookmaker odds display (Fortuna/Superbet/STS)
- Pagination with smooth scrolling
- Loading states and error handling
- Type-safe API calls

### 🔜 Coming Soon (Later)
- Supabase Authentication
- Stripe Payment Integration
- User Dashboard
- Match Detail Pages
- Email Subscription Management
- Favorite Matches
- Push Notifications

## 🔌 API Integration

Frontend proxies all `/api/*` requests to backend server:

```typescript
// Vite proxy configuration (vite.config.ts)
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
  },
}
```

## 🎯 Component Library

Using **shadcn/ui** components:
- Button
- Card
- Badge
- Dialog
- Select
- Tabs
- And more...

## 📱 Responsive Breakpoints

```css
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
2xl: 1536px /* Extra large */
```

## 🎨 Color Palette

```
Primary: Purple (#667eea - #764ba2)
Sport Football: Blue (#e3f2fd / #1565c0)
Sport Volleyball: Orange (#fff3e0 / #e65100)
Sport Handball: Pink (#fce4ec / #c2185b)
Fortuna: Red (#dc2626)
Superbet: Blue (#2563eb)
STS: Green (#16a34a)
```

## 🔧 Environment Variables

```bash
# Backend API URL (auto-proxied in dev)
VITE_API_URL=http://localhost:5000/api
```

## 📄 License

MIT
