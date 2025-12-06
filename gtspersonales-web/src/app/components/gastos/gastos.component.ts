import { Component, OnInit, ViewChild, TemplateRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { GastosService } from '../../services/gastos.service';
import { CategoriasService } from '../../services/categorias.service';
import { Gasto, GastoCreate } from '../../models/gasto.model';
import { Categoria } from '../../models/categoria.model';

@Component({
  selector: 'app-gastos',
  templateUrl: './gastos.component.html',
  styleUrls: ['./gastos.component.css']
})
export class GastosComponent implements OnInit {
  @ViewChild('modalGasto') modalGasto!: TemplateRef<any>;
  @ViewChild('modalConfirmacion') modalConfirmacion!: TemplateRef<any>;

  gastos: Gasto[] = [];
  categorias: Categoria[] = [];
  gastoForm: FormGroup;
  filtroForm: FormGroup;
  
  modoEdicion = false;
  gastoSeleccionado: Gasto | null = null;
  gastoAEliminar: Gasto | null = null;
  
  isLoading = false;
  errorMessage = '';
  successMessage = '';
  
  // Paginación
  paginaActual = 1;
  itemsPorPagina = 10;
  totalItems = 0;

  constructor(
    private fb: FormBuilder,
    private modalService: NgbModal,
    private gastosService: GastosService,
    private categoriasService: CategoriasService
  ) {
    // Formulario para gastos
    this.gastoForm = this.fb.group({
      categoria_id: ['', Validators.required],
      monto: ['', [Validators.required, Validators.min(0.01)]],
      fecha: ['', Validators.required],
      descripcion: ['', [Validators.required, Validators.minLength(3)]]
    });

    // Formulario para filtros
    this.filtroForm = this.fb.group({
      categoria_id: [''],
      fecha_inicio: [''],
      fecha_fin: [''],
      descripcion: ['']
    });
  }

  ngOnInit(): void {
    this.cargarCategorias();
    this.cargarGastos();
  }

  cargarCategorias(): void {
    this.categoriasService.getCategorias().subscribe({
      next: (categorias) => {
        this.categorias = categorias;
      },
      error: (error) => {
        console.error('Error al cargar categorías:', error);
        this.errorMessage = 'Error al cargar categorías';
      }
    });
  }

  cargarGastos(): void {
    this.isLoading = true;
    this.gastosService.getGastos().subscribe({
      next: (gastos) => {
        this.gastos = gastos;
        this.totalItems = gastos.length;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar gastos:', error);
        this.errorMessage = 'Error al cargar gastos';
        this.isLoading = false;
      }
    });
  }

  aplicarFiltros(): void {
    const filtros = this.filtroForm.value;
    this.isLoading = true;

    // Si hay fechas, usar filtro por fecha
    if (filtros.fecha_inicio && filtros.fecha_fin) {
      this.gastosService.getGastosPorFecha(
        filtros.fecha_inicio,
        filtros.fecha_fin
      ).subscribe({
        next: (gastos) => {
          this.gastos = this.filtrarGastos(gastos, filtros);
          this.totalItems = this.gastos.length;
          this.paginaActual = 1;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al filtrar gastos:', error);
          this.errorMessage = 'Error al aplicar filtros';
          this.isLoading = false;
        }
      });
    } else {
      // Filtrar localmente
      this.gastosService.getGastos().subscribe({
        next: (gastos) => {
          this.gastos = this.filtrarGastos(gastos, filtros);
          this.totalItems = this.gastos.length;
          this.paginaActual = 1;
          this.isLoading = false;
        },
        error: (error) => {
          console.error('Error al cargar gastos:', error);
          this.errorMessage = 'Error al cargar gastos';
          this.isLoading = false;
        }
      });
    }
  }

  limpiarFiltros(): void {
    this.filtroForm.reset();
    this.cargarGastos();
  }

  private filtrarGastos(gastos: Gasto[], filtros: any): Gasto[] {
    return gastos.filter(gasto => {
      // Filtrar por categoría
      if (filtros.categoria_id && gasto.categoria_id !== parseInt(filtros.categoria_id)) {
        return false;
      }

      // Filtrar por descripción
      if (filtros.descripcion && 
          !gasto.descripcion.toLowerCase().includes(filtros.descripcion.toLowerCase())) {
        return false;
      }

      return true;
    });
  }

  abrirModalNuevoGasto(): void {
    this.modoEdicion = false;
    this.gastoSeleccionado = null;
    this.gastoForm.reset();
    this.gastoForm.patchValue({
      fecha: new Date().toISOString().split('T')[0] // Fecha actual
    });
    this.modalService.open(this.modalGasto, { size: 'lg' });
  }

  abrirModalEditarGasto(gasto: Gasto): void {
    this.modoEdicion = true;
    this.gastoSeleccionado = { ...gasto };
    
    // Convertir fecha al formato YYYY-MM-DD para el input date
    const fecha = new Date(gasto.fecha);
    const fechaFormateada = fecha.toISOString().split('T')[0];
    
    this.gastoForm.patchValue({
      categoria_id: gasto.categoria_id,
      monto: gasto.monto,
      fecha: fechaFormateada,
      descripcion: gasto.descripcion
    });
    
    this.modalService.open(this.modalGasto, { size: 'lg' });
  }

  guardarGasto(): void {
    if (this.gastoForm.invalid) {
      this.marcarControlesComoTouched(this.gastoForm);
      return;
    }

    const gastoData: GastoCreate = this.gastoForm.value;
    this.isLoading = true;

    if (this.modoEdicion && this.gastoSeleccionado?.id) {
      // Actualizar gasto existente
      this.gastosService.updateGasto(this.gastoSeleccionado.id, gastoData).subscribe({
        next: (gastoActualizado) => {
          const index = this.gastos.findIndex(g => g.id === gastoActualizado.id);
          if (index !== -1) {
            this.gastos[index] = gastoActualizado;
          }
          this.successMessage = 'Gasto actualizado exitosamente';
          this.modalService.dismissAll();
          this.isLoading = false;
          setTimeout(() => this.successMessage = '', 3000);
        },
        error: (error) => {
          console.error('Error al actualizar gasto:', error);
          this.errorMessage = 'Error al actualizar gasto';
          this.isLoading = false;
        }
      });
    } else {
      // Crear nuevo gasto
      this.gastosService.createGasto(gastoData).subscribe({
        next: (nuevoGasto) => {
          this.gastos.unshift(nuevoGasto);
          this.totalItems = this.gastos.length;
          this.successMessage = 'Gasto creado exitosamente';
          this.modalService.dismissAll();
          this.isLoading = false;
          setTimeout(() => this.successMessage = '', 3000);
        },
        error: (error) => {
          console.error('Error al crear gasto:', error);
          this.errorMessage = 'Error al crear gasto';
          this.isLoading = false;
        }
      });
    }
  }

  confirmarEliminarGasto(gasto: Gasto): void {
    this.gastoAEliminar = gasto;
    this.modalService.open(this.modalConfirmacion);
  }

  eliminarGasto(): void {
    if (!this.gastoAEliminar?.id) return;

    this.isLoading = true;
    this.gastosService.deleteGasto(this.gastoAEliminar.id).subscribe({
      next: () => {
        this.gastos = this.gastos.filter(g => g.id !== this.gastoAEliminar?.id);
        this.totalItems = this.gastos.length;
        this.successMessage = 'Gasto eliminado exitosamente';
        this.modalService.dismissAll();
        this.gastoAEliminar = null;
        this.isLoading = false;
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        console.error('Error al eliminar gasto:', error);
        this.errorMessage = 'Error al eliminar gasto';
        this.modalService.dismissAll();
        this.isLoading = false;
      }
    });
  }

  obtenerNombreCategoria(categoriaId: number): string {
    const categoria = this.categorias.find(c => c.id === categoriaId);
    return categoria ? categoria.nombre : 'Desconocida';
  }

  formatearMoneda(monto: number): string {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(monto);
  }

  formatearFecha(fecha: string | Date): string {
    const date = new Date(fecha);
    return date.toLocaleDateString('es-MX', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }

  get gastosPaginados(): Gasto[] {
    const inicio = (this.paginaActual - 1) * this.itemsPorPagina;
    const fin = inicio + this.itemsPorPagina;
    return this.gastos.slice(inicio, fin);
  }

  cambiarPagina(pagina: number): void {
    this.paginaActual = pagina;
  }

  private marcarControlesComoTouched(formGroup: FormGroup): void {
    Object.values(formGroup.controls).forEach(control => {
      control.markAsTouched();
      if (control instanceof FormGroup) {
        this.marcarControlesComoTouched(control);
      }
    });
  }

  // Getters para validación del formulario
  get categoria_id() { return this.gastoForm.get('categoria_id'); }
  get monto() { return this.gastoForm.get('monto'); }
  get fecha() { return this.gastoForm.get('fecha'); }
  get descripcion() { return this.gastoForm.get('descripcion'); }

  getPaginas(): number[] {
  const totalPaginas = this.getTotalPaginas();
  const paginas: number[] = [];
  
  let inicio = Math.max(1, this.paginaActual - 2);
  let fin = Math.min(totalPaginas, inicio + 4);
  
  if (fin - inicio < 4) {
    inicio = Math.max(1, fin - 4);
  }
  
  for (let i = inicio; i <= fin; i++) {
    paginas.push(i);
  }
  
  return paginas;
}

getTotalPaginas(): number {
  return Math.ceil(this.totalItems / this.itemsPorPagina);
}
}