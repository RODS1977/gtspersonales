import { Component, OnInit, ViewChild, TemplateRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { CategoriasService } from '../../services/categorias.service';
import { Categoria } from '../../models/categoria.model';

@Component({
  selector: 'app-categorias',
  templateUrl: './categorias.component.html',
  styleUrls: ['./categorias.component.css']
})
export class CategoriasComponent implements OnInit {
  @ViewChild('modalCategoria') modalCategoria!: TemplateRef<any>;
  @ViewChild('modalConfirmacion') modalConfirmacion!: TemplateRef<any>;

  categorias: Categoria[] = [];
  categoriaForm: FormGroup;
  
  modoEdicion = false;
  categoriaSeleccionada: Categoria | null = null;
  categoriaAEliminar: Categoria | null = null;
  
  isLoading = false;
  errorMessage = '';
  successMessage = '';

  constructor(
    private fb: FormBuilder,
    private modalService: NgbModal,
    private categoriasService: CategoriasService
  ) {
    this.categoriaForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      descripcion: ['', [Validators.required, Validators.minLength(5)]]
    });
  }

  ngOnInit(): void {
    this.cargarCategorias();
  }

  cargarCategorias(): void {
    this.isLoading = true;
    this.categoriasService.getCategorias().subscribe({
      next: (categorias) => {
        this.categorias = categorias;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar categorías:', error);
        this.errorMessage = 'Error al cargar categorías';
        this.isLoading = false;
      }
    });
  }

  abrirModalNuevaCategoria(): void {
    this.modoEdicion = false;
    this.categoriaSeleccionada = null;
    this.categoriaForm.reset();
    this.modalService.open(this.modalCategoria, { size: 'md' });
  }

  abrirModalEditarCategoria(categoria: Categoria): void {
    this.modoEdicion = true;
    this.categoriaSeleccionada = { ...categoria };
    this.categoriaForm.patchValue({
      nombre: categoria.nombre,
      descripcion: categoria.descripcion
    });
    this.modalService.open(this.modalCategoria, { size: 'md' });
  }

  guardarCategoria(): void {
    if (this.categoriaForm.invalid) {
      this.marcarControlesComoTouched(this.categoriaForm);
      return;
    }

    const categoriaData: Categoria = this.categoriaForm.value;
    this.isLoading = true;

    if (this.modoEdicion && this.categoriaSeleccionada?.id) {
      // Actualizar categoría existente
      this.categoriasService.updateCategoria(this.categoriaSeleccionada.id, categoriaData).subscribe({
        next: (categoriaActualizada) => {
          const index = this.categorias.findIndex(c => c.id === categoriaActualizada.id);
          if (index !== -1) {
            this.categorias[index] = categoriaActualizada;
          }
          this.successMessage = 'Categoría actualizada exitosamente';
          this.modalService.dismissAll();
          this.isLoading = false;
          setTimeout(() => this.successMessage = '', 3000);
        },
        error: (error) => {
          console.error('Error al actualizar categoría:', error);
          this.errorMessage = 'Error al actualizar categoría';
          this.isLoading = false;
        }
      });
    } else {
      // Crear nueva categoría
      this.categoriasService.createCategoria(categoriaData).subscribe({
        next: (nuevaCategoria) => {
          this.categorias.push(nuevaCategoria);
          this.successMessage = 'Categoría creada exitosamente';
          this.modalService.dismissAll();
          this.isLoading = false;
          setTimeout(() => this.successMessage = '', 3000);
        },
        error: (error) => {
          console.error('Error al crear categoría:', error);
          this.errorMessage = 'Error al crear categoría';
          this.isLoading = false;
        }
      });
    }
  }

  confirmarEliminarCategoria(categoria: Categoria): void {
    this.categoriaAEliminar = categoria;
    this.modalService.open(this.modalConfirmacion);
  }

  eliminarCategoria(): void {
    if (!this.categoriaAEliminar?.id) return;

    this.isLoading = true;
    this.categoriasService.deleteCategoria(this.categoriaAEliminar.id).subscribe({
      next: () => {
        this.categorias = this.categorias.filter(c => c.id !== this.categoriaAEliminar?.id);
        this.successMessage = 'Categoría eliminada exitosamente';
        this.modalService.dismissAll();
        this.categoriaAEliminar = null;
        this.isLoading = false;
        setTimeout(() => this.successMessage = '', 3000);
      },
      error: (error) => {
        console.error('Error al eliminar categoría:', error);
        this.errorMessage = 'Error al eliminar categoría';
        this.modalService.dismissAll();
        this.isLoading = false;
      }
    });
  }

  formatearFecha(fecha: string | Date | undefined): string {
    if (!fecha) return 'N/A';
    const date = new Date(fecha);
    return date.toLocaleDateString('es-MX', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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
  get nombre() { return this.categoriaForm.get('nombre'); }
  get descripcion() { return this.categoriaForm.get('descripcion'); }
}