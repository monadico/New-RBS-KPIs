import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'RareBetSports Analytics Dashboard',
  description: 'Check out the latest metrics of your favorite sports betting app!',
  generator: 'RareBetSports',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
