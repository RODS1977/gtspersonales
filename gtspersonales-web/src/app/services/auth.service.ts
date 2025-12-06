import { Injectable } from '@angular/core';
import { Observable, BehaviorSubject } from 'rxjs';
import { tap } from 'rxjs/operators';
import { ApiService } from './api.service';
import { Usuario, LoginRequest, AuthResponse } from '../models/usuario.model';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(private apiService: ApiService) { }

  // Método para registro (Template Driven)
  registrarUsuario(usuario: Usuario): Observable<AuthResponse> {
    return this.apiService.post<AuthResponse>('/auth/registro', usuario, false);
  }

  // Método para registro (Reactive Forms)
  registrarUsuarioModel(usuario: Usuario): Observable<AuthResponse> {
    return this.apiService.post<AuthResponse>('/auth/registro', usuario, false);
  }

  // Método para login
  login(credentials: LoginRequest): Observable<AuthResponse> {
    return this.apiService.post<AuthResponse>('/auth/login', credentials, false)
      .pipe(
        tap(response => {
          if (response.access_token) {
            this.setTokens(response);
            this.isAuthenticatedSubject.next(true);
          }
        })
      );
  }

  // Método para logout
  logout(): Observable<any> {
    return this.apiService.post('/auth/logout', {}).pipe(
      tap(() => {
        this.clearTokens();
        this.isAuthenticatedSubject.next(false);
      })
    );
  }

  // Método para refresh token
  refreshToken(): Observable<AuthResponse> {
    const refreshToken = localStorage.getItem('refresh_token');
    return this.apiService.post<AuthResponse>('/auth/refresh', { refresh_token: refreshToken })
      .pipe(
        tap(response => {
          if (response.access_token) {
            this.setTokens(response);
          }
        })
      );
  }

  // Método para cambiar contraseña
  cambiarPassword(passwordActual: string, nuevaPassword: string): Observable<any> {
    return this.apiService.post('/auth/cambiar-password', {
      password_actual: passwordActual,
      nueva_password: nuevaPassword
    });
  }

  // Métodos auxiliares
  private setTokens(response: AuthResponse): void {
    localStorage.setItem('access_token', response.access_token);
    if (response.refresh_token) {
      localStorage.setItem('refresh_token', response.refresh_token);
    }
  }

  private clearTokens(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  private hasToken(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  isLoggedIn(): boolean {
    return this.hasToken();
  }
}