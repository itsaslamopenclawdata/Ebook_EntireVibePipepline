// API Types for the Ebook Platform

// User Types
export interface User {
  id: string;
  email: string;
  username?: string;
  full_name?: string;
  avatar_url?: string;
  bio?: string;
  profile_visibility: 'public' | 'private' | 'friends';
  is_active: boolean;
  is_verified: boolean;
  is_superuser: boolean;
  created_at: string;
  last_login?: string;
}

export interface UserCreate {
  email: string;
  password: string;
  username?: string;
  full_name?: string;
}

export interface UserUpdate {
  full_name?: string;
  username?: string;
  bio?: string;
  avatar_url?: string;
  profile_visibility?: 'public' | 'private' | 'friends';
}

// Auth Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export interface EmailVerificationConfirm {
  token: string;
}

export interface MessageResponse {
  message: string;
}

// Book Types
export type BookStatus = 'draft' | 'published' | 'archived';

export interface Ebook {
  id: string;
  author_id: string;
  title: string;
  description?: string;
  cover_image_url?: string;
  status: BookStatus;
  content?: string;
  genre?: string;
  tags: string[];
  version: number;
  view_count: number;
  download_count: number;
  rating_average: number;
  rating_count: number;
  created_at: string;
  updated_at: string;
  published_at?: string;
  author?: UserPublic;
}

export interface EbookCreate {
  title: string;
  description?: string;
  cover_image_url?: string;
  content?: string;
  genre?: string;
  tags?: string[];
}

export interface EbookUpdate {
  title?: string;
  description?: string;
  cover_image_url?: string;
  content?: string;
  genre?: string;
  tags?: string[];
  status?: BookStatus;
}

export interface EbookListResponse {
  items: Ebook[];
  total: number;
  skip: number;
  limit: number;
}

// Chapter Types
export interface Chapter {
  id: string;
  ebook_id: string;
  chapter_number: number;
  title: string;
  content?: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface ChapterCreate {
  chapter_number: number;
  title: string;
  content?: string;
}

export interface ChapterUpdate {
  title?: string;
  content?: string;
}

export interface ChapterListResponse {
  items: ChapterSummary[];
  total: number;
}

export interface ChapterSummary {
  id: string;
  chapter_number: number;
  title: string;
  version: number;
  created_at: string;
  updated_at: string;
}

// Public user response (limited fields)
export interface UserPublic {
  id: string;
  username?: string;
  full_name?: string;
  avatar_url?: string;
  bio?: string;
  profile_visibility: 'public' | 'private' | 'friends';
  created_at: string;
}

// API Error
export interface ApiError {
  detail: string;
}

// Generation Types (for future content generation feature)
export interface GenerationRequest {
  title: string;
  genre?: string;
  prompt?: string;
  chapter_count?: number;
}

export interface GenerationProgress {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message?: string;
  result?: Ebook;
}

// Pagination params
export interface PaginationParams {
  skip?: number;
  limit?: number;
}

// Filter params
export interface BookFilters {
  status?: BookStatus;
  genre?: string;
  search?: string;
}
