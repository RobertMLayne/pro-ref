/**
 * Configuration settings for OpenAlex Citation Fetcher
 */

const CONFIG = {
  // API Configuration
  openAlexBaseUrl: 'https://api.openalex.org',
  userAgent: 'OpenAlex Citation Fetcher (mailto:robertmlayne@icloud.com)',
  
  // Rate limiting (requests per minute)
  rateLimitPerMinute: 100,
  
  // Download settings
  downloadTimeout: 30000, // 30 seconds
  maxFileSize: 100 * 1024 * 1024, // 100MB
  
  // File naming
  filenameSanitationRegex: /[^a-z0-9_\-\. ]+/gi,
  filenameReplacement: '_',
  
  // Debug settings
  debug: false,
  logLevel: 'info', // 'debug', 'info', 'warn', 'error'
  
  // Citation processing
  maxCitationsToFetch: 1000,
  citationBatchSize: 100,
  
  // Supported identifier patterns
  identifierPatterns: {
    doi: /^10\.\d+\/\S+$/,
    arxiv: /^\d{4}\.\d{4,5}(v\d+)?$/,
    openalex: /^W\d+$/,
    pmcid: /^PMC\d+$/,
    pmid: /^\d+$/,
    mag: /^\d+$/,
    s2: /^\d+$/
  },
  
  // API endpoints
  endpoints: {
    works: '/works',
    referencedWorks: '/referenced_works',
    citedBy: '/cited_by'
  },
  
  // File extensions
  fileExtensions: {
    ris: 'ris',
    pdf: 'pdf',
    json: 'json'
  },
  
  // Error messages
  errorMessages: {
    noIdentifier: 'Please enter an identifier.',
    unrecognizedFormat: 'Unrecognized identifier format.',
    requiresPrefix: 'All-digit IDs require prefix (pmid:/mag:).',
    unsupportedPrefix: 'Unsupported prefix.',
    networkError: 'Network error occurred.',
    apiError: 'API request failed.',
    downloadError: 'Download failed.'
  }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = CONFIG;
} else {
  // Browser environment
  window.CONFIG = CONFIG;
}