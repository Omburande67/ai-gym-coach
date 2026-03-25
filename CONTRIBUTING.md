# Contributing to AI Gym Coach

Thank you for your interest in contributing to AI Gym Coach! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-gym-coach.git
   cd ai-gym-coach
   ```

2. **Run the setup script**
   
   On Linux/Mac:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   
   On Windows:
   ```bash
   setup.bat
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Style

### Frontend (TypeScript/React)

- Use TypeScript for all new code
- Follow the ESLint configuration
- Format code with Prettier before committing
- Use functional components with hooks
- Write meaningful component and variable names

Run linting and formatting:
```bash
cd frontend
npm run lint
npx prettier --write .
```

### Backend (Python)

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Format code with Black (line length: 100)
- Sort imports with isort
- Use meaningful variable and function names

Run linting and formatting:
```bash
cd backend
black .
isort .
flake8
mypy app
```

## Testing

### Writing Tests

- Write tests for all new features
- Include both unit tests and property-based tests
- Aim for >80% code coverage
- Test edge cases and error conditions

### Running Tests

Frontend:
```bash
cd frontend
npm test
npm run test:coverage
```

Backend:
```bash
cd backend
pytest
pytest --cov=app --cov-report=html
```

### Property-Based Testing

For backend property tests, use Hypothesis:
```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=0, max_value=180))
def test_angle_calculation(angle):
    # Test implementation
    pass
```

For frontend property tests, use fast-check:
```typescript
import fc from 'fast-check';

it('should handle all valid angles', () => {
  fc.assert(
    fc.property(fc.integer({ min: 0, max: 180 }), (angle) => {
      // Test implementation
    })
  );
});
```

## Commit Messages

Follow the Conventional Commits specification:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example:
```
feat: add exercise recognition for lunges

- Implement lunge detection algorithm
- Add angle thresholds for lunge pattern
- Update exercise registry
```

## Pull Request Process

1. **Update documentation** if you're adding new features
2. **Add tests** for your changes
3. **Ensure all tests pass** locally
4. **Run linters and formatters**
5. **Update the README** if needed
6. **Create a pull request** with a clear description

### PR Description Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe the tests you added or ran

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## Project Structure

```
ai-gym-coach/
├── frontend/           # Next.js frontend
│   ├── src/
│   │   ├── app/       # Next.js pages
│   │   ├── components/ # React components
│   │   ├── lib/       # Utilities
│   │   └── types/     # TypeScript types
│   └── public/        # Static assets
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── core/      # Core functionality
│   │   ├── models/    # Database models
│   │   ├── schemas/   # Pydantic schemas
│   │   └── services/  # Business logic
│   └── tests/         # Test files
└── docker-compose.yml # Docker configuration
```

## Architecture Guidelines

### Frontend

- **Components**: Keep components small and focused
- **State Management**: Use React Context for global state
- **API Calls**: Create service functions in `src/lib/api`
- **Types**: Define TypeScript interfaces in `src/types`

### Backend

- **API Routes**: Define in `app/api/`
- **Business Logic**: Implement in `app/services/`
- **Database Models**: Define in `app/models/`
- **Schemas**: Create Pydantic models in `app/schemas/`

### Privacy-First Design

- Never store or transmit raw video frames
- Process video locally in the browser
- Only send pose keypoints to the backend
- Document privacy implications of changes

## Getting Help

- Open an issue for bugs or feature requests
- Join discussions in GitHub Discussions
- Ask questions in pull request comments

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
