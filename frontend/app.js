// Event Search Frontend JavaScript

class EventSearch {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000';
        this.events = [];
        this.currentFilters = {
            query: '',
            location: '',
            category: '',
            date: '',
            price: ''
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadEvents();
    }

    bindEvents() {
        // Search form submission
        const searchForm = document.querySelector('form') || this.createSearchForm();
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => this.handleSearch(e));
        }

        // Filter changes
        const filterSelects = document.querySelectorAll('select');
        filterSelects.forEach(select => {
            select.addEventListener('change', (e) => this.handleFilterChange(e));
        });

        // Load more button
        const loadMoreBtn = document.querySelector('button[class*="Load More"]');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', () => this.loadMoreEvents());
        }

        // Search button click
        const searchBtn = document.querySelector('button[class*="Search Events"]');
        if (searchBtn) {
            searchBtn.addEventListener('click', () => this.handleSearchClick());
        }
    }

    createSearchForm() {
        const searchContainer = document.querySelector('.max-w-2xl');
        if (searchContainer) {
            const form = document.createElement('form');
            form.className = 'flex flex-col md:flex-row gap-4';
            form.innerHTML = searchContainer.innerHTML;
            searchContainer.innerHTML = '';
            searchContainer.appendChild(form);
            return form;
        }
        return null;
    }

    async handleSearch(event) {
        event.preventDefault();
        const formData = new FormData(event.target);
        this.currentFilters.query = formData.get('query') || '';
        this.currentFilters.location = formData.get('location') || '';
        
        await this.searchEvents();
    }

    handleSearchClick() {
        const queryInput = document.querySelector('input[placeholder*="looking for"]');
        const locationInput = document.querySelector('input[placeholder="Location"]');
        
        if (queryInput) this.currentFilters.query = queryInput.value;
        if (locationInput) this.currentFilters.location = locationInput.value;
        
        this.searchEvents();
    }

    handleFilterChange(event) {
        const select = event.target;
        const value = select.value;
        
        // Determine filter type based on select options
        if (select.options[0]?.text.includes('Categories')) {
            this.currentFilters.category = value;
        } else if (select.options[0]?.text.includes('Date')) {
            this.currentFilters.date = value;
        } else if (select.options[0]?.text.includes('Price')) {
            this.currentFilters.price = value;
        }
        
        this.searchEvents();
    }

    async searchEvents() {
        try {
            this.showLoading();
            
            // Simulate API call (replace with actual API endpoint)
            const response = await this.mockApiCall();
            this.events = response.events;
            this.renderEvents();
            
        } catch (error) {
            console.error('Error searching events:', error);
            this.showError('Failed to search events. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    async loadEvents() {
        try {
            this.showLoading();
            
            // Load initial events
            const response = await this.mockApiCall();
            this.events = response.events;
            this.renderEvents();
            
        } catch (error) {
            console.error('Error loading events:', error);
            this.showError('Failed to load events. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    async loadMoreEvents() {
        try {
            this.showLoading();
            
            // Simulate loading more events
            const response = await this.mockApiCall();
            this.events = [...this.events, ...response.events];
            this.renderEvents();
            
        } catch (error) {
            console.error('Error loading more events:', error);
            this.showError('Failed to load more events. Please try again.');
        } finally {
            this.hideLoading();
        }
    }

    renderEvents() {
        const eventsContainer = document.querySelector('.grid.grid-cols-1');
        if (!eventsContainer) return;

        // Clear existing events (except the template cards)
        const existingEvents = eventsContainer.querySelectorAll('.event-card');
        existingEvents.forEach(event => event.remove());

        // Render new events
        this.events.forEach(event => {
            const eventCard = this.createEventCard(event);
            eventsContainer.appendChild(eventCard);
        });
    }

    createEventCard(event) {
        const card = document.createElement('div');
        card.className = 'event-card bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow';
        
        const gradientColors = [
            'from-primary to-secondary',
            'from-green-400 to-blue-500',
            'from-purple-400 to-pink-500',
            'from-yellow-400 to-orange-500',
            'from-red-400 to-pink-500'
        ];
        
        const randomGradient = gradientColors[Math.floor(Math.random() * gradientColors.length)];
        
        card.innerHTML = `
            <div class="h-48 bg-gradient-to-br ${randomGradient}"></div>
            <div class="p-6">
                <div class="flex items-center mb-2">
                    <span class="bg-${this.getCategoryColor(event.category)} text-white px-2 py-1 rounded text-sm font-medium">${event.category}</span>
                    <span class="ml-2 text-gray-500 text-sm">${this.formatDate(event.date)}</span>
                </div>
                <h4 class="text-xl font-semibold text-gray-900 mb-2">${event.title}</h4>
                <p class="text-gray-600 mb-4">${event.description}</p>
                <div class="flex items-center justify-between">
                    <span class="text-gray-500">📍 ${event.location}</span>
                    <span class="${event.price === 0 ? 'text-green-600' : 'text-primary'} font-semibold">${event.price === 0 ? 'Free' : '$' + event.price}</span>
                </div>
            </div>
        `;
        
        return card;
    }

    getCategoryColor(category) {
        const colors = {
            'Music': 'accent',
            'Technology': 'green-500',
            'Sports': 'blue-500',
            'Arts': 'purple-500',
            'Business': 'gray-500'
        };
        return colors[category] || 'gray-500';
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric' 
        });
    }

    async mockApiCall() {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock data
        return {
            events: [
                {
                    id: 1,
                    title: "Jazz Night at Blue Note",
                    description: "Experience an evening of smooth jazz with talented local musicians.",
                    location: "Blue Note Cafe, Downtown",
                    date: "2024-12-18T20:00:00Z",
                    price: 25,
                    category: "Music"
                },
                {
                    id: 2,
                    title: "Startup Pitch Competition",
                    description: "Watch innovative startups pitch their ideas to a panel of investors.",
                    location: "Innovation Hub",
                    date: "2024-12-19T14:00:00Z",
                    price: 0,
                    category: "Business"
                },
                {
                    id: 3,
                    title: "Yoga in the Park",
                    description: "Join us for a relaxing morning yoga session in the beautiful city park.",
                    location: "Central Park Pavilion",
                    date: "2024-12-21T09:00:00Z",
                    price: 15,
                    category: "Sports"
                }
            ]
        };
    }

    showLoading() {
        // Add loading indicator
        const loadMoreBtn = document.querySelector('button[class*="Load More"]');
        if (loadMoreBtn) {
            loadMoreBtn.textContent = 'Loading...';
            loadMoreBtn.disabled = true;
        }
    }

    hideLoading() {
        // Remove loading indicator
        const loadMoreBtn = document.querySelector('button[class*="Load More"]');
        if (loadMoreBtn) {
            loadMoreBtn.textContent = 'Load More Events';
            loadMoreBtn.disabled = false;
        }
    }

    showError(message) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EventSearch();
});

// Export for potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = EventSearch;
}