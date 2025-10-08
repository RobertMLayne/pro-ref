/**
 * Test configuration for Jest
 */
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testMatch: [
    '<rootDir>/tests/**/*.test.js'
  ],
  collectCoverageFrom: [
    'Extension/**/*.js',
    '!Extension/config.js',
    '!Extension/popup.js' // Skip main popup for now
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  verbose: true,
  globals: {
    chrome: {}
  }
};