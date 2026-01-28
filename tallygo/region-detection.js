// Region Detection and Auto-Routing
(function() {
  'use strict';
  
  // Detect user's region based on IP, language, or other factors
  function detectRegion() {
    // Check URL parameters first
    const urlParams = new URLSearchParams(window.location.search);
    const regionParam = urlParams.get('region');
    if (regionParam === 'india' || regionParam === 'global') {
      return regionParam;
    }
    
    // Check if we're already on a region-specific page
    const currentPath = window.location.pathname;
    if (currentPath.includes('global.html')) {
      return 'global';
    }
    if (currentPath.includes('index.html') || currentPath === '/') {
      return 'india';
    }
    
    // Auto-detect based on browser language and timezone
    const language = navigator.language || navigator.userLanguage;
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    
    // Indian indicators
    const indianIndicators = [
      'hi-IN', 'en-IN', 'gu-IN', 'ta-IN', 'te-IN', 'bn-IN', 'mr-IN', 'pa-IN',
      'Asia/Kolkata', 'Asia/Calcutta', 'Asia/Mumbai', 'Asia/Delhi'
    ];
    
    const isIndianRegion = indianIndicators.some(indicator => 
      language.includes(indicator) || timezone.includes(indicator)
    );
    
    return isIndianRegion ? 'india' : 'global';
  }
  
  // Redirect to appropriate version
  function redirectToRegion() {
    const region = detectRegion();
    const currentPath = window.location.pathname;
    
    // Don't redirect if already on correct page
    if (region === 'india' && (currentPath.includes('index.html') || currentPath === '/')) {
      return;
    }
    if (region === 'global' && currentPath.includes('global.html')) {
      return;
    }
    
    // Redirect to appropriate version
    if (region === 'india') {
      if (currentPath.includes('global.html')) {
        window.location.href = '/index.html';
      }
    } else if (region === 'global') {
      if (currentPath.includes('index.html') || currentPath === '/') {
        window.location.href = '/global.html';
      }
    }
  }
  
  // Add region switcher to navigation
  function addRegionSwitcher() {
    const region = detectRegion();
    const nav = document.querySelector('.nav__menu');
    if (!nav) return;
    
    const switcher = document.createElement('li');
    switcher.innerHTML = `
      <div class="region-switcher">
        <button class="region-btn ${region === 'india' ? 'active' : ''}" data-region="india">
          🇮🇳 India
        </button>
        <button class="region-btn ${region === 'global' ? 'active' : ''}" data-region="global">
          🌍 Global
        </button>
      </div>
    `;
    
    nav.insertBefore(switcher, nav.lastElementChild);
    
    // Add click handlers
    switcher.addEventListener('click', (e) => {
      if (e.target.classList.contains('region-btn')) {
        const targetRegion = e.target.dataset.region;
        if (targetRegion === 'india') {
          window.location.href = '/index.html';
        } else if (targetRegion === 'global') {
          window.location.href = '/global.html';
        }
      }
    });
  }
  
  // Initialize region detection
  function init() {
    // Only redirect if not on a specific region page
    const currentPath = window.location.pathname;
    if (currentPath === '/' || currentPath === '/index.html' || currentPath === '/global.html') {
      redirectToRegion();
    }
    
    // Add region switcher after DOM is loaded
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', addRegionSwitcher);
    } else {
      addRegionSwitcher();
    }
  }
  
  // Run initialization
  init();
})();
