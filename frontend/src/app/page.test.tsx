import { render, screen } from '@testing-library/react';
import Home from './page';

describe('Home Page', () => {
  it('renders the main heading', () => {
    render(<Home />);
    const heading = screen.getByText('AI Gym Coach');
    expect(heading).toBeInTheDocument();
  });

  it('renders the description', () => {
    render(<Home />);
    const description = screen.getByText('Privacy-first real-time workout recognition');
    expect(description).toBeInTheDocument();
  });
});
