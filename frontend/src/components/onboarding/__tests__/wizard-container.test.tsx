/**
 * Tests for WizardContainer component.
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { WizardContainer } from '../wizard-container';

const mockSteps = [
  { label: 'Welcome', content: <div>Welcome content</div> },
  { label: 'Preferences', content: <div>Preferences content</div> },
  { label: 'First Item', content: <div>First item content</div> },
  { label: 'Complete', content: <div>Completion content</div> },
];

const defaultProps = {
  steps: mockSteps,
  currentStep: 0,
  onNext: jest.fn(),
  onBack: jest.fn(),
  onSkip: jest.fn(),
};

beforeEach(() => {
  jest.clearAllMocks();
});

describe('WizardContainer', () => {
  it('renders current step content and progress indicator', () => {
    render(<WizardContainer {...defaultProps} />);

    expect(screen.getByText('Welcome content')).toBeInTheDocument();
    expect(screen.getByText('Step 1 of 4')).toBeInTheDocument();
  });

  it('shows Skip button on every step', () => {
    const { rerender } = render(<WizardContainer {...defaultProps} currentStep={0} />);
    expect(screen.getByRole('button', { name: /skip/i })).toBeInTheDocument();

    rerender(<WizardContainer {...defaultProps} currentStep={2} />);
    expect(screen.getByRole('button', { name: /skip/i })).toBeInTheDocument();
  });

  it('hides Back button on first step, shows on subsequent steps', () => {
    const { rerender } = render(<WizardContainer {...defaultProps} currentStep={0} />);
    expect(screen.queryByRole('button', { name: /back/i })).not.toBeInTheDocument();

    rerender(<WizardContainer {...defaultProps} currentStep={1} />);
    expect(screen.getByRole('button', { name: /back/i })).toBeInTheDocument();
  });

  it('calls onNext, onBack, and onSkip when buttons clicked', () => {
    const onNext = jest.fn();
    const onBack = jest.fn();
    const onSkip = jest.fn();

    render(
      <WizardContainer
        {...defaultProps}
        currentStep={1}
        onNext={onNext}
        onBack={onBack}
        onSkip={onSkip}
      />
    );

    fireEvent.click(screen.getByRole('button', { name: /next/i }));
    expect(onNext).toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /back/i }));
    expect(onBack).toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: /skip/i }));
    expect(onSkip).toHaveBeenCalled();
  });

  it('shows "Finish" instead of "Next" on the last step', () => {
    render(<WizardContainer {...defaultProps} currentStep={3} />);

    expect(screen.queryByRole('button', { name: /next/i })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: /finish/i })).toBeInTheDocument();
    expect(screen.getByText('Completion content')).toBeInTheDocument();
  });
});
