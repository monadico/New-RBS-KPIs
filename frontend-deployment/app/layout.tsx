import type { Metadata } from 'next'
import './globals.css'
import { ErrorBoundary } from '@/components/error-boundary'
import { ChunkErrorHandler } from '@/components/chunk-error-handler'

export const metadata: Metadata = {
  title: 'RBS Dashboard',
  description: 'RareBet Sports Analytics Dashboard - Check out the latest metrics of your favorite sports betting app!',
  generator: 'Next.js',
  applicationName: 'RBS Dashboard',
  keywords: ['RareBet Sports', 'Analytics', 'Dashboard', 'Sports Betting', 'Metrics'],
  authors: [{ name: 'RareBet Sports' }],
  creator: 'RareBet Sports',
  publisher: 'RareBet Sports',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: process.env.NEXT_PUBLIC_SITE_URL || 'https://your-domain.com',
    siteName: 'RBS Dashboard',
    title: 'RBS Dashboard - RareBet Sports Analytics',
    description: 'Check out the latest metrics of your favorite sports betting app!',
    images: [
      {
        url: '/favicon.jpg',
        width: 1200,
        height: 630,
        alt: 'RBS Dashboard - RareBet Sports Analytics',
        type: 'image/jpeg',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    site: '@RareBetSports',
    creator: '@RareBetSports',
    title: 'RBS Dashboard - RareBet Sports Analytics',
    description: 'Check out the latest metrics of your favorite sports betting app!',
    images: ['/favicon.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  icons: {
    icon: [
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/favicon.jpg', type: 'image/jpeg' },
    ],
    apple: { url: '/favicon.jpg', type: 'image/jpeg' },
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/favicon.jpg" type="image/jpeg" />
        <link rel="apple-touch-icon" href="/favicon.jpg" />
        <meta property="og:title" content="RBS Dashboard - RareBet Sports Analytics" />
        <meta property="og:description" content="Check out the latest metrics of your favorite sports betting app!" />
        <meta property="og:image" content="/favicon.jpg" />
        <meta property="og:site_name" content="RBS Dashboard" />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="RBS Dashboard - RareBet Sports Analytics" />
        <meta name="twitter:description" content="Check out the latest metrics of your favorite sports betting app!" />
        <meta name="twitter:image" content="/favicon.jpg" />
        <meta name="application-name" content="RBS Dashboard" />
        <meta name="theme-color" content="#D0FF12" />
        <meta property="og:url" content={process.env.NEXT_PUBLIC_SITE_URL || "https://your-domain.com"} />
        <meta property="og:locale" content="en_US" />
        <meta name="robots" content="index,follow" />
        <meta name="author" content="RareBet Sports" />
      </head>
      <body>
        <ErrorBoundary>
          <ChunkErrorHandler />
          {children}
        </ErrorBoundary>
      </body>
    </html>
  )
}
