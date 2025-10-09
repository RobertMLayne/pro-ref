/**
 * Unit tests for IdentifierParser
 */

const CONFIG = require('../Extension/config.js');
const IdentifierParser = require('../Extension/utils/identifier-parser.js');

describe('IdentifierParser', () => {
    let parser;

    beforeEach(() => {
        parser = new IdentifierParser(CONFIG);
    });

    describe('parseInput', () => {
        test('should parse DOI correctly', () => {
            const result = parser.parseInput('10.1038/nature12373');
            expect(result.error).toBeUndefined();
            expect(result.lookup).toBe('https://doi.org/10.1038/nature12373');
            expect(result.prefix).toBe('doi');
        });

        test('should parse DOI with prefix', () => {
            const result = parser.parseInput('doi:10.1038/nature12373');
            expect(result.error).toBeUndefined();
            expect(result.lookup).toBe('https://doi.org/10.1038/nature12373');
            expect(result.prefix).toBe('doi');
        });

        test('should parse arXiv ID', () => {
            const result = parser.parseInput('1234.5678');
            expect(result.error).toBeUndefined();
            expect(result.lookup).toBe('https://arxiv.org/abs/1234.5678');
            expect(result.prefix).toBe('arxiv');
        });

        test('should parse OpenAlex ID', () => {
            const result = parser.parseInput('W2123456789');
            expect(result.error).toBeUndefined();
            expect(result.lookup).toBe('W2123456789');
            expect(result.prefix).toBe('openalex');
        });

        test('should parse PMC ID', () => {
            const result = parser.parseInput('PMC4123456');
            expect(result.error).toBeUndefined();
            expect(result.lookup).toBe('https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4123456');
            expect(result.prefix).toBe('pmcid');
        });

        test('should require prefix for numeric IDs', () => {
            const result = parser.parseInput('12345');
            expect(result.error).toBe(CONFIG.errorMessages.requiresPrefix);
        });

        test('should parse flags correctly', () => {
            const result = parser.parseInput('10.1038/nature12373 --WC --SW');
            expect(result.error).toBeUndefined();
            expect(result.flags.has('--WC')).toBe(true);
            expect(result.flags.has('--SW')).toBe(true);
        });

        test('should handle empty input', () => {
            const result = parser.parseInput('');
            expect(result.error).toBe(CONFIG.errorMessages.noIdentifier);
        });

        test('should handle invalid format', () => {
            const result = parser.parseInput('invalid-format');
            expect(result.error).toBe(CONFIG.errorMessages.unrecognizedFormat);
        });
    });

    describe('sanitizeFilename', () => {
        test('should sanitize special characters', () => {
            const result = parser.sanitizeFilename('test/file:name?<>');
            expect(result).toBe('test_file_name');
        });

        test('should handle multiple spaces', () => {
            const result = parser.sanitizeFilename('test   multiple   spaces');
            expect(result).toBe('test_multiple_spaces');
        });

        test('should remove leading/trailing underscores', () => {
            const result = parser.sanitizeFilename('_test_file_');
            expect(result).toBe('test_file');
        });
    });

    describe('isValidIdentifier', () => {
        test('should validate DOI', () => {
            expect(parser.isValidIdentifier('10.1038/nature12373')).toBe(true);
            expect(parser.isValidIdentifier('invalid-doi')).toBe(false);
        });

        test('should validate with expected prefix', () => {
            expect(parser.isValidIdentifier('doi:10.1038/nature12373', 'doi')).toBe(true);
            expect(parser.isValidIdentifier('arxiv:1234.5678', 'doi')).toBe(false);
        });
    });

    describe('getSupportedTypes', () => {
        test('should return array of supported types', () => {
            const types = parser.getSupportedTypes();
            expect(Array.isArray(types)).toBe(true);
            expect(types).toContain('doi');
            expect(types).toContain('arxiv');
            expect(types).toContain('openalex');
        });
    });
});
