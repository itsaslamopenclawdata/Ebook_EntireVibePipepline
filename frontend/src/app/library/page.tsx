'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
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
  ChevronDown,
  X,
  Folder,
  Loader2,
  AlertCircle,
  Plus
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import api from '@/lib/api';
import type { Ebook, BookStatus } from '@/types/api';

type ViewMode = 'grid' | 'list';
type SortOption = 'title' | 'author' | 'rating' | 'created_at';

const categories = ['All', 'Technology', 'Psychology', 'Art', 'Fiction', 'Science', 'History'];
const shelves = ['All Books', 'Currently Reading', 'Finished', 'Want to Read'];

export default function LibraryPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedShelf, setSelectedShelf] = useState('All Books');
  const [sortBy, setSortBy] = useState<SortOption>('created_at');
  const [sortAsc, setSortAsc] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [showSortMenu, setShowSortMenu] = useState(false);
  
  // Data state
  const [books, setBooks] = useState<Ebook[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch books
  const fetchBooks = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      setIsLoading(true);
      setError(null);
      
      // Fetch user's books
      const response = await api.listMyBooks({ limit: 100 });
      setBooks(response.items);
    } catch (err) {
      console.error('Failed to fetch books:', err);
      setError('Failed to load books. Please try again.');
      setBooks([]);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    // Redirect if not authenticated
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchBooks();
    }
  }, [isAuthenticated, fetchBooks]);

  // Filter and sort books
  const filteredBooks = books
    .filter(book => {
      const matchesSearch = 
        book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        book.author?.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        book.author?.username?.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === 'All' || book.genre === selectedCategory;
      // Shelf filtering - based on book status
      const matchesShelf = selectedShelf === 'All Books' ||
        (selectedShelf === 'Currently Reading' && book.status === 'draft') ||
        (selectedShelf === 'Finished' && book.status === 'published') ||
        (selectedShelf === 'Want to Read' && book.status === 'draft');
      return matchesSearch && matchesCategory && matchesShelf;
    })
    .sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'title':
          comparison = a.title.localeCompare(b.title);
          break;
        case 'author':
          comparison = (a.author?.full_name || '').localeCompare(b.author?.full_name || '');
          break;
        case 'rating':
          comparison = b.rating_average - a.rating_average;
          break;
        case 'created_at':
          comparison = new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
          break;
      }
      return sortAsc ? -comparison : comparison;
    });

  const getSortLabel = () => {
    switch (sortBy) {
      case 'title': return 'Title';
      case 'author': return 'Author';
      case 'rating': return 'Rating';
      case 'created_at': return 'Date Added';
    }
  };

  // Loading state
  if (authLoading || (isLoading && !books.length)) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin text-primary-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading your library...</p>
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
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Failed to load library</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={fetchBooks}
            className="px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
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
                    {(['title', 'author', 'rating', 'created_at'] as SortOption[]).map((option) => (
                      <button
                        key={option}
                        onClick={() => {
                          if (sortBy === option) {
                            setSortAsc(!sortAsc);
                          } else {
                            setSortBy(option);
                            setSortAsc(false);
                          }
                          setShowSortMenu(false);
                        }}
                        className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-50 ${
                          sortBy === option ? 'text-primary-600 font-medium' : 'text-gray-700'
                        }`}
                      >
                        {option === 'title' && 'Title'}
                        {option === 'author' && 'Author'}
                        {option === 'rating' && 'Rating'}
                        {option === 'created_at' && 'Date Added'}
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
                  setSelectedShelf('All Books');
                  setSelectedCategory('All');
                  setSearchQuery('');
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
          Showing {filteredBooks.length} of {books.length} books
        </div>

        {filteredBooks.length === 0 ? (
          <div className="text-center py-16">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No books found</h3>
            <p className="text-gray-600 mb-6">Try adjusting your filters or search query</p>
            <Link
              href="/library"
              className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add New Book
            </Link>
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
                    {book.cover_image_url ? (
                      <img
                        src={book.cover_image_url}
                        alt={book.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center">
                        <BookOpen className="w-12 h-12 text-white/80" />
                      </div>
                    )}
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button className="p-2 bg-white/90 rounded-lg shadow-sm hover:bg-white">
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                    {book.status === 'draft' && (
                      <div className="absolute bottom-0 left-0 right-0 py-1 bg-yellow-500/90 text-white text-xs text-center">
                        Draft
                      </div>
                    )}
                  </div>
                </Link>
                <h3 className="font-semibold text-gray-900 truncate group-hover:text-primary-600 transition-colors">
                  {book.title}
                </h3>
                <p className="text-sm text-gray-600 truncate">{book.author?.full_name || book.author?.username || 'Unknown Author'}</p>
                <div className="flex items-center gap-2 mt-1">
                  <div className="flex items-center">
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <span className="text-sm ml-1">{book.rating_average > 0 ? book.rating_average.toFixed(1) : 'N/A'}</span>
                  </div>
                  {book.genre && (
                    <>
                      <span className="text-gray-300">•</span>
                      <span className="text-sm text-gray-500">{book.genre}</span>
                    </>
                  )}
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
                    {book.cover_image_url ? (
                      <img
                        src={book.cover_image_url}
                        alt={book.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-primary-400 to-accent-400 flex items-center justify-center">
                        <BookOpen className="w-8 h-8 text-white/80" />
                      </div>
                    )}
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
                      <p className="text-sm text-gray-600">{book.author?.full_name || book.author?.username || 'Unknown Author'}</p>
                    </div>
                    <button className="p-2 hover:bg-gray-100 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreVertical className="w-5 h-5 text-gray-500" />
                    </button>
                  </div>
                  <div className="flex items-center gap-4 mt-3">
                    <div className="flex items-center">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-sm ml-1">{book.rating_average > 0 ? book.rating_average.toFixed(1) : 'N/A'}</span>
                    </div>
                    {book.genre && (
                      <span className="px-2 py-1 bg-gray-100 rounded-full text-xs text-gray-600">
                        {book.genre}
                      </span>
                    )}
                    <span className="flex items-center text-sm text-gray-500">
                      <Clock className="w-4 h-4 mr-1" />
                      {new Date(book.created_at).toLocaleDateString()}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      book.status === 'published' 
                        ? 'bg-green-100 text-green-700' 
                        : book.status === 'draft'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {book.status}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  );
}
