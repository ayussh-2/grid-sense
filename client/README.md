# GridSense AI - Client

Modern Professional SaaS dashboard for real-time grid power monitoring and analysis.

## Features

- **Real-time Monitoring**: Live data streaming at 1Hz from connected devices
- **KPI Metrics**: Total current, power, voltage, and cost estimation
- **Live Charts**: Beautiful area charts showing current over time
- **Device Control**: Turn devices on/off directly from the dashboard
- **AI Insights**: Real-time analysis and recommendations
- **Professional Design**: Clean, matte, modern dark mode interface

## Tech Stack

- **Next.js 16** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS 4** - Utility-first styling
- **Recharts** - Data visualization
- **Lucide Icons** - Beautiful icon set
- **Biome** - Fast linter and formatter

## Design System

This project follows a "Modern Professional SaaS" design schema inspired by platforms like Vercel, Stripe, and Linear. Key principles:

- **Information First**: Data is the hero, no decorative elements
- **Matte over Glossy**: Flat surfaces with subtle borders
- **Slate Color Scale**: Professional industrial tone
- **Typography**: Inter for text, JetBrains Mono for data values

See `DESIGN_SCHEMA.md` for full design specifications.

## Getting Started

### Prerequisites

- Node.js 20+ installed
- GridSense API server running (default: `http://localhost:8000`)

### Installation

1. Install dependencies:

```bash
npm install
```

2. Configure environment variables:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` if your API server is running on a different URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:

```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── (home)/            # Dashboard page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/
│   ├── dashboard/         # Dashboard-specific components
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── MetricsGrid.tsx
│   │   ├── LiveChart.tsx
│   │   ├── DeviceTable.tsx
│   │   └── AIPanel.tsx
│   ├── typography/        # Typography components
│   │   ├── Heading.tsx
│   │   ├── Label.tsx
│   │   ├── Value.tsx
│   │   └── Body.tsx
│   └── ui/               # Base UI components
│       ├── Card.tsx
│       ├── Badge.tsx
│       └── Button.tsx
├── lib/
│   └── api/              # API client and types
│       ├── client.ts
│       ├── types.ts
│       └── index.ts
└── fonts/                # Font configuration
    └── index.ts
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run Biome linter
- `npm run format` - Format code with Biome

## API Integration

The dashboard connects to the GridSense API server for:

- **Live Data**: Polls `/api/live` every 1 second for device telemetry
- **Grid Context**: Polls `/api/grid` every 15 minutes for pricing and carbon data
- **Device Control**: POST requests to `/api/devices/{id}/control/{action}`

## Components

### Typography Components

- `Heading` - Semantic headings (h1-h4)
- `Label` - Uppercase labels for metrics
- `Value` - Monospace numbers with emphasis
- `Body` - Regular body text

### UI Components

- `Card` - Base container with optional critical styling
- `Badge` - Status indicators (success, warning, critical)
- `Button` - Action buttons with variants

### Dashboard Components

- `Sidebar` - Navigation sidebar with logo
- `Header` - Top bar with system status and time
- `MetricsGrid` - Grid of KPI metric cards
- `LiveChart` - Real-time area chart
- `DeviceTable` - Interactive device list with controls
- `AIPanel` - AI insights and recommendations

## Styling

Custom utility classes (defined in `globals.css`):

- `.card-base` - Base card styling
- `.text-label` - Label text styling
- `.value-mono` - Monospace value styling

## Development

The dashboard automatically:
- Fetches live data every second
- Updates charts in real-time
- Detects critical conditions (high current, faults)
- Switches to critical mode with red highlighting
- Handles device control actions

## Production Build

```bash
npm run build
npm run start
```

The production build is optimized and ready for deployment.

## License

Part of the GridSense AI project.
