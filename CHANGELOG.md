# Changelog

All notable changes to the OpenAlex Citation Fetcher extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-08

### Added

- **Modular Architecture**: Refactored codebase into separate utility modules
  - `IdentifierParser`: Handles parsing and validation of academic identifiers
  - `OpenAlexApiClient`: Manages API communication with rate limiting
  - `CitationProcessor`: Processes citations end-to-end with error handling
- **Enhanced UI**: Improved popup interface with better styling and user feedback
- **Configuration Management**: Centralized configuration in `config.js`
- **Progress Indicators**: Real-time feedback during processing
- **Error Handling**: Comprehensive error handling and user-friendly messages
- **Rate Limiting**: Built-in API rate limiting to respect OpenAlex guidelines
- **Keyboard Shortcuts**: Added Ctrl+Shift+F shortcut for quick access
- **Input Validation**: Real-time validation of identifier formats
- **Download Statistics**: Detailed feedback on successful downloads

### Enhanced

- **Citation Processing**: Complete implementation of citation fetching for referenced works and citing works
- **File Naming**: Improved filename sanitization and conflict resolution
- **API Integration**: More robust API calls with proper error handling and retries
- **User Experience**: Better visual feedback and status messages
- **Documentation**: Comprehensive README with installation and usage instructions

### Changed

- **File Structure**: Organized code into logical modules in `utils/` directory
- **Manifest Version**: Updated to version 1.1.0 with enhanced permissions
- **Dependencies**: Added development dependencies for testing and building

### Fixed

- **Duplicate Files**: Removed duplicate files with "(2)" suffixes
- **Empty Directories**: Cleaned up unused "Auto Hotkey" directory
- **Hard-coded Values**: Moved configuration to external config file
- **Incomplete Functions**: Fully implemented citation processing functionality

### Security

- **Content Security Policy**: Added CSP to prevent XSS attacks
- **Permission Scoping**: Refined host permissions to minimum required scope

## [1.0.0] - 2025-06-01

### Added

- Initial release of OpenAlex Citation Fetcher
- Basic support for DOI, PubMed ID, PMC ID, arXiv ID, and OpenAlex ID
- Context menu integration for selected text
- RIS metadata download
- PDF download when available
- Chrome extension popup interface

### Features

- **Multi-format Support**: Handle various academic identifier formats
- **Automatic Downloads**: Fetch RIS citation files and PDFs
- **Context Menu**: Right-click selected text to fetch citations
- **OpenAlex Integration**: Direct integration with OpenAlex API

## [Unreleased]

### Planned

- **Batch Processing**: Support for processing multiple identifiers at once
- **Export Formats**: Additional export formats (BibTeX, EndNote)
- **Citation Networks**: Enhanced visualization of citation relationships
- **User Preferences**: Customizable settings and preferences
- **Offline Support**: Basic offline functionality for cached data
- **Browser Sync**: Synchronize settings across devices
