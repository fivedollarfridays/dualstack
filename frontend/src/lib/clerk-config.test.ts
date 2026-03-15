/**
 * Tests for lib/clerk-config.ts -- Shared Clerk appearance configuration
 *
 * Structural tests: verify shape and key presence without asserting
 * exact color hex values or Tailwind class strings, which are brittle.
 */
import { clerkAppearance } from './clerk-config';

describe('clerkAppearance', () => {
  it('exports a non-null appearance object', () => {
    expect(clerkAppearance).toBeDefined();
    expect(typeof clerkAppearance).toBe('object');
  });

  it('has variables and elements top-level keys', () => {
    expect(clerkAppearance).toHaveProperty('variables');
    expect(clerkAppearance).toHaveProperty('elements');
  });

  describe('variables', () => {
    const expectedVariableKeys = [
      'colorPrimary',
      'colorBackground',
      'colorText',
      'colorTextSecondary',
      'colorInputBackground',
      'colorInputText',
    ];

    it.each(expectedVariableKeys)('has variable "%s"', (key) => {
      expect(clerkAppearance.variables).toHaveProperty(key);
    });

    it('all variable values are non-empty strings', () => {
      for (const value of Object.values(clerkAppearance.variables)) {
        expect(typeof value).toBe('string');
        expect((value as string).length).toBeGreaterThan(0);
      }
    });
  });

  describe('elements', () => {
    const expectedElementKeys = [
      'rootBox',
      'card',
      'headerTitle',
      'headerSubtitle',
      'socialButtonsBlockButton',
      'formFieldLabel',
      'formFieldInput',
      'footerActionLink',
      'formButtonPrimary',
    ];

    it.each(expectedElementKeys)('has element "%s"', (key) => {
      expect(clerkAppearance.elements).toHaveProperty(key);
    });

    it('all element values are non-empty strings', () => {
      for (const value of Object.values(clerkAppearance.elements)) {
        expect(typeof value).toBe('string');
        expect((value as string).length).toBeGreaterThan(0);
      }
    });
  });

  it('colorPrimary is a non-empty string (smoke test)', () => {
    const value = clerkAppearance.variables.colorPrimary;
    expect(typeof value).toBe('string');
    expect(value.length).toBeGreaterThan(0);
  });
});
