import { TestBed } from '@angular/core/testing';
import { ThemeService } from './theme.service';

describe('ThemeService', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.classList.remove('dark');
    TestBed.configureTestingModule({});
  });

  it('falls back to system color-scheme when no preference is stored', () => {
    const service = TestBed.inject(ThemeService);
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    expect(service.getCurrentTheme()).toBe(prefersDark ? 'midnight-cyber' : 'slate-clean');
  });

  it('applies data-theme and persists explicit selection', () => {
    const service = TestBed.inject(ThemeService);

    service.setTheme('warm-enterprise');

    expect(document.documentElement.getAttribute('data-theme')).toBe('warm-enterprise');
    expect(localStorage.getItem('user_preferred_theme')).toBe('warm-enterprise');
    expect(service.getCurrentTheme()).toBe('warm-enterprise');
  });

  it('restores the stored theme on initialization', () => {
    localStorage.setItem('user_preferred_theme', 'midnight-cyber');

    const service = TestBed.inject(ThemeService);

    expect(service.getCurrentTheme()).toBe('midnight-cyber');
    expect(document.documentElement.getAttribute('data-theme')).toBe('midnight-cyber');
  });

  it('migrates a legacy light/dark preference', () => {
    localStorage.setItem('theme-preference', 'dark');

    const service = TestBed.inject(ThemeService);

    expect(service.getCurrentTheme()).toBe('midnight-cyber');
  });

  it('removes the legacy dark class when applying themes', () => {
    document.documentElement.classList.add('dark');
    localStorage.setItem('user_preferred_theme', 'slate-clean');

    TestBed.inject(ThemeService);

    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('exposes all five theme definitions for the picker', () => {
    const service = TestBed.inject(ThemeService);
    expect(service.themes.map(t => t.id)).toEqual([
      'slate-clean',
      'midnight-cyber',
      'warm-enterprise',
      'solarized-light',
      'solarized-dark'
    ]);
  });

  it('accepts the classic solarized themes as valid selections', () => {
    const service = TestBed.inject(ThemeService);

    service.setTheme('solarized-dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('solarized-dark');
    expect(localStorage.getItem('user_preferred_theme')).toBe('solarized-dark');

    service.setTheme('solarized-light');
    expect(document.documentElement.getAttribute('data-theme')).toBe('solarized-light');
    expect(localStorage.getItem('user_preferred_theme')).toBe('solarized-light');
  });
});
