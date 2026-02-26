'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  Filter, 
  Grid, 
  List, 
  SortAsc, 
  SortDesc,
  BookOpen,
  Clock,
  Star,
  MoreVertical,
  Trash2,
  Edit,
  Download,
  ChevronDown,
  X,
  Folder
} from 'lucide-react'

// Mock books data
const allBooks = [
  {
    id: 1,
    title: 'The Art of Programming',
    author: 'John Smith',
    cover: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=300&h=400&fit=crop',
    category: 'Technology',
    rating: 4.8,
    progress: 75,
    lastRead: '2 hours ago',
    addedDate: '2026-01-15',
  },
  {
    id: 2,
    title: 'Clean Code',
    author: 'Robert Martin',
    cover: 'https://images.unsplash.com/photo-1587620962725-abab7fe55159?w=300&h=400&fit=crop',
    category: 'Technology',
    rating: 4.9,
    progress: 45,
    lastRead: 'Yesterday',
    addedDate: '2026-01-10',
  },
  {
    id: 3,
    title: 'Design Patterns',
    author: 'Gang of Four',
    cover: 'https://images.unsplash.com/photo-1532012197267-da84d127e765?w=300&h=400&fit=crop',
    category: 'Technology',
    rating: 4.7,
    progress: 20,
    lastRead: '3 days ago',
    addedDate: '2026-01-08',
  },
  {
    id: 4,
    title: 'The Pragmatic Programmer',
    author: 'David Thomas',
    cover: 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=300&h=400&fit=crop',
    category: 'Technology',
    rating: 4.6,
    progress: 100,
    lastRead: '1 week ago',
    addedDate: '2026-01-05',
  },
  {
    id: 5,
    title: 'Introduction to Psychology',
    author: 'James Kalat',
    cover: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=400&fit=crop',
    category: 'Psychology',
    rating: 4.5,
    progress: 0,
    lastRead: 'Never',
    addedDate: '2026-02-01',
  },
  {
    id: 6,
    title: 'Thinking, Fast and Slow',
    author: 'Daniel Kahneman',
    cover: 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=300&h=400&fit=crop',
    category: 'Psychology',
    rating: 4.9,
    progress: 30,
    lastRead: '5 days ago',
    addedDate: '2026-01-20',
  },
  {
    id: 7,
    title: 'History of Modern Art',
    author: 'H.H. Arnason',
    cover: 'https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=300&h=400&fit=crop',
    category: 'Art',
    rating: 4.4,
    progress: 0,
    lastRead: 'Never',
    addedDate: '2026-02-10',
  },
  {
    id: 8,
    title: 'The Great Gatsby',
    author: 'F. Scott Fitzgerald',
    cover: 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=300&h=400&fit=crop',
    category: 'Fiction',
    rating: 4.7,
    progress: 60,
    lastRead: '1 day ago',
    addedDate: '2026-01-25',
  },
]

const categories = ['All', 'Technology', 'Psychology', 'Art', 'Fiction']
const shelves = ['All Books', 'Currently Reading', 'Finished', 'Want to Read']

type ViewMode = 'grid' | 'list'
type SortOption = 'title' | 'author' | 'rating' | 'lastRead' | 'addedDate'

export default function LibraryPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [selectedShelf, setSelectedShelf] = useState('All Books')
  const [sortBy, setSortBy] = useState<SortOption>('lastRead')
  const [sortAsc, setSortAsc] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [showSortMenu, setShowSortMenu] = useState(false)

  const filteredBooks = allBooks
    .filter(book => {
      const matchesSearch = book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        book.author.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesCategory = selectedCategory === 'All' || book.category === selectedCategory
      const matchesShelf = selectedShelf === 'All Books' ||
        (selectedShelf === 'Currently Reading' && book.progress > 0 && book.progress < 100) ||
        (selectedShelf === 'Finished' && book.progress === 100) ||
        (selectedShelf === 'Want to Read' && book.progress === 0)
      return matchesSearch && matchesCategory && matchesShelf
    })
    .sort((a, b) => {
      let comparison = 0
      switch (sortBy) {
        case 'title':
          comparison = a.title.localeCompare(b.title)
          break
        case 'author':
          comparison = a.author.localeCompare(b.author)
          break
        case 'rating':
          comparison = b.rating - a.rating
          break
        case 'lastRead':
          comparison = a.lastRead.localeCompare(b.lastRead)
          break
        case 'addedDate':
          comparison = new Date(b.addedDate).getTime() - new Date(a.addedDate).getTime()
          break
      }
      return sortAsc ? comparison : -comparison
    })

  const getSortLabel = () => {
    switch (sortBy) {
      case 'title': return 'Title'
      case 'author': return 'Author'
      case 'rating': return 'Rating'
      case 'lastRead': return 'Last Read'
      case 'addedDate': return 'Date Added'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-900">My Library</h1>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-lg transition-colors ${viewMode === 'grid' ? 'bg-primary-100 text-primary-600' : 'hover:bg-gray-100'}`}
              >
                <Grid className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-lg transition-colors ${viewMode === 'list' ? 'bg-primary-100 text-primary-600' : 'hover:bg-gray-100'}`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Search Bar */}
          <div className="flex gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search books by title or author..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-200 rounded-full"
                >
                  <X className="w-4 h-4 text-gray-500" />
                </button>
              )}
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl border transition-colors ${
                showFilters ? 'bg-primary-50 border-primary-200 text-primary-600' : 'bg-white border-gray-200 hover:bg-gray-50'
              }`}
            >
              <Filter className="w-5 h-5" />
              <span className="hidden sm:inline">Filters</span>
            </button>
            <div className="relative">
              <button
                onClick={() => setShowSortMenu(!showSortMenu)}
                className="flex items-center gap-2 px-4 py-3 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
              >
                {sortAsc ? <SortAsc className="w-5 h-5" /> : <SortDesc className="w-5 h-5" />}
                <span className="hidden sm:inline">{getSortLabel()}</span>
                <ChevronDown className="w-4 h-4" />
              </button>
              <AnimatePresence>
                {showSortMenu && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-10"
                  >
                    {(['title', 'author', 'rating', 'lastRead', 'addedDate'] as SortOption[]).map((option) => (
                      <button
                        key={option}
                        onClick={() => {
                          if (sortBy === option) {
                            setSortAsc(!sortAsc)
                          } else {
                            setSortBy(option)
                            setSortAsc(false)
                          }
                          setShowSortMenu(false)
                        }}
                        className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-50 ${
                          sortBy === option ? 'text-primary-600 font-medium' : 'text-gray-700'
                        }`}
                      >
                        {option === 'title' && 'Title'}
                        {option === 'author' && 'Author'}
                        {option === 'rating' && 'Rating'}
                        {option === 'lastRead' && 'Last Read'}
                        {option === 'addedDate' && 'Date Added'}
                        {sortBy === option && (
                          <span className="ml-2">{sortAsc ? '↑' : '↓'}</span>
                        )}
                      </button>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Filters Panel */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="pb-6 space-y-4">
                  {/* Shelves */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Shelves</label>
                    <div className="flex flex-wrap gap-2">
                      {shelves.map((shelf) => (
                        <button
                          key={shelf}
                          onClick={() => setSelectedShelf(shelf)}
                          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                            selectedShelf === shelf
                              ? 'bg-primary-500 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          <Folder className="w-4 h-4 inline mr-2" />
                          {shelf}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Categories */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Categories</label>
                    <div className="flex flex-wrap gap-2">
                      {categories.map((category) => (
                        <button
                          key={category}
                          onClick={() => setSelectedCategory(category)}
                          className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                            selectedCategory === category
                              ? 'bg-accent-500 text-white'
                              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                          }`}
                        >
                          {category}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Active Filters */}
          {(selectedShelf !== 'All Books' || selectedCategory !== 'All' || searchQuery) && (
            <div className="flex flex-wrap items-center gap-2 pb-6">
              <span className="text-sm text-gray-500">Active filters:</span>
              {searchQuery && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                  Search: {searchQuery}
                  <button onClick={() => setSearchQuery('')}>
                    <X className="w-3 h-3" />
                  </button>
                </span>
              )}
              {selectedShelf !== 'All Books' && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                  {selectedShelf}
                  <button onClick={() => setSelectedShelf('All Books')}>
                    <X className="w-3 h-3" />
                  </button>
                </span>
              )}
              {selectedCategory !== 'All' && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-accent-100 text-accent-700 rounded-full text-sm">
                  {selectedCategory}
                  <button onClick={() => setSelectedCategory('All')}>
                    <X className="w-3 h-3" />
                  </button>
                </span>
              )}
              <button
                onClick={() => {
                  setSelectedShelf('All Books')
                  setSelectedCategory('All')
                  setSearchQuery('')
                }}
                className="text-sm text-gray-500 hover:text-gray-700 underline"
              >
                Clear all
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-4 text-sm text-gray-500">
          Showing {filteredBooks.length} of {allBooks.length} books
        </div>

        {filteredBooks.length === 0 ? (
          <div className="text-center py-16">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No books found</h3>
            <p className="text-gray-600">Try adjusting your filters or search query</p>
          </div>
        ) : viewMode === 'grid' ? (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6"
          >
            {filteredBooks.map((book) => (
              <motion.div
                key={book.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="group"
              >
                <Link href={`/reader?id=${book.id}`}>
                  <div className="relative aspect-[3/4] rounded-xl overflow-hidden mb-3 shadow-sm group-hover:shadow-md transition-shadow">
                    <img
                      src={book.cover}
                      alt={book.title}
                      className="w-full h-full object-cover"
                    />
                    {book.progress > 0 && (
                      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-200">
                        <div
                          className="h-full bg-primary-500"
                          style={{ width: `${book.progress}%` }}
                        />
                      </div>
                    )}
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="p-2 bg-white/90 rounded-lg shadow-sm hover:bg-white">
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </Link>
                <h3 className="font-semibold text-gray-900 truncate group-hover:text-primary-600 transition-colors">
                  {book.title}
                </h3>
                <p className="text-sm text-gray-600 truncate">{book.author}</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex items-center">
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <span className="text-sm ml-1">{book.rating}</span>
                  </div>
                  <span className="text-gray-300">•</span>
                  <span className="text-sm text-gray-500">{book.category}</span>
                </div>
              </motion.div>
            ))}
          </motion.div>
        ) : (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            {filteredBooks.map((book) => (
              <motion.div
                key={book.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="group flex gap-4 p-4 bg-white rounded-xl border border-gray-100 hover:shadow-md transition-all"
              >
                <Link href={`/reader?id=${book.id}`}>
                  <div className="w-20 h-28 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                    <img
                      src={book.cover}
                      alt={book.title}
                      className="w-full h-full object-cover"
                    />
                  </div>
                </Link>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div>
                      <Link href={`/reader?id=${book.id}`}>
                        <h3 className="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                          {book.title}
                        </h3>
                      </Link>
                      <p className="text-sm text-gray-600">{book.author}</p>
                    </div>
                    <button className="p-2 hover:bg-gray-100 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreVertical className="w-5 h-5 text-gray-500" />
                    </button>
                  </div>
                  <div className="flex items-center gap-4 mt-3">
                    <div className="flex items-center">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-sm ml-1">{book.rating}</span>
                    </div>
                    <span className="px-2 py-1 bg-gray-100 rounded-full text-xs text-gray-600">
                      {book.category}
                    </span>
                    <span className="flex items-center text-sm text-gray-500">
                      <Clock className="w-4 h-4 mr-1" />
                      {book.lastRead}
                    </span>
                  </div>
                  {book.progress > 0 && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                        <span>Progress</span>
                        <span>{book.progress}%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-primary-500 to-accent-500 rounded-full"
                          style={{ width: `${book.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  )
}
