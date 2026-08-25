import { Component, ElementRef, HostListener, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ThemePickerComponent } from '../theme-picker/theme-picker.component';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule, ThemePickerComponent],
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {
  readonly isProfileMenuOpen = signal(false);
  isMobileMenuOpen = false;

  private readonly elementRef = inject(ElementRef);

  // Mobile navigation
  toggleMenu(): void {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }

  closeMenu(): void {
    this.isMobileMenuOpen = false;
  }

  // Profile dropdown
  toggleProfileMenu(event: Event): void {
    event.stopPropagation();
    this.isProfileMenuOpen.update(open => !open);
  }

  closeProfileMenu(): void {
    this.isProfileMenuOpen.set(false);
  }

  onDropdownClick(event: Event): void {
    // Keep outside-click handler from closing while interacting inside the panel
    event.stopPropagation();
  }

  logout(): void {
    // Placeholder until authentication is implemented
    this.closeProfileMenu();
  }

  @HostListener('document:click')
  onDocumentClick(): void {
    if (this.isProfileMenuOpen()) {
      this.isProfileMenuOpen.set(false);
    }
  }

  @HostListener('document:keydown.escape')
  onEscapeKey(): void {
    if (this.isProfileMenuOpen()) {
      this.closeProfileMenu();
    }
  }
}
