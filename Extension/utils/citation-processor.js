/**
 * Citation processing utilities for downloading and formatting citations
 */

class CitationProcessor {
    constructor(config = window.CONFIG) {
        this.config = config;
        this.apiClient = new OpenAlexApiClient(config);
        this.parser = new IdentifierParser(config);
    }

    /**
     * Process a citation request end-to-end
     * @param {string} identifier - Academic identifier
     * @param {Set} flags - Processing flags
     * @returns {Promise<object>} - Processing results
     */
    async processCitation(identifier, flags = new Set()) {
        const results = {
            success: false,
            downloads: [],
            errors: [],
            metadata: null
        };

        try {
            // Parse identifier
            const parseResult = this.parser.parseInput(identifier);
            if (parseResult.error) {
                results.errors.push(parseResult.error);
                return results;
            }

            const { lookup } = parseResult;
            const baseName = this.parser.sanitizeFilename(lookup);

            // Fetch work metadata
            results.metadata = await this.apiClient.fetchWork(lookup, 'json');

            // Download PDF if available
            await this.downloadPdf(results.metadata, baseName, results);

            // Download RIS metadata
            await this.downloadRis(lookup, baseName, results);

            // Process flags for additional downloads
            if (flags.has('--WC')) {
                await this.processCitations(results.metadata.id, baseName, 'referenced_works', results);
            }

            if (flags.has('--SW')) {
                await this.processCitations(results.metadata.id, baseName, 'cited_by', results);
            }

            results.success = true;
        } catch (error) {
            results.errors.push(`Processing failed: ${error.message}`);
            this.logError('processCitation', error, { identifier, flags });
        }

        return results;
    }

    /**
     * Download PDF files if available
     * @param {object} metadata - Work metadata
     * @param {string} baseName - Base filename
     * @param {object} results - Results object to update
     */
    async downloadPdf(metadata, baseName, results) {
        const pdfUrls = this.extractPdfUrls(metadata);

        for (let i = 0; i < pdfUrls.length; i++) {
            try {
                const filename = `${baseName}${pdfUrls.length > 1 ? `-${i + 1}` : ''}.${this.config.fileExtensions.pdf}`;

                await chrome.downloads.download({
                    url: pdfUrls[i],
                    filename: filename,
                    conflictAction: 'uniquify'
                });

                results.downloads.push({
                    type: 'pdf',
                    filename: filename,
                    url: pdfUrls[i]
                });

                this.logDebug('PDF downloaded', { filename, url: pdfUrls[i] });
            } catch (error) {
                results.errors.push(`PDF download failed: ${error.message}`);
                this.logError('downloadPdf', error, { url: pdfUrls[i] });
            }
        }
    }

    /**
     * Download RIS metadata
     * @param {string} lookup - Work lookup identifier
     * @param {string} baseName - Base filename
     * @param {object} results - Results object to update
     */
    async downloadRis(lookup, baseName, results) {
        try {
            const risText = await this.apiClient.fetchWork(lookup, 'ris');

            if (risText && risText.trim()) {
                const blob = new Blob([risText], {
                    type: 'application/x-research-info-systems'
                });
                const url = URL.createObjectURL(blob);
                const filename = `${baseName}.${this.config.fileExtensions.ris}`;

                await chrome.downloads.download({
                    url: url,
                    filename: filename,
                    conflictAction: 'uniquify'
                });

                URL.revokeObjectURL(url);

                results.downloads.push({
                    type: 'ris',
                    filename: filename,
                    size: risText.length
                });

                this.logDebug('RIS downloaded', { filename, size: risText.length });
            }
        } catch (error) {
            results.errors.push(`RIS download failed: ${error.message}`);
            this.logError('downloadRis', error, { lookup });
        }
    }

    /**
     * Process citations (referenced works or citing works)
     * @param {string} workId - OpenAlex work ID
     * @param {string} baseName - Base filename
     * @param {string} type - 'referenced_works' or 'cited_by'
     * @param {object} results - Results object to update
     */
    async processCitations(workId, baseName, type, results) {
        try {
            const citations = await this.apiClient.fetchCitations(workId, type);

            if (citations.length > 0) {
                const citationData = this.formatCitations(citations, type);
                const filename = `${baseName}_${type}.${this.config.fileExtensions.json}`;

                await this.downloadJsonData(citationData, filename, results);

                this.logDebug(`Citations processed`, {
                    type,
                    count: citations.length,
                    filename
                });
            }
        } catch (error) {
            results.errors.push(`Citation processing failed for ${type}: ${error.message}`);
            this.logError('processCitations', error, { workId, type });
        }
    }

    /**
     * Download JSON data as file
     * @param {object} data - Data to download
     * @param {string} filename - Target filename
     * @param {object} results - Results object to update
     */
    async downloadJsonData(data, filename, results) {
        try {
            const jsonText = JSON.stringify(data, null, 2);
            const blob = new Blob([jsonText], { type: 'application/json' });
            const url = URL.createObjectURL(blob);

            await chrome.downloads.download({
                url: url,
                filename: filename,
                conflictAction: 'uniquify'
            });

            URL.revokeObjectURL(url);

            results.downloads.push({
                type: 'json',
                filename: filename,
                size: jsonText.length,
                records: Array.isArray(data) ? data.length : 1
            });
        } catch (error) {
            results.errors.push(`JSON download failed: ${error.message}`);
            this.logError('downloadJsonData', error, { filename });
        }
    }

    /**
     * Extract PDF URLs from work metadata
     * @param {object} metadata - Work metadata
     * @returns {Array} - Array of PDF URLs
     */
    extractPdfUrls(metadata) {
        const urls = [];

        // Primary open access location
        if (metadata.best_oa_location?.pdf_url) {
            urls.push(metadata.best_oa_location.pdf_url);
        }

        // Alternative open access locations
        if (metadata.open_access?.oa_locations) {
            metadata.open_access.oa_locations.forEach(location => {
                if (location.pdf_url && !urls.includes(location.pdf_url)) {
                    urls.push(location.pdf_url);
                }
            });
        }

        return urls;
    }

    /**
     * Format citations for download
     * @param {Array} citations - Raw citation data
     * @param {string} type - Citation type
     * @returns {object} - Formatted citation data
     */
    formatCitations(citations, type) {
        return {
            type: type,
            count: citations.length,
            generated_at: new Date().toISOString(),
            citations: citations.map(citation => ({
                id: citation.id,
                title: citation.title,
                authors: citation.authorships?.map(a => a.author?.display_name).filter(Boolean) || [],
                publication_year: citation.publication_year,
                venue: citation.primary_location?.source?.display_name,
                doi: citation.doi,
                open_access: citation.open_access?.is_oa || false,
                citation_count: citation.cited_by_count || 0
            }))
        };
    }

    /**
     * Get processing statistics
     * @param {object} results - Processing results
     * @returns {object} - Statistics summary
     */
    getProcessingStats(results) {
        const stats = {
            success: results.success,
            totalDownloads: results.downloads.length,
            errorCount: results.errors.length,
            downloadsByType: {}
        };

        // Count downloads by type
        results.downloads.forEach(download => {
            stats.downloadsByType[download.type] =
                (stats.downloadsByType[download.type] || 0) + 1;
        });

        return stats;
    }

    /**
     * Log debug information
     * @param {string} message - Debug message
     * @param {object} data - Additional data
     */
    logDebug(message, data = {}) {
        if (this.config.debug && this.config.logLevel === 'debug') {
            console.debug(`[CitationProcessor] ${message}`, data);
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
            console.error(`[CitationProcessor:${method}] ${error.message}`, { error, context });
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CitationProcessor;
} else {
    // Browser environment
    window.CitationProcessor = CitationProcessor;
}
