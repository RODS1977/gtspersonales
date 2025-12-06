import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard } from './guards/auth.guard';

// Importaremos los componentes cuando los creemos
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { GastosComponent } from './components/gastos/gastos.component';
import { CategoriasComponent } from './components/categorias/categorias.component';

const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  
  // Rutas protegidas
  { 
    path: 'dashboard', 
    component: DashboardComponent, 
    canActivate: [AuthGuard] 
  },
  { 
    path: 'gastos', 
    component: GastosComponent, 
    canActivate: [AuthGuard] 
  },
  { 
    path: 'categorias', 
    component: CategoriasComponent, 
    canActivate: [AuthGuard] 
  },
  
  // Redirección para rutas no encontradas
  { path: '**', redirectTo: '/dashboard' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }