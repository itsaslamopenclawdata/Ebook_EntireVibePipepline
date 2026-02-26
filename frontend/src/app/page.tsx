'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { BookOpen, Sparkles, Zap, Shield, Globe, Download } from 'lucide-react'

const features = [
  {
    icon: Sparkles,
    title: 'AI-Powered Generation',
    description: 'Create beautiful, professionally structured books with AI-generated content and infographics.'
  },
  {
    icon: BookOpen,
    title: 'Seamless Reading',
    description: 'Enjoy a distraction-free reading experience with customizable themes and fonts.'
  },
  {
    icon: Globe,
    title: 'Cloud Sync',
    description: 'Access your library from any device with automatic synchronization.'
  },
  {
    icon: Shield,
    title: 'Secure & Private',
    description: 'Your data is encrypted and protected with enterprise-grade security.'
  },
  {
    icon: Zap,
    title: 'Instant Export',
    description: 'Download your books in multiple formats including PDF, EPUB, and MOBI.'
  },
  {
    icon: Download,
    title: 'Easy Import',
    description: 'Import existing ebooks or generate new ones from your ideas.'
  }
]

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-primary-50 to-white py-20 sm:py-32">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-accent-200 rounded-full blur-3xl opacity-30 animate-float" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-primary-200 rounded-full blur-3xl opacity-30 animate-float" style={{ animationDelay: '3s' }} />
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-medium mb-6"
            >
              <Sparkles className="w-4 h-4" />
              AI-Powered Book Platform
            </motion.div>
            
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 tracking-tight mb-6">
              <span className="block">Your Reading</span>
              <span className="block bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
                Reimagined
              </span>
            </h1>
            
            <p className="max-w-2xl mx-auto text-xl text-gray-600 mb-10">
              Create, read, and manage your ebook library with the power of AI. 
              Generate professional books, customize your reading experience, 
              and access your library anywhere.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href="/auth/register"
                className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-white bg-primary-600 rounded-xl hover:bg-primary-700 transition-all hover:scale-105 hover:shadow-lg"
              >
                Start Creating Free
                <Zap className="ml-2 w-5 h-5" />
              </Link>
              <Link 
                href="/library"
                className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-gray-700 bg-white border-2 border-gray-200 rounded-xl hover:border-primary-300 hover:bg-primary-50 transition-all"
              >
                Explore Library
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { value: '10K+', label: 'Books Created' },
              { value: '50K+', label: 'Active Readers' },
              { value: '99.9%', label: 'Uptime' },
              { value: '4.9', label: 'User Rating' }
            ].map((stat, index) => (
              <motion.div 
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-4xl font-bold text-primary-600 mb-2">{stat.value}</div>
                <div className="text-gray-600">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Powerful features designed to enhance your reading and writing experience
            </p>
          </motion.div>
          
          <motion.div 
            variants={container}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            className="grid md:grid-cols-2 lg:grid-cols-3 gap-8"
          >
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                variants={item}
                className="bg-white p-8 rounded-2xl shadow-sm hover:shadow-md transition-shadow border border-gray-100"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center mb-6">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-gradient-to-r from-primary-600 to-accent-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold text-white mb-6">
              Ready to Start Your Journey?
            </h2>
            <p className="text-xl text-primary-100 mb-10">
              Join thousands of readers and writers who have transformed their experience with VibeBooks.
            </p>
            <Link 
              href="/auth/register"
              className="inline-flex items-center justify-center px-8 py-4 text-base font-semibold text-primary-600 bg-white rounded-xl hover:bg-gray-50 transition-all hover:scale-105"
            >
              Get Started for Free
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">V</span>
                </div>
                <span className="font-bold text-xl text-white">VibeBooks</span>
              </div>
              <p className="text-sm">
                AI-powered ebook platform for the modern reader.
              </p>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">API</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Blog</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Careers</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><Link href="#" className="hover:text-white transition-colors">Privacy</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Terms</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Security</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-12 pt-8 text-sm text-center">
            © 2026 VibeBooks. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}
