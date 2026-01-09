/**
 * Initialize Google Sign-In
 * @param {string} clientId - Google OAuth Client ID
 * @param {Function} callback - Callback function to handle the credential response
 */
export const initializeGoogleSignIn = (clientId, callback) => {
  if (typeof window === 'undefined' || !window.google) {
    console.error('Google Identity Services library not loaded');
    return;
  }

  window.google.accounts.id.initialize({
    client_id: clientId,
    callback: callback,
  });
};

/**
 * Render Google Sign-In button
 * @param {string} elementId - ID of the element to render the button
 * @param {Object} options - Button customization options
 */
export const renderGoogleButton = (elementId, options = {}) => {
  if (typeof window === 'undefined' || !window.google) {
    console.error('Google Identity Services library not loaded');
    return;
  }

  const element = document.getElementById(elementId);
  if (!element) {
    console.error(`Element with id "${elementId}" not found`);
    // Retry after a short delay in case DOM isn't ready
    setTimeout(() => {
      const retryElement = document.getElementById(elementId);
      if (retryElement) {
        const defaultOptions = {
          type: 'standard',
          theme: 'outline',
          size: 'large',
          text: 'signin_with',
          width: '100%',
          ...options,
        };
        window.google.accounts.id.renderButton(retryElement, defaultOptions);
      }
    }, 100);
    return;
  }

  const defaultOptions = {
    type: 'standard',
    theme: 'outline',
    size: 'large',
    text: 'signin_with',
    width: '100%',
    ...options,
  };

  window.google.accounts.id.renderButton(element, defaultOptions);
};

/**
 * Prompt Google Sign-In
 */
export const promptGoogleSignIn = () => {
  if (typeof window === 'undefined' || !window.google) {
    console.error('Google Identity Services library not loaded');
    return;
  }

  window.google.accounts.id.prompt();
};

