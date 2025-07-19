import type { Metadata } from 'next'
import './globals.css'
import { ErrorBoundary } from '@/components/error-boundary'
import { ChunkErrorHandler } from '@/components/chunk-error-handler'

export const metadata: Metadata = {
  title: 'RBS Dashboard',
  description: 'RareBet Sports Analytics Dashboard - Check out the latest metrics of your favorite sports betting app!',
  generator: 'Next.js',
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
