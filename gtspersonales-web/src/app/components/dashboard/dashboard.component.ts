import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  userName = 'Usuario'; // Esto debería venir del servicio de autenticación
  currentDate = new Date();
  
  // Datos de ejemplo para estadísticas
  estadisticas = {
    totalGastos: 0,
    gastosMes: 0,
    gastosHoy: 0,
    categoriaMasUsada: 'Sin datos'
  };

  // Últimos gastos (ejemplo)
  ultimosGastos: any[] = [
    // Se poblará con datos reales desde el backend
  ];

  constructor() { }

  ngOnInit(): void {
    this.loadDashboardData();
  }

  loadDashboardData(): void {
    // Aquí cargarás los datos reales desde los servicios
    // Por ahora usamos datos de ejemplo
    this.estadisticas = {
      totalGastos: 12500.75,
      gastosMes: 4500.25,
      gastosHoy: 125.50,
      categoriaMasUsada: 'Comida'
    };

    this.ultimosGastos = [
      { descripcion: 'Supermercado', monto: 125.50, fecha: '2024-01-15', categoria: 'Comida' },
      { descripcion: 'Gasolina', monto: 500.00, fecha: '2024-01-14', categoria: 'Transporte' },
      { descripcion: 'Netflix', monto: 199.00, fecha: '2024-01-13', categoria: 'Entretenimiento' }
    ];
  }

  // Método para formatear moneda
  formatCurrency(value: number): string {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(value);
  }
}