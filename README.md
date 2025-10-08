# OpenAlex Citation Fetcher

A Chrome extension for fetching academic citation metadata and PDFs from OpenAlex, with support for DOI, PubMed, arXiv, and other academic identifiers.

## Features

- 🔍 **Multi-format Support**: DOI, PubMed ID, PMC ID, arXiv ID, OpenAlex ID
- 📄 **Automatic Downloads**: Fetches RIS citation files and available PDFs
- 🖱️ **Context Menu Integration**: Right-click selected text to fetch citations
- 📚 **Citation Networks**: Optional flags to fetch referenced works and citations
- 🎯 **Smart Detection**: Automatically detects identifier formats

## Installation

### From Source
1. Clone this repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" in the top right
4. Click "Load unpacked" and select the `Extension` folder
5. The extension icon should appear in your toolbar

### Development Setup
```bash
npm install
npm run build
npm test
```

## Usage

### Basic Citation Fetching
1. **Via Extension Popup**: Click the extension icon and enter an identifier
2. **Via Context Menu**: Select text containing an identifier, right-click, and choose "Fetch Citation Metadata"

### Supported Identifiers
- **DOI**: `10.1038/nature12373` or `doi:10.1038/nature12373`
- **PubMed ID**: `pmid:23685631`
- **PMC ID**: `PMC4123456` or `pmcid:PMC4123456`
- **arXiv ID**: `1234.5678` or `arxiv:1234.5678`
- **OpenAlex ID**: `W2123456789` or `openalex:W2123456789`

### Advanced Flags
Add flags after the identifier for additional functionality:
- `--WC`: Download referenced works citations
- `--SW`: Download citing works citations

**Example**: `10.1038/nature12373 --WC --SW`

## File Outputs

- **RIS Files**: `[sanitized_identifier].ris` - Citation metadata
- **PDF Files**: `[sanitized_identifier].pdf` - Full text when available
- **Citation Sets**: Additional RIS files for reference networks

## Configuration

Edit `Extension/config.js` to customize:
- User-Agent email address
- Download file naming patterns
- API rate limiting settings

## Development

### Project Structure
```
Extension/
├── manifest.json          # Chrome extension manifest
├── popup.html             # Extension popup interface
├── popup.js               # Main functionality
├── background.js          # Background service worker
├── config.js              # Configuration settings
├── utils/
│   ├── identifier-parser.js  # ID parsing utilities
│   ├── api-client.js        # OpenAlex API client
│   └── citation-processor.js # Citation processing
└── tests/
    └── *.test.js          # Unit tests
```

### Building
```bash
npm run build              # Build extension
npm run lint              # Lint code
npm run test              # Run tests
npm run package           # Create distributable package
```

### Testing
```bash
npm test                  # Run all tests
npm run test:unit         # Unit tests only
npm run test:integration  # Integration tests only
```

## API Reference

### OpenAlex API
This extension uses the [OpenAlex API](https://docs.openalex.org/) to fetch academic metadata.

**Rate Limits**: 100,000 requests per day for polite users
**Courtesy**: Please include your email in the User-Agent string

### Supported Formats
- **Input**: DOI, PubMed ID, PMC ID, arXiv ID, OpenAlex ID
- **Output**: RIS (Research Information Systems) format
- **Downloads**: PDF when open access available

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Use ESLint configuration provided
- Follow Chrome extension best practices
- Include tests for new functionality
- Update documentation for API changes

## Troubleshooting

### Common Issues

**"Unrecognized identifier format"**
- Ensure the identifier matches supported formats
- Try adding an explicit prefix (e.g., `doi:` or `pmid:`)

**"OpenAlex 404"**
- The identifier may not exist in OpenAlex database
- Verify the identifier is correct
- Some older publications may not be indexed

**Downloads not working**
- Check Chrome's download settings
- Ensure the extension has download permissions
- Verify the PDF URL is accessible

**Context menu not appearing**
- Ensure text is selected before right-clicking
- Check that the extension is enabled
- Reload the page and try again

### Debug Mode
Enable debug logging in `config.js`:
```javascript
const CONFIG = {
  debug: true,
  // ... other settings
};
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenAlex](https://openalex.org/) for providing open academic metadata
- [CrossRef](https://www.crossref.org/) for DOI resolution services
- Chrome Extensions team for the platform

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.