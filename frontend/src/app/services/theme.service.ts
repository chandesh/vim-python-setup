import { Injectable, signal } from '@angular/core';

export type ThemeId =
  | 'slate-clean'
  | 'midnight-cyber'
  | 'warm-enterprise'
  | 'solarized-light'
  | 'solarized-dark';

export interface ThemeDefinition {
  id: ThemeId;
  name: string;
  description: string;
  mode: 'light' | 'dark';
  /** Preview swatch colors for the theme picker UI */
  swatch: {
    background: string;
    surface: string;
    accent: string;
    text: string;
  };
}

export const THEMES: ThemeDefinition[] = [
  {
    id: 'slate-clean',
    name: 'Slate Clean',
    description: 'Default Light',
    mode: 'light',
    swatch: { background: '#f8fafc', surface: '#ffffff', accent: '#2563eb', text: '#0f172a' }
  },
  {
    id: 'midnight-cyber',
    name: 'Midnight Cyber',
    description: 'Default Dark',
    mode: 'dark',
    swatch: { background: '#090d16', surface: '#1f2937', accent: '#6366f1', text: '#f9fafb' }
  },
  {
    id: 'warm-enterprise',
    name: 'Warm Enterprise',
    description: 'New',
    mode: 'light',
    swatch: { background: '#fbf9f5', surface: '#f4f0ea', accent: '#292524', text: '#1c1917' }
  },
  {
    id: 'solarized-light',
    name: 'Solarized Light',
    description: 'Classic · Refined',
    mode: 'light',
    swatch: { background: '#fdf6e3', surface: '#fffcf2', accent: '#268bd2', text: '#073642' }
  },
  {
    id: 'solarized-dark',
    name: 'Solarized Dark',
    description: 'Classic Dark · Refined',
    mode: 'dark',
    swatch: { background: '#002b36', surface: '#0a3d4d', accent: '#268bd2', text: '#eee8d5' }
  }
];

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private readonly THEME_KEY = 'user_preferred_theme';
  private readonly LEGACY_THEME_KEY = 'theme-preference';

  /** All available themes for pickers/menus */
  readonly themes = THEMES;

  // Reactive theme state
  theme = signal<ThemeId>(this.getInitialTheme());

  constructor() {
    this.applyTheme(this.theme());
    this.watchSystemPreference();
  }

  /**
   * Get initial theme: stored preference > legacy stored value >
   * system color-scheme > slate-clean default
   */
  private getInitialTheme(): ThemeId {
    if (typeof localStorage !== 'undefined') {
      const stored = localStorage.getItem(this.THEME_KEY);
      if (this.isValidTheme(stored)) {
        return stored;
      }

      // Migrate pre-existing light/dark preference to the new scheme
      const legacy = localStorage.getItem(this.LEGACY_THEME_KEY);
      if (legacy === 'dark') {
        return 'midnight-cyber';
      }
      if (legacy === 'light') {
        return 'slate-clean';
      }
    }

    return this.getSystemTheme();
  }

  private getSystemTheme(): ThemeId {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'midnight-cyber'
        : 'slate-clean';
    }
    return 'slate-clean';
  }

  private isValidTheme(value: string | null): value is ThemeId {
    return !!value && this.themes.some(t => t.id === value);
  }

  /**
   * Keep following the OS color scheme until the user picks a theme explicitly.
   */
  private watchSystemPreference(): void {
    if (typeof window === 'undefined' || !window.matchMedia) {
      return;
    }

    const media = window.matchMedia('(prefers-color-scheme: dark)');
    media.addEventListener('change', (event) => {
      if (typeof localStorage !== 'undefined' && localStorage.getItem(this.THEME_KEY)) {
        return; // Explicit user choice wins
      }
      this.setTheme(event.matches ? 'midnight-cyber' : 'slate-clean', { persist: false });
    });
  }

  /**
   * Set a specific theme and persist it as the user's explicit choice.
   */
  setTheme(theme: ThemeId, options: { persist?: boolean } = {}): void {
    const { persist = true } = options;

    this.theme.set(theme);
    this.applyTheme(theme);

    if (persist && typeof localStorage !== 'undefined') {
      localStorage.setItem(this.THEME_KEY, theme);
    }
  }

  /**
   * Apply theme via data-theme attribute on <html>
   */
  private applyTheme(theme: ThemeId): void {
    if (typeof document !== 'undefined') {
      const root = document.documentElement;
      root.setAttribute('data-theme', theme);
      root.classList.remove('dark'); // Clean up legacy class-based theming
    }
  }

  getThemeDefinition(id: ThemeId = this.theme()): ThemeDefinition {
    return this.themes.find(t => t.id === id) ?? this.themes[0];
  }

  getCurrentTheme(): ThemeId {
    return this.theme();
  }
}
