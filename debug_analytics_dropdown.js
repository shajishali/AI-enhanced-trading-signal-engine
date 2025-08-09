// Enhanced Analytics Dropdown Debug Script
// Add this to your browser console to debug dropdown issues

console.log('=== Enhanced Analytics Dropdown Debug Script ===');

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, starting debug...');
    
    // Check dropdown elements
    const analyticsDropdown = document.querySelector('#nav-analytics');
    const dropdownMenu = analyticsDropdown ? analyticsDropdown.nextElementSibling : null;
    
    console.log('Analytics dropdown found:', !!analyticsDropdown);
    console.log('Dropdown menu found:', !!dropdownMenu);
    
    if (analyticsDropdown) {
        console.log('Analytics dropdown classes:', analyticsDropdown.className);
        console.log('Analytics dropdown attributes:', {
            'data-bs-toggle': analyticsDropdown.getAttribute('data-bs-toggle'),
            'aria-expanded': analyticsDropdown.getAttribute('aria-expanded'),
            'id': analyticsDropdown.getAttribute('id'),
            'href': analyticsDropdown.getAttribute('href')
        });
        
        // Check if Bootstrap is available
        if (typeof bootstrap !== 'undefined') {
            console.log('Bootstrap is available');
            const dropdown = bootstrap.Dropdown.getInstance(analyticsDropdown);
            console.log('Bootstrap dropdown instance:', dropdown);
        } else {
            console.log('Bootstrap is NOT available');
        }
    }
    
    if (dropdownMenu) {
        console.log('Dropdown menu classes:', dropdownMenu.className);
        console.log('Dropdown menu style:', {
            display: dropdownMenu.style.display,
            visibility: dropdownMenu.style.visibility,
            opacity: dropdownMenu.style.opacity,
            zIndex: dropdownMenu.style.zIndex,
            position: dropdownMenu.style.position
        });
        
        // Check dropdown items
        const dropdownItems = dropdownMenu.querySelectorAll('.dropdown-item');
        console.log('Dropdown items found:', dropdownItems.length);
        
        dropdownItems.forEach((item, index) => {
            console.log(`Dropdown item ${index + 1}:`, {
                text: item.textContent.trim(),
                href: item.getAttribute('href'),
                classes: item.className
            });
        });
    }
    
    // Test dropdown functionality
    function testAnalyticsDropdown() {
        console.log('Testing analytics dropdown...');
        
        if (analyticsDropdown) {
            // Try Bootstrap dropdown
            if (typeof bootstrap !== 'undefined') {
                try {
                    const dropdown = bootstrap.Dropdown.getInstance(analyticsDropdown);
                    if (dropdown) {
                        dropdown.toggle();
                        console.log('Bootstrap dropdown toggled');
                    } else {
                        console.log('No Bootstrap dropdown instance found');
                    }
                } catch (error) {
                    console.error('Bootstrap dropdown error:', error);
                }
            }
            
            // Manual toggle test
            if (dropdownMenu) {
                const isVisible = dropdownMenu.classList.contains('show');
                console.log('Dropdown currently visible:', isVisible);
                
                if (isVisible) {
                    dropdownMenu.classList.remove('show');
                    dropdownMenu.style.display = 'none';
                    console.log('Dropdown manually hidden');
                } else {
                    dropdownMenu.classList.add('show');
                    dropdownMenu.style.display = 'block';
                    dropdownMenu.style.visibility = 'visible';
                    dropdownMenu.style.opacity = '1';
                    console.log('Dropdown manually shown');
                }
            }
        }
    }
    
    // Make function globally available
    window.testAnalyticsDropdown = testAnalyticsDropdown;
    
    console.log('Debug script loaded. Run testAnalyticsDropdown() to test the dropdown.');
    
    // Auto-test after a delay
    setTimeout(testAnalyticsDropdown, 1000);
});

// Additional debugging functions
window.debugAnalyticsDropdown = {
    // Check all dropdown elements
    checkElements: function() {
        const elements = {
            toggle: document.getElementById('nav-analytics'),
            menu: document.getElementById('analytics-dropdown-menu'),
            container: document.getElementById('analytics-dropdown-container')
        };
        
        console.log('Analytics dropdown elements:', elements);
        return elements;
    },
    
    // Check CSS styles
    checkStyles: function() {
        const menu = document.getElementById('analytics-dropdown-menu');
        if (menu) {
            const styles = window.getComputedStyle(menu);
            console.log('Dropdown menu computed styles:', {
                display: styles.display,
                visibility: styles.visibility,
                opacity: styles.opacity,
                position: styles.position,
                zIndex: styles.zIndex,
                top: styles.top,
                left: styles.left
            });
        }
    },
    
    // Force show dropdown
    forceShow: function() {
        const menu = document.getElementById('analytics-dropdown-menu');
        if (menu) {
            menu.classList.add('show');
            menu.style.display = 'block';
            menu.style.visibility = 'visible';
            menu.style.opacity = '1';
            menu.style.zIndex = '10000';
            console.log('Dropdown forced to show');
        }
    },
    
    // Force hide dropdown
    forceHide: function() {
        const menu = document.getElementById('analytics-dropdown-menu');
        if (menu) {
            menu.classList.remove('show');
            menu.style.display = 'none';
            menu.style.visibility = 'hidden';
            menu.style.opacity = '0';
            console.log('Dropdown forced to hide');
        }
    },
    
    // Test click events
    testClick: function() {
        const toggle = document.getElementById('nav-analytics');
        if (toggle) {
            console.log('Simulating click on analytics dropdown...');
            toggle.click();
        }
    }
};

console.log('Debug functions available:');
console.log('- debugAnalyticsDropdown.checkElements()');
console.log('- debugAnalyticsDropdown.checkStyles()');
console.log('- debugAnalyticsDropdown.forceShow()');
console.log('- debugAnalyticsDropdown.forceHide()');
console.log('- debugAnalyticsDropdown.testClick()');
console.log('- testAnalyticsDropdown()');
