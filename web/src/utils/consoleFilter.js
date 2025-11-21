/**
 * Filter out known harmless browser extension errors from console
 * This helps keep the console clean by suppressing extension-related errors
 * 
 * Note: Browser extensions (ad blockers, password managers, etc.) often generate
 * console errors that are harmless and don't affect application functionality.
 */

export const setupConsoleFilter = () => {
  // Only filter in production, show in dev for debugging
  const isDevelopment = import.meta.env.DEV;
  
  // Override console.error to filter out extension errors
  const originalError = console.error;
  
  console.error = (...args) => {
    // Check if this is a browser extension error
    const errorMessage = args.join(' ').toLowerCase();
    
    // Common extension error patterns
    const extensionErrorPatterns = [
      'unchecked runtime.lasterror',
      'listener indicated an asynchronous response',
      'message channel closed',
      'extension context invalidated',
      'could not establish connection',
      'receiving end does not exist',
    ];
    
    // Check if it matches any extension error pattern
    const isExtensionError = extensionErrorPatterns.some(pattern => 
      errorMessage.includes(pattern.toLowerCase())
    );
    
    if (isExtensionError) {
      // In development, show as debug message
      if (isDevelopment) {
        console.debug('[Extension Error (Harmless)]', ...args);
      }
      // In production, suppress completely
      return;
    }
    
    // Log all other errors normally
    originalError.apply(console, args);
  };
  
  // Also filter console.warn for extension warnings
  const originalWarn = console.warn;
  
  console.warn = (...args) => {
    const warningMessage = args.join(' ').toLowerCase();
    
    const extensionWarningPatterns = [
      'runtime.lasterror',
      'extension',
      'chrome-extension://',
    ];
    
    const isExtensionWarning = extensionWarningPatterns.some(pattern =>
      warningMessage.includes(pattern.toLowerCase())
    ) && warningMessage.includes('lasterror');
    
    if (isExtensionWarning) {
      if (isDevelopment) {
        console.debug('[Extension Warning (Harmless)]', ...args);
      }
      return;
    }
    
    originalWarn.apply(console, args);
  };
};

/**
 * Alternative: Use a simple error wrapper that filters extension errors
 * Call this in your main app initialization
 */
export const filterExtensionErrors = (error) => {
  const errorString = error?.message || error?.toString() || '';
  
  const extensionErrorPatterns = [
    /runtime\.lastError/i,
    /asynchronous response/i,
    /message channel closed/i,
    /Extension context/i,
    /Could not establish connection/i,
  ];
  
  return extensionErrorPatterns.some(pattern => pattern.test(errorString));
};

