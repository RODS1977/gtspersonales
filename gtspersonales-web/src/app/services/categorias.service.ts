import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Categoria } from '../models/categoria.model';

@Injectable({
  providedIn: 'root'
})
export class CategoriasService {
  private endpoint = '/api/categorias'; // Ajusta según tu endpoint

  constructor(private apiService: ApiService) { }

  // Obtener todas las categorías
  getCategorias(): Observable<Categoria[]> {
    return this.apiService.get<Categoria[]>(this.endpoint);
  }

  // Obtener categoría por ID
  getCategoria(id: number): Observable<Categoria> {
    return this.apiService.get<Categoria>(`${this.endpoint}/${id}`);
  }

  // Crear nueva categoría
  createCategoria(categoria: Categoria): Observable<Categoria> {
    return this.apiService.post<Categoria>(this.endpoint, categoria);
  }

  // Actualizar categoría
  updateCategoria(id: number, categoria: Categoria): Observable<Categoria> {
    return this.apiService.put<Categoria>(`${this.endpoint}/${id}`, categoria);
  }

  // Eliminar categoría
  deleteCategoria(id: number): Observable<any> {
    return this.apiService.delete(`${this.endpoint}/${id}`);
  }
}