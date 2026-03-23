# JobSync Frontend

A modern React + TypeScript frontend for the JobSync job platform.

## Features

- 🔍 Search jobs by title/keywords and location
- 📄 View job listings with pagination
- ✨ Clean, responsive UI with Tailwind CSS
- 🚀 Built with React 18 and TypeScript
- ⚡ Fast development with Vite

## Setup

### Prerequisites
- Node.js 16+ and npm or yarn

### Installation

```bash
# Install dependencies
npm install

# or with yarn
yarn install
```

### Development Server

```bash
# Start the dev server (runs on http://localhost:5173)
npm run dev

# or with yarn
yarn dev
```

The frontend will be available at `http://localhost:5173` and can proxy requests to the API at `http://localhost:8000`.

### Building for Production

```bash
# Build the project
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` or `.env.local` file (optional):

```
REACT_APP_API_URL=http://localhost:8000
```

If not set, defaults to `http://localhost:8000`.

## Project Structure

```
src/
├── api/
│   └── client.ts           # API client and endpoints
├── components/
│   ├── SearchBar.tsx       # Search form
│   ├── JobCard.tsx         # Individual job card display
│   ├── JobList.tsx         # Job list with loading/error states
│   └── Pagination.tsx      # Pagination controls
├── types/
│   └── index.ts            # TypeScript type definitions
├── App.tsx                 # Main app component
├── main.tsx                # Application entry point
└── index.css               # Tailwind CSS setup
```

## API Integration

The frontend communicates with the JobSync API directly:

### Endpoints Used

- `GET /jobs` - List jobs with search and pagination
  - Query params: `q`, `location`, `limit`, `offset`

- `GET /jobs/{job_id}` - Get job details (coming soon)

## Styling

This project uses **Tailwind CSS** for styling. Customize in:
- `tailwind.config.js` - Theme and plugin configuration
- `src/index.css` - Tailwind directives and custom styles

## Development Tips

- Components are located in `src/components/`
- API calls are managed in `src/api/client.ts`
- Type definitions are in `src/types/index.ts`
- Vite HMR (Hot Module Replacement) is enabled for fast development

## Build & Deploy

```bash
# Production build
npm run build

# Output is in the `dist/` folder
```

Deploy the `dist/` folder to your hosting provider (Vercel, Netlify, GitHub Pages, etc.).

## Troubleshooting

### API Connection Issues
- Ensure the backend API is running on `http://localhost:8000`
- Check CORS headers if deployed to different domain
- Verify `REACT_APP_API_URL` environment variable

### Module Import Errors
- Run `npm install` again
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

## Future Enhancements

- [ ] Job detail modal/page
- [ ] Save favorite jobs
- [ ] Job alerts/notifications
- [ ] Dark mode
- [ ] Advanced filtering
- [ ] Company profiles
- [ ] User authentication
