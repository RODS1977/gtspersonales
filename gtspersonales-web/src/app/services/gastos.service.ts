import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Gasto, GastoCreate } from '../models/gasto.model';

@Injectable({
  providedIn: 'root'
})
export class GastosService {
  private endpoint = '/api/gastos'; // Ajusta según tu endpoint

  constructor(private apiService: ApiService) { }

  // Obtener todos los gastos
  getGastos(): Observable<Gasto[]> {
    return this.apiService.get<Gasto[]>(this.endpoint);
  }

  // Obtener gasto por ID
  getGasto(id: number): Observable<Gasto> {
    return this.apiService.get<Gasto>(`${this.endpoint}/${id}`);
  }

  // Crear nuevo gasto
  createGasto(gasto: GastoCreate): Observable<Gasto> {
    return this.apiService.post<Gasto>(this.endpoint, gasto);
  }

  // Actualizar gasto
  updateGasto(id: number, gasto: GastoCreate): Observable<Gasto> {
    return this.apiService.put<Gasto>(`${this.endpoint}/${id}`, gasto);
  }

  // Eliminar gasto
  deleteGasto(id: number): Observable<any> {
    return this.apiService.delete(`${this.endpoint}/${id}`);
  }

  // Obtener gastos por rango de fechas
  getGastosPorFecha(fechaInicio: string, fechaFin: string): Observable<Gasto[]> {
    return this.apiService.get<Gasto[]>(`${this.endpoint}/filtrar?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`);
  }

  // Obtener gastos por categoría
  getGastosPorCategoria(categoriaId: number): Observable<Gasto[]> {
    return this.apiService.get<Gasto[]>(`${this.endpoint}/categoria/${categoriaId}`);
  }
}