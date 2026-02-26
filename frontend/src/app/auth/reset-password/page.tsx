'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react'

export default function ResetPasswordPage() {
  const [email, setEmail] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)

  const validateForm = () => {
    const newErrors: Record<string, string> = {}
    
    if (!email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Please enter a valid email'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validateForm()) return
    
    setIsLoading(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))
    setIsLoading(false)
    setIsSubmitted(true)
  }

  if (isSubmitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-accent-50 py-12 px-4">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="relative w-full max-w-md"
        >
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6"
            >
              <CheckCircle className="w-10 h-10 text-green-600" />
            </motion.div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Check your email</h1>
            <p className="text-gray-600 mb-8">
              We&apos;ve sent password reset instructions to <span className="font-medium text-gray-900">{email}</span>
            </p>
            <Link 
              href="/auth/login"
              className="inline-flex items-center justify-center py-3 px-6 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-all"
            >
              Back to Sign In
            </Link>
          </div>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-accent-50 py-12 px-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-accent-200 rounded-full blur-3xl opacity-20" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-primary-200 rounded-full blur-3xl opacity-20" />
      </div>
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative w-full max-w-md"
      >
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <div className="text-center mb-8">
            <Link href="/" className="inline-flex items-center space-x-2 mb-6">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-xl">V</span>
              </div>
            </Link>
            <h1 className="text-2xl font-bold text-gray-900">Reset password</h1>
            <p className="text-gray-600 mt-2">Enter your email and we&apos;ll send you instructions</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value)
                    if (errors.email) setErrors(prev => ({ ...prev, email: '' }))
                  }}
                  className={`w-full pl-10 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all ${errors.email ? 'border-red-500' : 'border-gray-200'}`}
                  placeholder="you@example.com"
                />
              </div>
              {errors.email && <p className="mt-1 text-sm text-red-500">{errors.email}</p>}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center py-3 px-4 bg-primary-600 text-white font-semibold rounded-xl hover:bg-primary-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                'Send Reset Instructions'
              )}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-gray-600">
            Remember your password?{' '}
            <Link href="/auth/login" className="text-primary-600 hover:text-primary-700 font-medium inline-flex items-center">
              <ArrowLeft className="w-4 h-4 mr-1" />
              Sign in
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}
