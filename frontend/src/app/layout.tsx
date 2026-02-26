import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'VibeBooks - Your Digital Reading Companion',
  description: 'AI-powered ebook platform for reading, managing, and generating books',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <Link href="/" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">V</span>
                </div>
                <span className="font-bold text-xl text-gray-900">VibeBooks</span>
              </Link>
              <div className="flex items-center space-x-4">
                <Link href="/library" className="text-gray-600 hover:text-primary-600 transition-colors">
                  Library
                </Link>
                <Link href="/dashboard" className="text-gray-600 hover:text-primary-600 transition-colors">
                  Dashboard
                </Link>
                <Link 
                  href="/auth/login" 
                  className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-primary-600 transition-colors"
                >
                  Sign In
                </Link>
                <Link 
                  href="/auth/register" 
                  className="px-4 py-2 text-sm font-medium bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                >
                  Get Started
                </Link>
              </div>
            </div>
          </div>
        </nav>
        <main className="pt-16">
          {children}
        </main>
      </body>
    </html>
  )
}
