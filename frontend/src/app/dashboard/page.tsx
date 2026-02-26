'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  BookOpen, 
  Clock, 
  TrendingUp, 
  ChevronRight,
  Flame,
  Calendar,
  Award,
  BookMarked,
  Loader2,
  AlertCircle,
  LogOut,
  User
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import type { Ebook } from '@/types/api';

// Stats interface
interface Stats {
  booksRead: number;
  hoursRead: number;
  currentStreak: number;
  pagesRead: number;
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const [books, setBooks] = useState<Ebook[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Stats - these would come from user data in a real app
  const stats: Stats = {
    booksRead: books.length,
    hoursRead: Math.round(books.length * 6.5),
    currentStreak: 7,
    pagesRead: books.length * 320,
  };

  useEffect(() => {
    // Redirect if not authenticated
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    const fetchBooks = async () => {
      if (!isAuthenticated) return;
      
      try {
        setIsLoading(true);
        setError(null);
        // Fetch user's books
        const response = await api.listMyBooks({ limit: 10 });
        setBooks(response.items);
      } catch (err) {
        console.error('Failed to fetch books:', err);
        setError('Failed to load your books. Please try again.');
        // Use mock data on error for demo purposes
        setBooks([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchBooks();
  }, [isAuthenticated]);

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/auth/login');
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  // Loading state
  if (authLoading || (isLoading && !books.length)) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !books.length) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md p-6">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Something went wrong</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Get user initials for avatar
  const getUserInitials = () => {
    if (user?.full_name) {
      return user.full_name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    }
    if (user?.username) {
      return user.username.slice(0, 2).toUpperCase();
    }
    return 'U';
  };

  // Weekly goal (mock data - would come from user progress data)
  const weeklyGoal = {
    current: 5,
    target: 7,
    books: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    completed: [true, true, true, true, true, false, false] as boolean[],
  };

  // Achievements (mock data - would come from user achievements data)
  const achievements = [
    { icon: Award, label: 'First Book', unlocked: books.length > 0 },
    { icon: Flame, label: '7 Day Streak', unlocked: true },
    { icon: BookMarked, label: 'Weekly Goal', unlocked: weeklyGoal.current >= weeklyGoal.target },
    { icon: BookOpen, label: 'Library Complete', unlocked: false },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Welcome back{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ''}!
              </h1>
              <p className="text-gray-600 mt-1">Continue your reading journey</p>
            </div>
            <div className="flex items-center gap-4">
              <button 
                onClick={handleLogout}
                className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Sign out"
              >
                <LogOut className="w-5 h-5" />
              </button>
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center">
                <span className="text-white font-semibold">{getUserInitials()}</span>
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
          <motion.div
            variants={item}
            className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-primary-500 bg-opacity-10">
                <BookOpen className="w-6 h-6 text-primary-500" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{stats.booksRead}</div>
            <div className="text-sm text-gray-600">Books Read</div>
          </motion.div>

          <motion.div
            variants={item}
            className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-accent-500 bg-opacity-10">
                <Clock className="w-6 h-6 text-accent-500" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{stats.hoursRead}</div>
            <div className="text-sm text-gray-600">Hours Read</div>
          </motion.div>

          <motion.div
            variants={item}
            className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-orange-500 bg-opacity-10">
                <Flame className="w-6 h-6 text-orange-500" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{stats.currentStreak}</div>
            <div className="text-sm text-gray-600">Day Streak</div>
          </motion.div>

          <motion.div
            variants={item}
            className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 rounded-xl bg-green-500 bg-opacity-10">
                <TrendingUp className="w-6 h-6 text-green-500" />
              </div>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">{stats.pagesRead.toLocaleString()}</div>
            <div className="text-sm text-gray-600">Pages Read</div>
          </motion.div>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Continue Reading */}
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
                {books.length > 0 ? (
                  <div className="grid sm:grid-cols-2 gap-6">
                    {books.slice(0, 4).map((book) => (
                      <Link 
                        key={book.id} 
                        href={`/reader?id=${book.id}`}
                        className="group flex gap-4 p-3 rounded-xl hover:bg-gray-50 transition-colors"
                      >
                        <div className="w-20 h-28 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                          {book.cover_image_url ? (
                            <img 
                              src={book.cover_image_url} 
                              alt={book.title}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center bg-primary-100">
                              <BookOpen className="w-8 h-8 text-primary-400" />
                            </div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-gray-900 truncate group-hover:text-primary-600 transition-colors">
                            {book.title}
                          </h3>
                          <p className="text-sm text-gray-600 truncate">{book.author?.full_name || 'Unknown Author'}</p>
                          {book.status !== 'published' && (
                            <span className="inline-block mt-1 px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs rounded-full">
                              {book.status}
                            </span>
                          )}
                        </div>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-600 mb-4">You haven&apos;t added any books yet</p>
                    <Link 
                      href="/library"
                      className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                    >
                      Browse Library
                    </Link>
                  </div>
                )}
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
  );
}
