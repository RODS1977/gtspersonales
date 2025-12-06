export interface Usuario {
  id?: number;
  nombre: string;
  correo: string;
  password?: string;
  fecha_creacion?: Date;
  fecha_actualizacion?: Date;
}

export interface LoginRequest {
  correo: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
  usuario?: {
    id: number;
    nombre: string;
    correo: string;
  };
}