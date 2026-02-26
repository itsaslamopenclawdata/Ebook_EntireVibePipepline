'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  BookOpen, 
  Clock, 
  TrendingUp, 
  Target, 
  ChevronRight,
  Flame,
  Calendar,
  Award,
  BookMarked
} from 'lucide-react'

// Mock data for the dashboard
const stats = [
  { label: 'Books Read', value: 24, icon: BookOpen, change: '+3 this month', color: 'bg-primary-500' },
  { label: 'Hours Read', value: 156, icon: Clock, change: '+12 this week', color: 'bg-accent-500' },
  { label: 'Current Streak', value: 7, icon: Flame, change: 'days', color: 'bg-orange-500' },
  { label: 'Pages Read', value: 8240, icon: TrendingUp, change: '+450 this week', color: 'bg-green-500' },
]

const recentBooks = [
  {
    id: 1,
    title: 'The Art of Programming',
    author: 'John Smith',
    cover: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=200&h=300&fit=crop',
    progress: 75,
    lastRead: '2 hours ago',
  },
  {
    id: 2,
    title: 'Clean Code',
    author: 'Robert Martin',
    cover: 'https://images.unsplash.com/photo-1587620962725-abab7fe55159?w=200&h=300&fit=crop',
    progress: 45,
    lastRead: 'Yesterday',
  },
  {
    id: 3,
    title: 'Design Patterns',
    author: 'Gang of Four',
    cover: 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=200&h=300&fit=crop',
    progress: 20,
    lastRead: '3 days ago',
  },
  {
    id: 4,
    title: 'The Pragmatic Programmer',
    author: 'David Thomas',
    cover: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=200&h=300&fit=crop',
    progress: 100,
    lastRead: '1 week ago',
  },
]

const weeklyGoal = {
  current: 5,
  target: 7,
  books: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  completed: [true, true, true, true, true, false, false],
}

const achievements = [
  { icon: Award, label: 'First Book', unlocked: true },
  { icon: Flame, label: '7 Day Streak', unlocked: true },
  { icon: Target, label: 'Weekly Goal', unlocked: false },
  { icon: BookMarked, label: 'Library Complete', unlocked: false },
]

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Welcome back, Reader!</h1>
              <p className="text-gray-600 mt-1">Continue your reading journey</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors">
                <Calendar className="w-5 h-5" />
              </button>
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold">JD</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <motion.div 
          variants={container}
          initial="hidden"
          animate="show"
          className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8"
        >
          {stats.map((stat) => (
            <motion.div
              key={stat.label}
              variants={item}
              className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl ${stat.color} bg-opacity-10`}>
                  <stat.icon className={`w-6 h-6 ${stat.color.replace('bg-', 'text-')}`} />
                </div>
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</div>
              <div className="text-sm text-gray-600">{stat.label}</div>
              <div className="text-xs text-primary-600 mt-2">{stat.change}</div>
            </motion.div>
          ))}
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Recent Books */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white rounded-2xl border border-gray-100 shadow-sm"
            >
              <div className="flex items-center justify-between p-6 border-b border-gray-100">
                <h2 className="text-lg font-semibold text-gray-900">Continue Reading</h2>
                <Link href="/library" className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center">
                  View All <ChevronRight className="w-4 h-4" />
                </Link>
              </div>
              <div className="p-6">
                <div className="grid sm:grid-cols-2 gap-6">
                  {recentBooks.slice(0, 4).map((book) => (
                    <Link 
                      key={book.id} 
                      href={`/reader?id=${book.id}`}
                      className="group flex gap-4 p-3 rounded-xl hover:bg-gray-50 transition-colors"
                    >
                      <div className="w-20 h-28 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                        <img 
                          src={book.cover} 
                          alt={book.title}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 truncate group-hover:text-primary-600 transition-colors">
                          {book.title}
                        </h3>
                        <p className="text-sm text-gray-600 truncate">{book.author}</p>
                        <div className="mt-3">
                          <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                            <span>Progress</span>
                            <span>{book.progress}%</span>
                          </div>
                          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full transition-all"
                              style={{ width: `${book.progress}%` }}
                            />
                          </div>
                        </div>
                        <p className="text-xs text-gray-400 mt-2">{book.lastRead}</p>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Weekly Goal */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-gray-900">Weekly Goal</h3>
                <span className="text-sm text-gray-600">{weeklyGoal.current}/{weeklyGoal.target} books</span>
              </div>
              <div className="h-3 bg-gray-100 rounded-full overflow-hidden mb-4">
                <div 
                  className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full transition-all"
                  style={{ width: `${(weeklyGoal.current / weeklyGoal.target) * 100}%` }}
                />
              </div>
              <div className="flex justify-between">
                {weeklyGoal.books.map((day, index) => (
                  <div key={day} className="text-center">
                    <div 
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
                        weeklyGoal.completed[index] 
                          ? 'bg-primary-500 text-white' 
                          : 'bg-gray-100 text-gray-500'
                      }`}
                    >
                      {day.charAt(0)}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Achievements */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6"
            >
              <h3 className="font-semibold text-gray-900 mb-4">Achievements</h3>
              <div className="grid grid-cols-2 gap-4">
                {achievements.map((achievement) => (
                  <div 
                    key={achievement.label}
                    className={`p-4 rounded-xl text-center ${
                      achievement.unlocked 
                        ? 'bg-primary-50 border border-primary-100' 
                        : 'bg-gray-50 border border-gray-100 opacity-50'
                    }`}
                  >
                    <achievement.icon className={`w-6 h-6 mx-auto mb-2 ${achievement.unlocked ? 'text-primary-500' : 'text-gray-400'}`} />
                    <p className={`text-xs font-medium ${achievement.unlocked ? 'text-primary-700' : 'text-gray-500'}`}>
                      {achievement.label}
                    </p>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-gradient-to-br from-primary-600 to-accent-600 rounded-2xl p-6 text-white"
            >
              <h3 className="font-semibold mb-2">Ready for more?</h3>
              <p className="text-primary-100 text-sm mb-4">Explore new books and continue your journey</p>
              <Link 
                href="/library"
                className="inline-flex items-center justify-center w-full py-3 bg-white text-primary-600 font-semibold rounded-xl hover:bg-primary-50 transition-colors"
              >
                Browse Library
              </Link>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}
