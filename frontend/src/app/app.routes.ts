import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { AgentsListComponent } from './components/agents-list/agents-list.component';
import { AgentDetailComponent } from './components/agent-detail/agent-detail.component';
import { McpServersComponent } from './components/mcp-servers/mcp-servers.component';
import { McpServerDetailComponent } from './components/mcp-server-detail/mcp-server-detail.component';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { UserProfileComponent } from './components/user-profile/user-profile.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'agents', component: AgentsListComponent },
  { path: 'agents/:id', component: AgentDetailComponent },
  { path: 'mcp-servers', component: McpServersComponent },
  { path: 'mcp-servers/:id', component: McpServerDetailComponent },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'profile', component: UserProfileComponent, canActivate: [authGuard] },
  { path: '**', redirectTo: '' }
];
