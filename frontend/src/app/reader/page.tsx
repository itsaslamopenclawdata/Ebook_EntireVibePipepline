'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ChevronLeft, 
  ChevronRight, 
  Menu, 
  Settings, 
  Sun, 
  Moon, 
  BookOpen,
  Type,
  Maximize2,
  Minimize2,
  X,
  Home,
  Bookmark,
  Search,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import type { Ebook, Chapter, ChapterSummary } from '@/types/api';

type Theme = 'light' | 'dark' | 'sepia';
type ViewMode = 'scroll' | 'paginate';

export default function ReaderPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const bookId = searchParams.get('id');
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  
  // Book state
  const [book, setBook] = useState<Ebook | null>(null);
  const [chapters, setChapters] = useState<ChapterSummary[]>([]);
  const [currentChapterContent, setCurrentChapterContent] = useState<Chapter | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Reader state
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [theme, setTheme] = useState<Theme>('light');
  const [fontSize, setFontSize] = useState(18);
  const [viewMode, setViewMode] = useState<ViewMode>('paginate');
  const [showSettings, setShowSettings] = useState(false);
  const [showToc, setShowToc] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [bookmarks, setBookmarks] = useState<number[]>([]);

  // Fetch book and chapters
  const fetchBookData = useCallback(async () => {
    if (!bookId || !isAuthenticated) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch book details
      const bookData = await api.getBook(bookId);
      setBook(bookData);
      
      // Fetch chapters
      const chaptersData = await api.listChapters(bookId);
      setChapters(chaptersData.items);
      
      // Set total pages (treat each chapter as a "page" for now)
      // In a real app, you'd have actual page breakdowns
      setTotalPages(Math.max(1, chaptersData.items.length));
    } catch (err) {
      console.error('Failed to fetch book:', err);
      setError('Failed to load book. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [bookId, isAuthenticated]);

  useEffect(() => {
    // Redirect if not authenticated
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated && bookId) {
      fetchBookData();
    }
  }, [isAuthenticated, bookId, fetchBookData]);

  const getCurrentChapter = (): ChapterSummary | null => {
    if (chapters.length === 0) return null;
    const index = Math.min(currentPage, chapters.length - 1);
    return chapters[index] || null;
  };

  const currentChapter = getCurrentChapter();

  const goToNextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1);
    }
  };

  const goToPrevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  const toggleBookmark = () => {
    if (bookmarks.includes(currentPage)) {
      setBookmarks(bookmarks.filter(b => b !== currentPage));
    } else {
      setBookmarks([...bookmarks, currentPage]);
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        goToNextPage();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        goToPrevPage();
      } else if (e.key === 'Escape') {
        setShowSettings(false);
        setShowToc(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentPage, totalPages]);

  // Fetch chapter content when page changes
  useEffect(() => {
    const fetchChapterContent = async () => {
      if (!bookId || !currentChapter) {
        setCurrentChapterContent(null);
        return;
      }

      try {
        const chapterData = await api.getChapter(bookId, currentChapter.id);
        setCurrentChapterContent(chapterData);
      } catch (err) {
        console.error('Failed to fetch chapter content:', err);
        // If chapter fetch fails, we'll just show the chapter title
        setCurrentChapterContent(null);
      }
    };

    fetchChapterContent();
  }, [bookId, currentChapter]);

  // Loading state
  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading book...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center max-w-md p-6">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Failed to load book</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={fetchBookData}
              className="px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors"
            >
              Try Again
            </button>
            <Link
              href="/library"
              className="px-6 py-3 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-colors"
            >
              Back to Library
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Book not found
  if (!book) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center max-w-md p-6">
          <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Book not found</h2>
          <p className="text-gray-600 mb-6">This book may have been removed or you don&apos;t have access.</p>
          <Link
            href="/library"
            className="px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors"
          >
            Back to Library
          </Link>
        </div>
      </div>
    );
  }

  const themeClasses: Record<Theme, string> = {
    light: 'bg-white text-gray-900',
    dark: 'bg-gray-900 text-gray-100',
    sepia: 'bg-[#f4ecd8] text-[#5b4636]'
  };

  return (
    <div className={`min-h-screen ${themeClasses[theme]} transition-colors duration-300`}>
      {/* Top Bar */}
      <motion.header 
        initial={{ y: -60 }}
        animate={{ y: 0 }}
        className="fixed top-0 left-0 right-0 z-50 border-b border-gray-200/10 bg-inherit backdrop-blur-md"
      >
        <div className="flex items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <Link href="/library" className="p-2 hover:bg-black/5 rounded-lg transition-colors">
              <Home className="w-5 h-5" />
            </Link>
            <div className="hidden sm:block">
              <h1 className="font-semibold">{book.title}</h1>
              <p className="text-sm opacity-60">{currentChapter?.title || 'Loading...'}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={toggleBookmark}
              className={`p-2 rounded-lg transition-colors ${bookmarks.includes(currentPage) ? 'bg-primary-500 text-white' : 'hover:bg-black/5'}`}
            >
              <Bookmark className="w-5 h-5" fill={bookmarks.includes(currentPage) ? 'currentColor' : 'none'} />
            </button>
            <button 
              onClick={() => setShowToc(!showToc)}
              className="p-2 hover:bg-black/5 rounded-lg transition-colors"
            >
              <Menu className="w-5 h-5" />
            </button>
            <button 
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 hover:bg-black/5 rounded-lg transition-colors"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="pt-20 pb-24 px-4 max-w-3xl mx-auto">
        <motion.div
          key={currentPage}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          className="reader-container"
          style={{ fontSize: `${fontSize}px` }}
        >
          <div className={`prose max-w-none ${viewMode === 'scroll' ? 'leading-relaxed' : 'min-h-[60vh]'}`}>
            {viewMode === 'paginate' ? (
              <div className="whitespace-pre-wrap leading-loose">
                {currentChapterContent?.content || currentChapter?.title || 'No content available'}
              </div>
            ) : (
              <div>
                {chapters.length > 0 ? (
                  chapters.map((ch, idx) => (
                    <div key={ch.id} className="mb-12">
                      <h2 className="text-2xl font-bold mb-4">{ch.title}</h2>
                      <p className="opacity-70">Click to read this chapter...</p>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <BookOpen className="w-16 h-16 mx-auto mb-4 opacity-30" />
                    <p className="opacity-60">No chapters available</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Bottom Navigation */}
      <motion.footer 
        initial={{ y: 60 }}
        animate={{ y: 0 }}
        className="fixed bottom-0 left-0 right-0 z-50 border-t border-gray-200/10 bg-inherit backdrop-blur-md"
      >
        <div className="flex items-center justify-between px-4 py-3 max-w-3xl mx-auto">
          <button 
            onClick={goToPrevPage}
            disabled={currentPage === 0}
            className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-black/5 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
            <span className="hidden sm:inline">Previous</span>
          </button>
          
          <div className="flex items-center gap-2">
            <span className="text-sm">
              Chapter {currentPage + 1} of {totalPages}
            </span>
            <div className="hidden sm:block w-32 h-1.5 bg-gray-200 rounded-full ml-4">
              <div 
                className="h-full bg-primary-500 rounded-full transition-all"
                style={{ width: `${((currentPage + 1) / totalPages) * 100}%` }}
              />
            </div>
          </div>
          
          <button 
            onClick={goToNextPage}
            disabled={currentPage === totalPages - 1}
            className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-black/5 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
          >
            <span className="hidden sm:inline">Next</span>
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      </motion.footer>

      {/* Settings Panel */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 300, opacity: 0 }}
            className={`fixed right-0 top-0 bottom-0 w-80 shadow-xl z-50 p-6 overflow-y-auto ${
              theme === 'dark' ? 'bg-gray-800' : 'bg-white'
            }`}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold">Reader Settings</h2>
              <button onClick={() => setShowSettings(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-6">
              {/* View Mode */}
              <div>
                <label className="block text-sm font-medium mb-3">View Mode</label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setViewMode('paginate')}
                    className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                      viewMode === 'paginate' 
                        ? 'bg-primary-500 text-white' 
                        : 'bg-gray-100 hover:bg-gray-200'
                    }`}
                  >
                    <BookOpen className="w-4 h-4 inline mr-2" />
                    Paginate
                  </button>
                  <button
                    onClick={() => setViewMode('scroll')}
                    className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                      viewMode === 'scroll' 
                        ? 'bg-primary-500 text-white' 
                        : 'bg-gray-100 hover:bg-gray-200'
                    }`}
                  >
                    <Search className="w-4 h-4 inline mr-2" />
                    Scroll
                  </button>
                </div>
              </div>

              {/* Theme */}
              <div>
                <label className="block text-sm font-medium mb-3">Theme</label>
                <div className="flex gap-2">
                  <button
                    onClick={() => setTheme('light')}
                    className={`flex-1 py-3 rounded-lg border-2 transition-colors ${
                      theme === 'light' ? 'border-primary-500 bg-white' : 'border-gray-200'
                    }`}
                  >
                    <Sun className="w-5 h-5 mx-auto" />
                  </button>
                  <button
                    onClick={() => setTheme('sepia')}
                    className={`flex-1 py-3 rounded-lg border-2 transition-colors ${
                      theme === 'sepia' ? 'border-primary-500 bg-[#f4ecd8]' : 'border-gray-200'
                    }`}
                  >
                    <span className="text-2xl">📖</span>
                  </button>
                  <button
                    onClick={() => setTheme('dark')}
                    className={`flex-1 py-3 rounded-lg border-2 transition-colors ${
                      theme === 'dark' ? 'border-primary-500 bg-gray-900' : 'border-gray-200'
                    }`}
                  >
                    <Moon className="w-5 h-5 mx-auto" />
                  </button>
                </div>
              </div>

              {/* Font Size */}
              <div>
                <label className="block text-sm font-medium mb-3">Font Size</label>
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => setFontSize(Math.max(14, fontSize - 2))}
                    className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200"
                  >
                    <Type className="w-4 h-4" />
                  </button>
                  <div className="flex-1 h-2 bg-gray-200 rounded-full">
                    <div 
                      className="h-full bg-primary-500 rounded-full"
                      style={{ width: `${((fontSize - 14) / 20) * 100}%` }}
                    />
                  </div>
                  <button
                    onClick={() => setFontSize(Math.min(32, fontSize + 2))}
                    className="p-2 bg-gray-100 rounded-lg hover:bg-gray-200"
                  >
                    <Type className="w-6 h-6" />
                  </button>
                </div>
                <p className="text-center text-sm mt-2">{fontSize}px</p>
              </div>

              {/* Fullscreen */}
              <button
                onClick={toggleFullscreen}
                className="w-full flex items-center justify-center gap-2 py-3 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
                {isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Table of Contents */}
      <AnimatePresence>
        {showToc && (
          <motion.div
            initial={{ x: -300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            className={`fixed left-0 top-0 bottom-0 w-80 shadow-xl z-50 p-6 overflow-y-auto ${
              theme === 'dark' ? 'bg-gray-800' : 'bg-white'
            }`}
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold">Table of Contents</h2>
              <button onClick={() => setShowToc(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <nav className="space-y-2">
              {chapters.map((ch, idx) => (
                <button
                  key={ch.id}
                  onClick={() => {
                    setCurrentPage(idx);
                    setShowToc(false);
                  }}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    currentPage === idx 
                      ? 'bg-primary-500 text-white' 
                      : 'hover:bg-gray-100'
                  }`}
                >
                  <div className="font-medium">{ch.title}</div>
                  <div className="text-sm opacity-70">Chapter {ch.chapter_number}</div>
                </button>
              ))}
            </nav>

            {chapters.length === 0 && (
              <p className="text-center text-gray-500 py-8">No chapters available</p>
            )}

            {bookmarks.length > 0 && (
              <div className="mt-8">
                <h3 className="text-sm font-medium mb-3 opacity-70">Bookmarks</h3>
                <div className="space-y-2">
                  {bookmarks.map((page) => (
                    <button
                      key={page}
                      onClick={() => {
                        setCurrentPage(page);
                        setShowToc(false);
                      }}
                      className="w-full text-left p-3 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <Bookmark className="w-4 h-4 text-primary-500" fill="currentColor" />
                        <span className="text-sm">Chapter {page + 1}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
