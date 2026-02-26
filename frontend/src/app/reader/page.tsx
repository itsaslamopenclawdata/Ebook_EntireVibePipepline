'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
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
  Search
} from 'lucide-react'

// Mock book content
const bookContent = {
  title: 'The Art of Programming',
  author: 'John Smith',
  chapters: [
    {
      title: 'Chapter 1: Introduction',
      pages: [
        'Welcome to the world of programming. This book will guide you through the fundamental concepts that every developer should know. Programming is not just about writing code; it\'s about solving problems in elegant ways.',
        'Before we dive into the technical aspects, let\'s understand what programming really means. At its core, programming is giving instructions to a computer to perform specific tasks. These instructions, written in programming languages, form the software that powers our digital world.',
        'The journey of learning to program is challenging but rewarding. You\'ll encounter obstacles, debug errors, and experience the joy of seeing your code work. Remember, every expert programmer started as a beginner.',
      ]
    },
    {
      title: 'Chapter 2: Variables and Data Types',
      pages: [
        'Variables are containers for storing data values. Think of them as labeled boxes where you can put information. In most programming languages, you need to declare a variable before using it.',
        'Data types define the kind of data a variable can hold. Common data types include integers (whole numbers), floating-point numbers (decimals), strings (text), and booleans (true/false).',
        'Understanding data types is crucial because it affects how you manipulate and process information. Different operations work with different data types, and understanding this will help you write more efficient code.',
      ]
    },
    {
      title: 'Chapter 3: Control Flow',
      pages: [
        'Control flow determines the order in which statements are executed. The most basic control flow structures are conditional statements, which allow your program to make decisions based on certain conditions.',
        'Loops are another essential control flow mechanism. They allow you to repeat a block of code multiple times, which is essential for processing collections of data or performing repetitive tasks.',
        'Understanding control flow is fundamental to writing dynamic programs that can respond to different inputs and situations. Master these concepts and you\'ll be able to create complex, intelligent applications.',
      ]
    }
  ]
}

type Theme = 'light' | 'dark' | 'sepia'
type ViewMode = 'scroll' | 'paginate'

export default function ReaderPage() {
  const [currentPage, setCurrentPage] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [theme, setTheme] = useState<Theme>('light')
  const [fontSize, setFontSize] = useState(18)
  const [viewMode, setViewMode] = useState<ViewMode>('paginate')
  const [showSettings, setShowSettings] = useState(false)
  const [showToc, setShowToc] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [bookmarks, setBookmarks] = useState<number[]>([])
  const contentRef = useRef<HTMLDivElement>(null)

  // Calculate total pages
  useEffect(() => {
    const pages = bookContent.chapters.reduce((acc, ch) => acc + ch.pages.length, 0)
    setTotalPages(pages)
  }, [])

  const getCurrentChapter = () => {
    let pageCount = 0
    for (const chapter of bookContent.chapters) {
      if (currentPage < pageCount + chapter.pages.length) {
        return { chapter, index: bookContent.chapters.indexOf(chapter) }
      }
      pageCount += chapter.pages.length
    }
    return { chapter: bookContent.chapters[0], index: 0 }
  }

  const { chapter: currentChapter, index: chapterIndex } = getCurrentChapter()
  const chapterStartPage = bookContent.chapters.slice(0, chapterIndex).reduce((acc, ch) => acc + ch.pages.length, 0)
  const pageInChapter = currentPage - chapterStartPage

  const goToNextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1)
    }
  }

  const goToPrevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1)
    }
  }

  const toggleBookmark = () => {
    if (bookmarks.includes(currentPage)) {
      setBookmarks(bookmarks.filter(b => b !== currentPage))
    } else {
      setBookmarks([...bookmarks, currentPage])
    }
  }

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'ArrowRight' || e.key === ' ') {
      goToNextPage()
    } else if (e.key === 'ArrowLeft') {
      goToPrevPage()
    } else if (e.key === 'Escape') {
      setShowSettings(false)
      setShowToc(false)
    }
  }

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [currentPage, totalPages])

  const themeClasses: Record<Theme, string> = {
    light: 'bg-white text-gray-900',
    dark: 'bg-gray-900 text-gray-100',
    sepia: 'reader-container sepia'
  }

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
            <Link href="/dashboard" className="p-2 hover:bg-black/5 rounded-lg transition-colors">
              <Home className="w-5 h-5" />
            </Link>
            <div className="hidden sm:block">
              <h1 className="font-semibold">{bookContent.title}</h1>
              <p className="text-sm opacity-60">{currentChapter.title}</p>
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
          ref={contentRef}
          className="reader-container"
          style={{ fontSize: `${fontSize}px` }}
        >
          <div className={`prose max-w-none ${viewMode === 'scroll' ? 'leading-relaxed' : 'min-h-[60vh]'}`}>
            {viewMode === 'paginate' ? (
              <div className="whitespace-pre-wrap leading-loose">
                {currentChapter.pages[pageInChapter]}
              </div>
            ) : (
              <div>
                {bookContent.chapters.map((ch, idx) => (
                  <div key={idx} className="mb-12">
                    <h2 className="text-2xl font-bold mb-4">{ch.title}</h2>
                    {ch.pages.map((page, pIdx) => (
                      <p key={pIdx} className="mb-4 leading-loose">{page}</p>
                    ))}
                  </div>
                ))}
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
              Page {currentPage + 1} of {totalPages}
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
            className="fixed right-0 top-0 bottom-0 w-80 bg-white dark:bg-gray-800 shadow-xl z-50 p-6 overflow-y-auto"
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
                        : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200'
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
                        : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200'
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
                    className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200"
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
                    className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200"
                  >
                    <Type className="w-6 h-6" />
                  </button>
                </div>
                <p className="text-center text-sm mt-2">{fontSize}px</p>
              </div>

              {/* Fullscreen */}
              <button
                onClick={toggleFullscreen}
                className="w-full flex items-center justify-center gap-2 py-3 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
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
            className="fixed left-0 top-0 bottom-0 w-80 bg-white dark:bg-gray-800 shadow-xl z-50 p-6 overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold">Table of Contents</h2>
              <button onClick={() => setShowToc(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <nav className="space-y-2">
              {bookContent.chapters.map((ch, idx) => {
                const startPage = bookContent.chapters.slice(0, idx).reduce((acc, c) => acc + c.pages.length, 0)
                return (
                  <button
                    key={idx}
                    onClick={() => {
                      setCurrentPage(startPage)
                      setShowToc(false)
                    }}
                    className={`w-full text-left p-3 rounded-lg transition-colors ${
                      chapterIndex === idx 
                        ? 'bg-primary-500 text-white' 
                        : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="font-medium">{ch.title}</div>
                    <div className="text-sm opacity-70">{ch.pages.length} pages</div>
                  </button>
                )
              })}
            </nav>

            {bookmarks.length > 0 && (
              <div className="mt-8">
                <h3 className="text-sm font-medium mb-3 opacity-70">Bookmarks</h3>
                <div className="space-y-2">
                  {bookmarks.map((page) => (
                    <button
                      key={page}
                      onClick={() => {
                        setCurrentPage(page)
                        setShowToc(false)
                      }}
                      className="w-full text-left p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <Bookmark className="w-4 h-4 text-primary-500" fill="currentColor" />
                        <span className="text-sm">Page {page + 1}</span>
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
  )
}
