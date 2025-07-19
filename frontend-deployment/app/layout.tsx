import type { Metadata } from 'next'
import './globals.css'
import { ChunkErrorHandler } from '@/components/chunk-error-handler'

export const metadata: Metadata = {
  title: 'v0 App',
  description: 'Created with v0',
  generator: 'v0.dev',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>
        <ChunkErrorHandler />
        {children}
      </body>
    </html>
  )
}
