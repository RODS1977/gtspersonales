import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:5000'; // Ajusta según tu puerto Flask

  constructor(private http: HttpClient) { }

  private getHeaders(includeAuth: boolean = true): HttpHeaders {
    let headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    });

    if (includeAuth) {
      const token = localStorage.getItem('access_token');
      if (token) {
        headers = headers.set('Authorization', `Bearer ${token}`);
      }
    }

    return headers;
  }

  get<T>(endpoint: string, includeAuth: boolean = true): Observable<T> {
    return this.http.get<T>(`${this.apiUrl}${endpoint}`, {
      headers: this.getHeaders(includeAuth)
    }).pipe(
      catchError(this.handleError)
    );
  }

  post<T>(endpoint: string, data: any, includeAuth: boolean = true): Observable<T> {
    return this.http.post<T>(`${this.apiUrl}${endpoint}`, data, {
      headers: this.getHeaders(includeAuth)
    }).pipe(
      catchError(this.handleError)
    );
  }

  put<T>(endpoint: string, data: any, includeAuth: boolean = true): Observable<T> {
    return this.http.put<T>(`${this.apiUrl}${endpoint}`, data, {
      headers: this.getHeaders(includeAuth)
    }).pipe(
      catchError(this.handleError)
    );
  }

  delete<T>(endpoint: string, includeAuth: boolean = true): Observable<T> {
    return this.http.delete<T>(`${this.apiUrl}${endpoint}`, {
      headers: this.getHeaders(includeAuth)
    }).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'Error desconocido';
    
    if (error.error instanceof ErrorEvent) {
      // Error del lado del cliente
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Error del servidor
      if (error.status === 401) {
        errorMessage = 'No autorizado. Por favor, inicie sesión nuevamente.';
        // Opcional: redirigir al login
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      } else if (error.status === 400) {
        errorMessage = error.error?.message || 'Datos inválidos';
      } else if (error.status === 404) {
        errorMessage = 'Recurso no encontrado';
      } else if (error.status === 500) {
        errorMessage = 'Error interno del servidor';
      }
    }
    
    console.error(errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}