/**
 * OpenAlex API client with rate limiting and error handling
 */

class OpenAlexApiClient {
  constructor(config = window.CONFIG) {
    this.config = config;
    this.baseUrl = config.openAlexBaseUrl;
    this.userAgent = config.userAgent;
    this.rateLimiter = new RateLimiter(config.rateLimitPerMinute);
  }

  /**
   * Fetch work metadata from OpenAlex
   * @param {string} lookup - Work identifier or URL
   * @param {string} format - Response format ('json' or 'ris')
   * @returns {Promise<object|string>} - Work metadata or RIS text
   */
  async fetchWork(lookup, format = 'json') {
    await this.rateLimiter.waitForSlot();

    const url = `${this.baseUrl}/works/${encodeURIComponent(lookup)}`;
    const headers = {
      'User-Agent': this.userAgent
    };

    if (format === 'ris') {
      headers.Accept = 'application/x-research-info-systems';
    } else {
      headers.Accept = 'application/json';
    }

    try {
      const response = await fetch(url, {
        headers,
        timeout: this.config.downloadTimeout
      });

      if (!response.ok) {
        throw new Error(`OpenAlex API error: ${response.status} ${response.statusText}`);
      }

      if (format === 'ris') {
        return await response.text();
      } else {
        return await response.json();
      }
    } catch (error) {
      this.logError('fetchWork', error, { lookup, format });
      throw error;
    }
  }

  /**
   * Fetch citations (referenced works or citing works)
   * @param {string} workId - OpenAlex work ID
   * @param {string} type - 'referenced_works' or 'cited_by'
   * @param {number} limit - Maximum number of citations to fetch
   * @returns {Promise<Array>} - Array of citation metadata
   */
  async fetchCitations(workId, type, limit = this.config.maxCitationsToFetch) {
    const citations = [];
    let cursor = null;
    let page = 1;

    while (citations.length < limit) {
      await this.rateLimiter.waitForSlot();

      const url = this.buildCitationsUrl(workId, type, cursor);
      
      try {
        const response = await fetch(url, {
          headers: {
            'Accept': 'application/json',
            'User-Agent': this.userAgent
          },
          timeout: this.config.downloadTimeout
        });

        if (!response.ok) {
          throw new Error(`Citations API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        citations.push(...data.results);

        // Check for pagination
        cursor = data.meta?.next_cursor;
        if (!cursor || citations.length >= limit) {
          break;
        }

        this.logDebug(`Fetched page ${page} for ${type}`, { 
          workId, 
          count: data.results.length, 
          total: citations.length 
        });
        
        page++;
      } catch (error) {
        this.logError('fetchCitations', error, { workId, type, page });
        break; // Continue with what we have
      }
    }

    return citations.slice(0, limit);
  }

  /**
   * Build URL for citations API
   * @param {string} workId - Work ID
   * @param {string} type - Citation type
   * @param {string} cursor - Pagination cursor
   * @returns {string} - Complete URL
   */
  buildCitationsUrl(workId, type, cursor = null) {
    const baseUrl = `${this.baseUrl}/works/${encodeURIComponent(workId)}/${type}`;
    const params = new URLSearchParams({
      'per-page': this.config.citationBatchSize.toString()
    });

    if (cursor) {
      params.set('cursor', cursor);
    }

    return `${baseUrl}?${params.toString()}`;
  }

  /**
   * Search works by query
   * @param {string} query - Search query
   * @param {object} filters - Additional filters
   * @returns {Promise<Array>} - Array of work metadata
   */
  async searchWorks(query, filters = {}) {
    await this.rateLimiter.waitForSlot();

    const params = new URLSearchParams({
      search: query,
      'per-page': '25'
    });

    // Add filters
    Object.entries(filters).forEach(([key, value]) => {
      params.set(key, value);
    });

    const url = `${this.baseUrl}/works?${params.toString()}`;

    try {
      const response = await fetch(url, {
        headers: {
          'Accept': 'application/json',
          'User-Agent': this.userAgent
        },
        timeout: this.config.downloadTimeout
      });

      if (!response.ok) {
        throw new Error(`Search API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data.results || [];
    } catch (error) {
      this.logError('searchWorks', error, { query, filters });
      throw error;
    }
  }

  /**
   * Get work statistics
   * @param {string} workId - Work ID
   * @returns {Promise<object>} - Work statistics
   */
  async getWorkStats(workId) {
    const work = await this.fetchWork(workId);
    
    return {
      citationCount: work.cited_by_count || 0,
      referenceCount: work.referenced_works?.length || 0,
      openAccess: work.open_access?.is_oa || false,
      publicationYear: work.publication_year,
      type: work.type,
      venue: work.primary_location?.source?.display_name
    };
  }

  /**
   * Log debug information
   * @param {string} message - Debug message
   * @param {object} data - Additional data
   */
  logDebug(message, data = {}) {
    if (this.config.debug && this.config.logLevel === 'debug') {
      console.debug(`[OpenAlexAPI] ${message}`, data);
    }
  }

  /**
   * Log error information
   * @param {string} method - Method name
   * @param {Error} error - Error object
   * @param {object} context - Additional context
   */
  logError(method, error, context = {}) {
    if (['debug', 'info', 'warn', 'error'].includes(this.config.logLevel)) {
      console.error(`[OpenAlexAPI:${method}] ${error.message}`, { error, context });
    }
  }
}

/**
 * Simple rate limiter for API requests
 */
class RateLimiter {
  constructor(requestsPerMinute) {
    this.requestsPerMinute = requestsPerMinute;
    this.requests = [];
  }

  async waitForSlot() {
    const now = Date.now();
    const oneMinuteAgo = now - 60000;

    // Remove requests older than 1 minute
    this.requests = this.requests.filter(time => time > oneMinuteAgo);

    // If we're at the limit, wait
    if (this.requests.length >= this.requestsPerMinute) {
      const oldestRequest = Math.min(...this.requests);
      const waitTime = oldestRequest + 60000 - now;
      
      if (waitTime > 0) {
        await new Promise(resolve => setTimeout(resolve, waitTime));
        return this.waitForSlot(); // Recursive call after waiting
      }
    }

    // Record this request
    this.requests.push(now);
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { OpenAlexApiClient, RateLimiter };
} else {
  // Browser environment
  window.OpenAlexApiClient = OpenAlexApiClient;
  window.RateLimiter = RateLimiter;
}