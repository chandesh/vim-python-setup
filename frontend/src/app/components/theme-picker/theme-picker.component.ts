import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { THEMES, ThemeId, ThemeService } from '../../services/theme.service';

@Component({
  selector: 'app-theme-picker',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './theme-picker.component.html',
  styleUrls: ['./theme-picker.component.css']
})
export class ThemePickerComponent {
  readonly themeService = inject(ThemeService);
  readonly themes = THEMES;

  selectTheme(themeId: ThemeId): void {
    this.themeService.setTheme(themeId);
  }

  isSelected(themeId: ThemeId): boolean {
    return this.themeService.theme() === themeId;
  }
}
