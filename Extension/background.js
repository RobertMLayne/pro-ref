const MENU_ID = 'fetchCitation';

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: MENU_ID,
    title: 'Fetch Citation Metadata',
    contexts: ['selection'],
  });
});

chrome.contextMenus.onClicked.addListener(async (info) => {
  if (info.menuItemId !== MENU_ID || !info.selectionText) return;

  try {
    await chrome.storage.local.set({
      lastIdentifier: info.selectionText.trim(),
      triggerPopup: true,
    });
    // User must manually open popup (by clicking icon)
  } catch (error) {
    console.error('Storage error:', error);
  }
});
