import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { ApiResponse } from '../models/agent.model';
import { AuthToken, User } from '../models/user.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private http = inject(HttpClient);
  private authUrl = 'http://localhost:8333/api/v1/auth';
  private readonly tokenKey = 'auth_token';

  private currentUser = signal<User | null>(null);
  private initialized = false;

  /** Currently authenticated user (null when logged out). */
  readonly user = this.currentUser.asReadonly();

  /** True when a user is authenticated. */
  readonly isAuthenticated = computed(() => this.currentUser() !== null);

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  setToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
  }

  clearToken(): void {
    localStorage.removeItem(this.tokenKey);
    this.currentUser.set(null);
  }

  register(email: string, username: string, password: string): Observable<ApiResponse<User>> {
    return this.http.post<ApiResponse<User>>(`${this.authUrl}/register`, { email, username, password });
  }

  login(email: string, password: string): Observable<ApiResponse<AuthToken>> {
    return this.http.post<ApiResponse<AuthToken>>(`${this.authUrl}/login`, { email, password }).pipe(
      tap(response => {
        if (response.success && response.data) {
          this.setToken(response.data.access_token);
        }
      })
    );
  }

  getCurrentUser(): Observable<ApiResponse<User>> {
    return this.http.get<ApiResponse<User>>(`${this.authUrl}/me`);
  }

  /** Fetch the current user and update state. Returns null when no valid session. */
  loadCurrentUser(): Observable<User | null> {
    return new Observable<User | null>(observer => {
      const token = this.getToken();
      if (!token) {
        this.currentUser.set(null);
        observer.next(null);
        observer.complete();
        return;
      }
      this.getCurrentUser().subscribe({
        next: (response) => {
          if (response.success && response.data) {
            this.currentUser.set(response.data);
            observer.next(response.data);
          } else {
            this.clearToken();
            observer.next(null);
          }
          observer.complete();
        },
        error: () => {
          this.clearToken();
          observer.next(null);
          observer.complete();
        }
      });
    });
  }

  /** Restore the session from a stored token exactly once per app run. */
  ensureInitialized(): void {
    if (!this.initialized) {
      this.initialized = true;
      this.loadCurrentUser().subscribe();
    }
  }

  /** Clear local session. JWT is stateless; server call is best-effort only. */
  logout(): void {
    this.clearToken();
  }
}
