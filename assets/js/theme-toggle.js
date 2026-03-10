// Theme Toggle Functionality for Dark/Light Mode
// ================================================

document.addEventListener('DOMContentLoaded', function() {
  
  // Elements
  const themeToggle = document.getElementById('theme-toggle');
  const htmlElement = document.documentElement;
  const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
  const navMenu = document.getElementById('nav-menu');
  const navLinks = document.querySelectorAll('.nav-link');
  
  // ============================================
  // Theme Toggle
  // ============================================
  
  // Check for saved theme preference or default to 'light'
  const currentTheme = localStorage.getItem('theme') || 'light';
  htmlElement.setAttribute('data-theme', currentTheme);
  
  // Theme toggle click handler
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      const current = htmlElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      
      // Update theme
      htmlElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      
      // Optional: Add a brief animation class
      themeToggle.style.transform = 'rotate(360deg)';
      setTimeout(() => {
        themeToggle.style.transform = 'rotate(0deg)';
      }, 300);
    });
  }
  
  // ============================================
  // Mobile Menu Toggle
  // ============================================
  
  if (mobileMenuToggle && navMenu) {
    mobileMenuToggle.addEventListener('click', function() {
      navMenu.classList.toggle('active');
      mobileMenuToggle.classList.toggle('active');
      
      // Prevent body scroll when menu is open
      if (navMenu.classList.contains('active')) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
    });
    
    // Close menu when clicking on a link
    navLinks.forEach(link => {
      link.addEventListener('click', function() {
        navMenu.classList.remove('active');
        mobileMenuToggle.classList.remove('active');
        document.body.style.overflow = '';
      });
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
      const isClickInsideNav = navMenu.contains(event.target);
      const isClickOnToggle = mobileMenuToggle.contains(event.target);
      
      if (!isClickInsideNav && !isClickOnToggle && navMenu.classList.contains('active')) {
        navMenu.classList.remove('active');
        mobileMenuToggle.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }
  
  // ============================================
  // Smooth Scroll with Active Link Highlighting
  // ============================================
  
  // Highlight active section in navigation
  function highlightActiveSection() {
    const sections = document.querySelectorAll('section[id], .hero');
    const scrollPosition = window.scrollY + 100;
    
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      const sectionId = section.getAttribute('id');
      
      if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
        navLinks.forEach(link => {
          link.classList.remove('active');
          if (link.getAttribute('href') === `#${sectionId}`) {
            link.classList.add('active');
          }
        });
      }
    });
  }
  
  // Add scroll event listener for active section highlighting
  let scrollTimeout;
  window.addEventListener('scroll', function() {
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(highlightActiveSection, 50);
  });
  
  // ============================================
  // Navbar Background on Scroll
  // ============================================
  
  const navbar = document.getElementById('navbar');
  
  function updateNavbarOnScroll() {
    if (window.scrollY > 50) {
      navbar.style.boxShadow = '0 2px 10px var(--shadow-md)';
    } else {
      navbar.style.boxShadow = 'none';
    }
  }
  
  window.addEventListener('scroll', updateNavbarOnScroll);
  
  // ============================================
  // Detect System Theme Preference (Optional)
  // ============================================
  
  // If user hasn't set a preference, detect system preference
  if (!localStorage.getItem('theme')) {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const systemTheme = prefersDark ? 'dark' : 'light';
    htmlElement.setAttribute('data-theme', systemTheme);
    localStorage.setItem('theme', systemTheme);
  }
  
  // Listen for system theme changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    // Only auto-update if user hasn't manually set a preference
    const manuallySet = localStorage.getItem('theme-manually-set');
    if (!manuallySet) {
      const newTheme = e.matches ? 'dark' : 'light';
      htmlElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
    }
  });
  
  // Mark that user has manually set theme when they click the toggle
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      localStorage.setItem('theme-manually-set', 'true');
    });
  }
  
  // ============================================
  // Add Animation on Page Load
  // ============================================
  
  // Fade in content
  document.body.style.opacity = '0';
  setTimeout(() => {
    document.body.style.transition = 'opacity 0.5s ease';
    document.body.style.opacity = '1';
  }, 100);
  
});
