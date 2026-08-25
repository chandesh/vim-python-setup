import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { AgentsListComponent } from './components/agents-list/agents-list.component';
import { McpServersComponent } from './components/mcp-servers/mcp-servers.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'agents', component: AgentsListComponent },
  { path: 'mcp-servers', component: McpServersComponent },
  { path: '**', redirectTo: '' }
];
