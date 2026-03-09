/**
 * Tests for shared constants.
 */
import { CONFIRM_PHRASE } from './constants';

describe('constants', () => {
  it('exports CONFIRM_PHRASE as a non-empty string', () => {
    expect(typeof CONFIRM_PHRASE).toBe('string');
    expect(CONFIRM_PHRASE.length).toBeGreaterThan(0);
  });

  it('CONFIRM_PHRASE is uppercase for visual clarity', () => {
    expect(CONFIRM_PHRASE).toBe(CONFIRM_PHRASE.toUpperCase());
  });
});
