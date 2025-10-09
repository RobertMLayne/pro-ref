/**
 * Test setup for Jest environment
 */

// Mock Chrome APIs
global.chrome = {
    storage: {
        local: {
            get: jest.fn(),
            set: jest.fn(),
            remove: jest.fn()
        },
        sync: {
            get: jest.fn(),
            set: jest.fn()
        }
    },
    downloads: {
        download: jest.fn()
    },
    contextMenus: {
        create: jest.fn(),
        onClicked: {
            addListener: jest.fn()
        }
    },
    runtime: {
        onInstalled: {
            addListener: jest.fn()
        }
    }
};

// Mock fetch API
global.fetch = jest.fn();

// Mock URL.createObjectURL
global.URL = {
    createObjectURL: jest.fn(() => 'mock-blob-url'),
    revokeObjectURL: jest.fn()
};

// Mock Blob
global.Blob = jest.fn();

// Mock console methods in tests
global.console = {
    ...console,
    log: jest.fn(),
    error: jest.fn(),
    warn: jest.fn(),
    debug: jest.fn()
};
