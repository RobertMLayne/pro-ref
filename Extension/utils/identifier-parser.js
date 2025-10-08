/**
 * Identifier parsing utilities for academic identifiers
 */

class IdentifierParser {
  constructor(config = window.CONFIG) {
    this.config = config;
    this.patterns = config.identifierPatterns;
  }

  /**
   * Parse input string to extract identifier and flags
   * @param {string} raw - Raw input string
   * @returns {object} - {lookup, flags, error}
   */
  parseInput(raw) {
    if (!raw || typeof raw !== 'string') {
      return { error: this.config.errorMessages.noIdentifier };
    }

    const parts = raw.trim().split(/\s+/);
    const idPart = parts.shift();
    const flags = new Set(parts.filter(p => /^--(WC|SW|ONN)$/.test(p)));

    const { prefix, id, error } = this.extractPrefixAndId(idPart);
    if (error) {
      return { error };
    }

    const lookup = this.constructLookupUrl(prefix, id);
    if (!lookup) {
      return { error: this.config.errorMessages.unsupportedPrefix };
    }

    return { lookup, flags, prefix, id };
  }

  /**
   * Extract prefix and ID from identifier
   * @param {string} idPart - Identifier part
   * @returns {object} - {prefix, id, error}
   */
  extractPrefixAndId(idPart) {
    const prefixMatch = idPart.match(/^([A-Za-z]+):(.+)$/);
    
    if (prefixMatch) {
      const prefix = prefixMatch[1].toLowerCase();
      const id = prefixMatch[2];
      return { prefix, id };
    }

    // Auto-detect format
    if (this.patterns.doi.test(idPart)) {
      return { prefix: 'doi', id: idPart };
    }
    
    if (this.patterns.arxiv.test(idPart)) {
      return { prefix: 'arxiv', id: idPart };
    }
    
    if (this.patterns.openalex.test(idPart)) {
      return { prefix: 'openalex', id: idPart };
    }
    
    if (this.patterns.pmcid.test(idPart)) {
      return { prefix: 'pmcid', id: idPart };
    }
    
    if (this.patterns.pmid.test(idPart)) {
      return { error: this.config.errorMessages.requiresPrefix };
    }

    return { error: this.config.errorMessages.unrecognizedFormat };
  }

  /**
   * Construct lookup URL based on prefix and ID
   * @param {string} prefix - Identifier prefix
   * @param {string} id - Identifier value
   * @returns {string|null} - Lookup URL or null if unsupported
   */
  constructLookupUrl(prefix, id) {
    const urlMap = {
      doi: `https://doi.org/${id}`,
      pmid: `https://pubmed.ncbi.nlm.nih.gov/${id}`,
      pmcid: `https://www.ncbi.nlm.nih.gov/pmc/articles/${id}`,
      arxiv: `https://arxiv.org/abs/${id}`,
      openalex: id, // Already in correct format
      mag: `https://doi.org/${id}`, // Microsoft Academic Graph
      s2: `https://doi.org/${id}` // Semantic Scholar
    };

    return urlMap[prefix] || null;
  }

  /**
   * Validate identifier format
   * @param {string} identifier - Identifier to validate
   * @param {string} expectedPrefix - Expected prefix (optional)
   * @returns {boolean} - Whether identifier is valid
   */
  isValidIdentifier(identifier, expectedPrefix = null) {
    const { prefix, error } = this.extractPrefixAndId(identifier);
    
    if (error) {
      return false;
    }

    if (expectedPrefix && prefix !== expectedPrefix) {
      return false;
    }

    return true;
  }

  /**
   * Get supported identifier types
   * @returns {Array} - Array of supported prefixes
   */
  getSupportedTypes() {
    return Object.keys(this.patterns);
  }

  /**
   * Sanitize filename for downloads
   * @param {string} name - Original filename
   * @returns {string} - Sanitized filename
   */
  sanitizeFilename(name) {
    return name
      .replace(this.config.filenameSanitationRegex, this.config.filenameReplacement)
      .trim()
      .replace(/\s+/g, this.config.filenameReplacement)
      .replace(/_+/g, '_') // Remove multiple underscores
      .replace(/^_|_$/g, ''); // Remove leading/trailing underscores
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = IdentifierParser;
} else {
  // Browser environment
  window.IdentifierParser = IdentifierParser;
}