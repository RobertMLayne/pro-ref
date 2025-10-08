#!/usr/bin/env node

/**
 * Build script for the OpenAlex Citation Fetcher extension
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BUILD_DIR = 'dist';
const EXTENSION_DIR = 'Extension';

console.log('🏗️  Building OpenAlex Citation Fetcher...\n');

// Clean build directory
if (fs.existsSync(BUILD_DIR)) {
  fs.rmSync(BUILD_DIR, { recursive: true });
  console.log('✅ Cleaned build directory');
}

// Create build directory
fs.mkdirSync(BUILD_DIR, { recursive: true });
console.log('✅ Created build directory');

// Copy extension files
console.log('📁 Copying extension files...');
copyDirectory(EXTENSION_DIR, path.join(BUILD_DIR, 'extension'));

// Run tests
console.log('\n🧪 Running tests...');
try {
  execSync('npm test', { stdio: 'inherit' });
  console.log('✅ All tests passed');
} catch (error) {
  console.error('❌ Tests failed');
  process.exit(1);
}

// Run linting
console.log('\n🔍 Linting code...');
try {
  execSync('npm run lint', { stdio: 'inherit' });
  console.log('✅ Linting passed');
} catch (error) {
  console.error('❌ Linting failed');
  process.exit(1);
}

// Create package
console.log('\n📦 Creating package...');
try {
  execSync(`cd ${BUILD_DIR} && zip -r ../openalex-citation-fetcher.zip extension/`, { stdio: 'inherit' });
  console.log('✅ Package created: openalex-citation-fetcher.zip');
} catch (error) {
  console.error('❌ Package creation failed');
  process.exit(1);
}

console.log('\n🎉 Build completed successfully!');

/**
 * Copy directory recursively
 */
function copyDirectory(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  
  const entries = fs.readdirSync(src, { withFileTypes: true });
  
  for (let entry of entries) {
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    
    if (entry.isDirectory()) {
      copyDirectory(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}