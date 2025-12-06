export interface Gasto {
  id?: number;
  usuario_id: number;
  categoria_id: number;
  monto: number;
  fecha: Date | string;
  descripcion: string;
  fecha_creacion?: Date;
  fecha_actualizacion?: Date;
  
  // Para mostrar en frontend
  categoria_nombre?: string;
  usuario_nombre?: string;
}

export interface GastoCreate {
  categoria_id: number;
  monto: number;
  fecha: string;
  descripcion: string;
}