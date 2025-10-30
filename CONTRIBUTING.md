# Contributing to LinkedIn Profile Scraper

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Any error messages or logs

### Suggesting Features

Feature requests are welcome! Please open an issue with:
- A clear description of the feature
- Why it would be useful
- Example use cases
- Any implementation ideas

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/linkedinprofilescraper.git
   cd linkedinprofilescraper
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

4. **Test your changes**
   ```bash
   python main.py -u "https://linkedin.com/in/testprofile"
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Provide a clear description
   - Reference any related issues
   - Explain what you changed and why

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small

### Project Structure

```
linkedinprofilescraper/
├── config.py           # Configuration management
├── parsers.py          # HTML/data parsing utilities
├── scraper.py          # Main scraper logic
├── main.py             # CLI entry point
└── tests/              # Test files (future)
```

### Adding New Extraction Features

When adding extraction for new profile sections:

1. **Add extraction method in `scraper.py`**
   ```python
   async def _extract_new_section(self) -> List[Dict[str, Any]]:
       """Extract new section data"""
       data = []
       # Your extraction logic here
       return data
   ```

2. **Add parsing utilities in `parsers.py`** (if needed)
   ```python
   def parse_new_field(text: str) -> Any:
       """Parse specific field format"""
       # Your parsing logic here
       return parsed_value
   ```

3. **Call in main scrape method**
   ```python
   profile_data['newSection'] = await self._extract_new_section()
   ```

4. **Update documentation**
   - Add to README.md output format
   - Add example output
   - Update field descriptions

### Testing

Before submitting a PR:

1. Test with multiple profiles
2. Test with profiles that have/don't have the data you're extracting
3. Test error handling
4. Verify output format matches expected JSON structure

### Error Handling

- Use try-except blocks for extraction logic
- Log errors with descriptive messages
- Don't let one error stop the entire scrape
- Return default values (empty string, empty list, etc.) on errors

Example:
```python
try:
    # Extraction logic
    value = extract_something()
except Exception as e:
    print(f"Error extracting field: {e}")
    value = ""
```

## Areas for Contribution

Here are some areas where contributions would be especially valuable:

### High Priority
- [ ] Improve error handling and retry logic
- [ ] Add unit tests
- [ ] Better handling of privacy-restricted profiles
- [ ] Improve speed/performance
- [ ] Add support for company pages

### Medium Priority
- [ ] Add CSV export format
- [ ] Database integration (SQLite, PostgreSQL)
- [ ] Web UI/dashboard
- [ ] Better logging system
- [ ] Rate limiting improvements

### Low Priority
- [ ] Docker containerization
- [ ] API server mode
- [ ] Scheduled scraping
- [ ] Email notifications
- [ ] Data visualization

## Code Review Process

1. All PRs will be reviewed by maintainers
2. We may suggest changes or improvements
3. Once approved, your PR will be merged
4. Your contribution will be credited in the changelog

## Questions?

If you have questions about contributing:
- Open an issue
- Check existing issues and PRs
- Review the README.md documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Every contribution helps make this project better. Thank you for being part of the community!
