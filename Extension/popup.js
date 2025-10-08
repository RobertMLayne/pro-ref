/**
 * OpenAlex Citation Fetcher - Main Popup Script
 * Enhanced with modular architecture and comprehensive error handling
 */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
  try {
    await initializeExtension();
  } catch (error) {
    console.error('Failed to initialize extension:', error);
    showError('Extension initialization failed. Please reload.');
  }
});

/**
 * Initialize the extension popup
 */
async function initializeExtension() {
  // Check for stored data from context menu
  const data = await chrome.storage.local.get(['lastIdentifier', 'triggerPopup']);
  
  if (data.triggerPopup && data.lastIdentifier) {
    document.getElementById('identifier').value = data.lastIdentifier;
    await chrome.storage.local.remove('triggerPopup');
  }

  // Initialize UI components
  initializeUI();
  
  // Set up event listeners
  setupEventListeners();
  
  // Load user preferences
  await loadUserPreferences();
}

/**
 * Initialize UI components
 */
function initializeUI() {
  const statusDiv = document.getElementById('status');
  const errorDiv = document.getElementById('error');
  const progressDiv = createProgressIndicator();
  
  // Clear any existing content
  statusDiv.textContent = '';
  errorDiv.textContent = '';
  
  // Add progress indicator
  document.querySelector('.container').appendChild(progressDiv);
}

/**
 * Create progress indicator element
 */
function createProgressIndicator() {
  const progressDiv = document.createElement('div');
  progressDiv.id = 'progress';
  progressDiv.style.cssText = `
    margin-top: 10px;
    padding: 5px;
    background: #f0f0f0;
    border-radius: 3px;
    display: none;
  `;
  return progressDiv;
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
  const idInput = document.getElementById('identifier');
  const fetchBtn = document.getElementById('fetchBtn');
  
  // Main fetch button
  fetchBtn.addEventListener('click', handleFetchRequest);
  
  // Enter key support
  idInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
      handleFetchRequest();
    }
  });
  
  // Input validation
  idInput.addEventListener('input', validateInput);
  
  // Help button (if exists)
  const helpBtn = document.getElementById('helpBtn');
  if (helpBtn) {
    helpBtn.addEventListener('click', showHelpDialog);
  }
}

/**
 * Load user preferences from storage
 */
async function loadUserPreferences() {
  try {
    const prefs = await chrome.storage.sync.get([
      'defaultFlags',
      'autoDownloadPdf',
      'fileNamingPattern'
    ]);
    
    // Apply preferences to UI
    if (prefs.defaultFlags) {
      // Could add checkboxes for default flags
    }
  } catch (error) {
    console.warn('Failed to load user preferences:', error);
  }
}

/**
 * Handle fetch request from user
 */
async function handleFetchRequest() {
  const idInput = document.getElementById('identifier');
  const fetchBtn = document.getElementById('fetchBtn');
  
  // Clear previous results
  clearMessages();
  
  const identifier = idInput.value.trim();
  if (!identifier) {
    showError(CONFIG.errorMessages.noIdentifier);
    return;
  }

  // Disable UI during processing
  setUIState(false);
  showProgress('Initializing...');

  try {
    // Initialize processor
    const processor = new CitationProcessor(CONFIG);
    
    // Parse identifier and flags
    const parser = new IdentifierParser(CONFIG);
    const parseResult = parser.parseInput(identifier);
    
    if (parseResult.error) {
      throw new Error(parseResult.error);
    }

    const { flags } = parseResult;
    
    // Update progress
    showProgress('Fetching metadata...');
    
    // Process citation
    const results = await processor.processCitation(identifier, flags);
    
    // Handle results
    await handleProcessingResults(results);
    
  } catch (error) {
    console.error('Fetch request failed:', error);
    showError(`Error: ${error.message}`);
  } finally {
    // Re-enable UI
    setUIState(true);
    hideProgress();
  }
}

/**
 * Handle processing results
 */
async function handleProcessingResults(results) {
  if (!results.success) {
    throw new Error(results.errors.join('; '));
  }

  // Show success message with statistics
  const stats = new CitationProcessor().getProcessingStats(results);
  showSuccess(formatSuccessMessage(stats));
  
  // Store processing results for future reference
  await chrome.storage.local.set({
    lastResults: {
      timestamp: Date.now(),
      stats: stats,
      downloads: results.downloads
    }
  });
  
  // Show download details if in debug mode
  if (CONFIG.debug) {
    console.log('Processing results:', results);
  }
}

/**
 * Format success message
 */
function formatSuccessMessage(stats) {
  let message = '✅ Complete! ';
  
  if (stats.totalDownloads > 0) {
    message += `Downloaded ${stats.totalDownloads} file(s)`;
    
    const types = Object.keys(stats.downloadsByType);
    if (types.length > 1) {
      message += ` (${types.map(type => 
        `${stats.downloadsByType[type]} ${type.toUpperCase()}`
      ).join(', ')})`;
    }
  } else {
    message += 'No downloads available';
  }
  
  return message;
}

/**
 * Validate input as user types
 */
function validateInput() {
  const idInput = document.getElementById('identifier');
  const fetchBtn = document.getElementById('fetchBtn');
  const identifier = idInput.value.trim();
  
  if (!identifier) {
    fetchBtn.disabled = true;
    return;
  }
  
  // Basic validation
  const parser = new IdentifierParser(CONFIG);
  const isValid = parser.isValidIdentifier(identifier.split(/\s+/)[0]);
  
  fetchBtn.disabled = !isValid;
  
  // Visual feedback
  idInput.style.borderColor = isValid ? '' : '#ff6b6b';
}

/**
 * Show help dialog
 */
function showHelpDialog() {
  const helpContent = `
    Supported identifiers:
    • DOI: 10.1038/nature12373
    • PubMed ID: pmid:23685631
    • PMC ID: PMC4123456
    • arXiv ID: 1234.5678
    • OpenAlex ID: W2123456789
    
    Flags:
    • --WC: Download referenced works
    • --SW: Download citing works
    
    Example: "10.1038/nature12373 --WC"
  `;
  
  alert(helpContent);
}

/**
 * Set UI state (enabled/disabled)
 */
function setUIState(enabled) {
  const idInput = document.getElementById('identifier');
  const fetchBtn = document.getElementById('fetchBtn');
  
  idInput.disabled = !enabled;
  fetchBtn.disabled = !enabled;
  fetchBtn.textContent = enabled ? 'Fetch' : 'Processing...';
}

/**
 * Show progress message
 */
function showProgress(message) {
  const progressDiv = document.getElementById('progress');
  progressDiv.textContent = message;
  progressDiv.style.display = 'block';
}

/**
 * Hide progress indicator
 */
function hideProgress() {
  const progressDiv = document.getElementById('progress');
  progressDiv.style.display = 'none';
}

/**
 * Clear all messages
 */
function clearMessages() {
  document.getElementById('status').textContent = '';
  document.getElementById('error').textContent = '';
}

/**
 * Show success message
 */
function showSuccess(message) {
  const statusDiv = document.getElementById('status');
  statusDiv.textContent = message;
  statusDiv.style.color = 'green';
}

/**
 * Show error message
 */
function showError(message) {
  const errorDiv = document.getElementById('error');
  errorDiv.textContent = message;
  errorDiv.style.color = 'red';
}

/**
 * Handle extension errors gracefully
 */
window.addEventListener('error', (event) => {
  console.error('Popup error:', event.error);
  showError('An unexpected error occurred. Please try again.');
});

/**
 * Handle unhandled promise rejections
 */
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  showError('An unexpected error occurred. Please try again.');
  event.preventDefault();
});