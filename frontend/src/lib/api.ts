// API Client Service for connecting to the backend

import type {
  User,
  UserCreate,
  UserUpdate,
  LoginRequest,
  TokenResponse,
  RefreshTokenRequest,
  PasswordResetRequest,
  PasswordResetConfirm,
  EmailVerificationConfirm,
  MessageResponse,
  Ebook,
  EbookCreate,
  EbookUpdate,
  EbookListResponse,
  Chapter,
  ChapterCreate,
  ChapterUpdate,
  ChapterListResponse,
  ApiError,
  GenerationRequest,
  GenerationProgress,
  BookFilters,
  PaginationParams,
} from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
      this.refreshToken = localStorage.getItem('refresh_token');
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }
    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }
    if (response.status === 204) {
      return {} as T;
    }
    return response.json();
  }

  // Token Management
  setTokens(accessToken: string, refreshToken: string) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  // Auth API
  async login(credentials: LoginRequest): Promise<TokenResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    return this.handleResponse<TokenResponse>(response);
  }

  async register(userData: UserCreate): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    return this.handleResponse<User>(response);
  }

  async logout(refreshToken: string): Promise<MessageResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    this.clearTokens();
    return this.handleResponse<MessageResponse>(response);
  }

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    const tokens = await this.handleResponse<TokenResponse>(response);
    this.setTokens(tokens.access_token, tokens.refresh_token);
    return tokens;
  }

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<User>(response);
  }

  async requestPasswordReset(data: PasswordResetRequest): Promise<MessageResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/password-reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return this.handleResponse<MessageResponse>(response);
  }

  async confirmPasswordReset(data: PasswordResetConfirm): Promise<MessageResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/password-reset/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return this.handleResponse<MessageResponse>(response);
  }

  async requestEmailVerification(): Promise<MessageResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/verify-email`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    return this.handleResponse<MessageResponse>(response);
  }

  async confirmEmailVerification(data: EmailVerificationConfirm): Promise<MessageResponse> {
    const response = await fetch(`${API_BASE_URL}/auth/verify-email/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return this.handleResponse<MessageResponse>(response);
  }

  // Books API
  async listBooks(params?: PaginationParams & BookFilters): Promise<EbookListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.status) searchParams.set('status', params.status);
    if (params?.genre) searchParams.set('genre', params.genre);
    if (params?.search) searchParams.set('search', params.search);

    const response = await fetch(`${API_BASE_URL}/ebooks?${searchParams.toString()}`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<EbookListResponse>(response);
  }

  async listMyBooks(params?: PaginationParams & { status?: string }): Promise<EbookListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.status) searchParams.set('status', params.status);

    const response = await fetch(`${API_BASE_URL}/ebooks/my?${searchParams.toString()}`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<EbookListResponse>(response);
  }

  async getBook(ebookId: string): Promise<Ebook> {
    const response = await fetch(`${API_BASE_URL}/ebooks/${ebookId}`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<Ebook>(response);
  }

  async createBook(ebookData: EbookCreate): Promise<Ebook> {
    const response = await fetch(`${API_BASE_URL}/ebooks`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(ebookData),
    });
    return this.handleResponse<Ebook>(response);
  }

  async updateBook(ebookId: string, ebookData: EbookUpdate): Promise<Ebook> {
    const response = await fetch(`${API_BASE_URL}/ebooks/${ebookId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(ebookData),
    });
    return this.handleResponse<Ebook>(response);
  }

  async deleteBook(ebookId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/ebooks/${ebookId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    return this.handleResponse<void>(response);
  }

  async publishBook(ebookId: string): Promise<Ebook> {
    const response = await fetch(`${API_BASE_URL}/ebooks/${ebookId}/publish`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    return this.handleResponse<Ebook>(response);
  }

  async archiveBook(ebookId: string): Promise<Ebook> {
    const response = await fetch(`${API_BASE_URL}/ebooks/${ebookId}/archive`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    return this.handleResponse<Ebook>(response);
  }

  // Chapters API
  async listChapters(ebookId: string): Promise<ChapterListResponse> {
    const response = await fetch(`${API_BASE_URL}/ebooks/${ebookId}/chapters`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<ChapterListResponse>(response);
  }

  async getChapter(ebookId: string, chapterId: string): Promise<Chapter> {
    const response = await fetch(`${API_BASE_URL}/ebooks/${ebookId}/chapters/${chapterId}`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<Chapter>(response);
  }

  async createChapter(ebookId: string, chapterData: ChapterCreate): Promise<Chapter> {
    const response = await fetch(`${API_BASE_URL}/ebooks/${ebookId}/chapters`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(chapterData),
    });
    return this.handleResponse<Chapter>(response);
  }

  async updateChapter(ebookId: string, chapterId: string, chapterData: ChapterUpdate): Promise<Chapter> {
    const response = await fetch(`${API_BASE_URL}/ebooks/${ebookId}/chapters/${chapterId}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(chapterData),
    });
    return this.handleResponse<Chapter>(response);
  }

  async deleteChapter(ebookId: string, chapterId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/ebooks/${ebookId}/chapters/${chapterId}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });
    return this.handleResponse<void>(response);
  }

  // Generation API (for future content generation feature)
  async startGeneration(request: GenerationRequest): Promise<GenerationProgress> {
    const response = await fetch(`${API_BASE_URL}/generation/start`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });
    return this.handleResponse<GenerationProgress>(response);
  }

  async getGenerationProgress(jobId: string): Promise<GenerationProgress> {
    const response = await fetch(`${API_BASE_URL}/generation/${jobId}/progress`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<GenerationProgress>(response);
  }

  async cancelGeneration(jobId: string): Promise<MessageResponse> {
    const response = await fetch(`${API_BASE_URL}/generation/${jobId}/cancel`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    return this.handleResponse<MessageResponse>(response);
  }

  async retryGeneration(jobId: string): Promise<GenerationProgress> {
    const response = await fetch(`${API_BASE_URL}/generation/${jobId}/retry`, {
      method: 'POST',
      headers: this.getHeaders(),
    });
    return this.handleResponse<GenerationProgress>(response);
  }

  // User Profile API
  async updateProfile(userData: UserUpdate): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/me`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(userData),
    });
    return this.handleResponse<User>(response);
  }

  async getUserProfile(userId: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse<User>(response);
  }
}

// Export singleton instance
export const api = new ApiClient();
export default api;
