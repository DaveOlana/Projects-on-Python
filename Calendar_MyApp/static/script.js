// ===========================
// CalendME - Smart Schedule Builder
// JavaScript Core Functionality
// ===========================

// State Management
let events = [];
let currentTheme = 'light';
let selectedPriority = 'green';
let editingEventId = null;

// DOM Elements
const naturalInput = document.getElementById('natural-input');
const addEventBtn = document.getElementById('add-event-btn');
const eventsContainer = document.getElementById('events-container');
const emptyState = document.getElementById('empty-state');
const eventCountEl = document.getElementById('event-count');
const parseFeedback = document.getElementById('parse-feedback');
const exportBtn = document.getElementById('export-ics-btn');
const themeToggle = document.getElementById('theme-toggle');
const priorityBtns = document.querySelectorAll('.priority-btn');
const saveJsonBtn = document.getElementById('save-json-btn');
const loadJsonBtn = document.getElementById('load-json-btn');
const clearAllBtn = document.getElementById('clear-all-btn');
const jsonFileInput = document.getElementById('json-file-input');
const editModal = document.getElementById('edit-modal');
const closeEditModal = document.getElementById('close-edit-modal');
const editForm = document.getElementById('edit-form');
const cancelEdit = document.getElementById('cancel-edit');
const importGuideBtn = document.getElementById('import-guide-btn');
const importGuideModal = document.getElementById('import-guide-modal');
const closeImportGuide = document.getElementById('close-import-guide');

// ===========================
// Initialization
// ===========================

document.addEventListener('DOMContentLoaded', () => {
    loadFromLocalStorage();
    loadThemePreference();
    initEventListeners();
    renderEvents();
    updateUI();
});

// ===========================
// Event Listeners
// ===========================

function initEventListeners() {
    // Quick Add Form
    addEventBtn.addEventListener('click', handleAddEvent);
    naturalInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleAddEvent();
        }
    });

    // Priority Selection
    priorityBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            priorityBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            selectedPriority = btn.dataset.priority;
        });
    });

    // Theme Toggle
    themeToggle.addEventListener('click', cycleTheme);

    // Export
    exportBtn.addEventListener('click', exportToICS);

    // JSON Import/Export
    saveJsonBtn.addEventListener('click', exportToJSON);
    loadJsonBtn.addEventListener('click', () => jsonFileInput.click());
    jsonFileInput.addEventListener('change', importFromJSON);

    // Clear All
    clearAllBtn.addEventListener('click', handleClearAll);

    // Edit Modal
    closeEditModal.addEventListener('click', closeEditModalHandler);
    cancelEdit.addEventListener('click', closeEditModalHandler);
    editForm.addEventListener('submit', handleEditSubmit);

    // Close modal on overlay click
    editModal.addEventListener('click', (e) => {
        if (e.target === editModal) {
            closeEditModalHandler();
        }
    });

    // Import Guide Modal
    importGuideBtn.addEventListener('click', openImportGuideModal);
    closeImportGuide.addEventListener('click', closeImportGuideModal);

    // Tab switching
    const guideTabs = document.querySelectorAll('.guide-tab');
    guideTabs.forEach(tab => {
        tab.addEventListener('click', () => switchGuideTab(tab.dataset.tab));
    });

    // Close modal on overlay click
    importGuideModal.addEventListener('click', (e) => {
        if (e.target === importGuideModal) {
            closeImportGuideModal();
        }
    });
}

// ===========================
// Natural Language Processing
// ===========================

async function handleAddEvent() {
    const input = naturalInput.value.trim();

    if (!input) {
        showFeedback('Please enter an event description', 'error');
        return;
    }

    try {
        // Call backend to parse natural language
        const response = await fetch('/parse_nl', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ input })
        });

        const data = await response.json();

        if (!data.success) {
            showFeedback(data.error || 'Failed to parse input', 'error');
            return;
        }

        // Create event from parsed data
        const newEvent = {
            id: generateId(),
            title: data.event.title,
            date: data.event.date,
            startTime: data.event.startTime,
            endTime: data.event.endTime,
            priority: selectedPriority,
            notes: '',
            reminder: data.event.reminder || null,
            createdAt: new Date().toISOString()
        };

        // Check for conflicts
        const conflicts = checkConflicts(newEvent);
        if (conflicts.length > 0) {
            const conflictMessages = conflicts.map(e =>
                `• ${e.title} (${e.startTime} - ${e.endTime})`
            ).join('\n');

            const proceed = confirm(
                `⚠️ Time Conflict Detected!\n\n` +
                `Your new event "${newEvent.title}" overlaps with:\n${conflictMessages}\n\n` +
                `Do you want to add it anyway?`
            );

            if (!proceed) {
                showFeedback('Event not added due to conflict', 'error');
                return;
            }
        }

        addEvent(newEvent);
        naturalInput.value = '';

        // Show reminder info if present
        let feedbackMsg = `Added: ${newEvent.title}`;
        if (newEvent.reminder) {
            feedbackMsg += ` (⏰ ${newEvent.reminder}min reminder)`;
        }
        showFeedback(feedbackMsg, 'success');

        // Reset to default priority
        selectedPriority = 'green';
        priorityBtns.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.priority === 'green');
        });

    } catch (error) {
        console.error('Error adding event:', error);
        showFeedback('Failed to add event. Please try again.', 'error');
    }
}

function showFeedback(message, type) {
    parseFeedback.textContent = message;
    parseFeedback.className = `parse-feedback ${type}`;

    setTimeout(() => {
        parseFeedback.className = 'parse-feedback';
    }, 3000);
}

// ===========================
// Event Management
// ===========================

function addEvent(event) {
    events.push(event);
    sortEvents();
    saveToLocalStorage();
    renderEvents();
    updateUI();
}

function deleteEvent(eventId) {
    const card = document.querySelector(`[data-event-id="${eventId}"]`);

    if (card) {
        card.classList.add('exiting');
        setTimeout(() => {
            events = events.filter(e => e.id !== eventId);
            saveToLocalStorage();
            renderEvents();
            updateUI();
        }, 250);
    }
}

function editEvent(eventId) {
    const event = events.find(e => e.id === eventId);
    if (!event) return;

    editingEventId = eventId;

    // Populate form
    document.getElementById('edit-title').value = event.title;
    document.getElementById('edit-date').value = event.date;
    document.getElementById('edit-start-time').value = event.startTime;
    document.getElementById('edit-end-time').value = event.endTime;
    document.getElementById('edit-priority').value = event.priority;
    document.getElementById('edit-notes').value = event.notes || '';

    // Show modal
    editModal.style.display = 'flex';
}

function handleEditSubmit(e) {
    e.preventDefault();

    const eventIndex = events.findIndex(e => e.id === editingEventId);
    if (eventIndex === -1) return;

    // Update event
    events[eventIndex] = {
        ...events[eventIndex],
        title: document.getElementById('edit-title').value,
        date: document.getElementById('edit-date').value,
        startTime: document.getElementById('edit-start-time').value,
        endTime: document.getElementById('edit-end-time').value,
        priority: document.getElementById('edit-priority').value,
        notes: document.getElementById('edit-notes').value
    };

    sortEvents();
    saveToLocalStorage();
    renderEvents();
    updateUI();
    closeEditModalHandler();
}

function closeEditModalHandler() {
    editModal.style.display = 'none';
    editingEventId = null;
}

// ===========================
// Auto-Chronological Sorting
// ===========================

function sortEvents() {
    events.sort((a, b) => {
        const dateA = new Date(`${a.date}T${a.startTime}`);
        const dateB = new Date(`${b.date}T${b.startTime}`);

        if (dateA < dateB) return -1;
        if (dateA > dateB) return 1;

        // If same time, sort alphabetically by title
        return a.title.localeCompare(b.title);
    });
}

// ===========================
// Conflict Detection
// ===========================

function checkConflicts(newEvent) {
    /**
     * Check if newEvent overlaps with any existing events
     * Returns array of conflicting events
     */
    const conflicts = [];

    for (const existingEvent of events) {
        // Skip if different dates
        if (existingEvent.date !== newEvent.date) continue;

        // Convert times to minutes for easier comparison
        const newStart = timeToMinutes(newEvent.startTime);
        const newEnd = timeToMinutes(newEvent.endTime);
        const existingStart = timeToMinutes(existingEvent.startTime);
        const existingEnd = timeToMinutes(existingEvent.endTime);

        // Check for overlap: events overlap if one starts before the other ends
        const overlaps = (newStart < existingEnd && newEnd > existingStart);

        if (overlaps) {
            conflicts.push(existingEvent);
        }
    }

    return conflicts;
}

function timeToMinutes(timeStr) {
    /**
     * Convert HH:MM to total minutes since midnight
     */
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
}

// ===========================
// Rendering
// ===========================

function renderEvents() {
    // Clear container except empty state
    const existingCards = eventsContainer.querySelectorAll('.event-card');
    existingCards.forEach(card => card.remove());

    if (events.length === 0) {
        emptyState.style.display = 'flex';
        return;
    }

    emptyState.style.display = 'none';

    events.forEach((event, index) => {
        const card = createEventCard(event);
        eventsContainer.appendChild(card);

        // Stagger animation
        setTimeout(() => {
            card.classList.add('entering');
        }, index * 50);
    });
}

function createEventCard(event) {
    const card = document.createElement('div');
    card.className = 'event-card';
    card.dataset.eventId = event.id;
    card.dataset.priority = event.priority;

    const formattedDate = formatDate(event.date);
    const formattedTime = `${event.startTime} - ${event.endTime}`;

    card.innerHTML = `
        <div class="event-card-content">
            <div class="event-title">${escapeHtml(event.title)}</div>
            <div class="event-datetime">
                <span class="event-date">
                    📅 ${formattedDate}
                </span>
                <span class="event-time">
                    🕐 ${formattedTime}
                </span>
            </div>
        </div>
        <div class="event-actions">
            <button class="event-btn edit-btn" onclick="editEvent('${event.id}')" title="Edit">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M11.5 1.5L14.5 4.5L5 14H2V11L11.5 1.5Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
            <button class="event-btn delete-btn" onclick="deleteEvent('${event.id}')" title="Delete">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
            </button>
        </div>
    `;

    return card;
}

function updateUI() {
    const count = events.length;
    eventCountEl.textContent = `${count} event${count !== 1 ? 's' : ''}`;
    exportBtn.disabled = count === 0;
}

// ===========================
// Local Storage
// ===========================

function saveToLocalStorage() {
    localStorage.setItem('calendme_events', JSON.stringify(events));
}

function loadFromLocalStorage() {
    const saved = localStorage.getItem('calendme_events');
    if (saved) {
        try {
            events = JSON.parse(saved);
            sortEvents();
        } catch (error) {
            console.error('Error loading events:', error);
            events = [];
        }
    }
}

// ===========================
// Theme Management
// ===========================

function loadThemePreference() {
    const saved = localStorage.getItem('calendme_theme');
    if (saved) {
        currentTheme = saved;
        applyTheme(currentTheme);
    } else {
        // Auto-detect based on time of day for ambient mode
        currentTheme = 'ambient';
        applyTheme(currentTheme);
    }
}

function cycleTheme() {
    const themes = ['light', 'dark', 'ambient'];
    const currentIndex = themes.indexOf(currentTheme);
    const nextIndex = (currentIndex + 1) % themes.length;
    currentTheme = themes[nextIndex];

    applyTheme(currentTheme);
    localStorage.setItem('calendme_theme', currentTheme);
}

function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);

    // Update icon visibility
    const sunIcon = themeToggle.querySelector('.sun-icon');
    const moonIcon = themeToggle.querySelector('.moon-icon');
    const autoIcon = themeToggle.querySelector('.auto-icon');

    sunIcon.style.display = theme === 'light' ? 'block' : 'none';
    moonIcon.style.display = theme === 'dark' ? 'block' : 'none';
    autoIcon.style.display = theme === 'ambient' ? 'block' : 'none';
}

// ===========================
// Export Functionality
// ===========================

async function exportToICS() {
    if (events.length === 0) return;

    try {
        const response = await fetch('/generate_ics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ events })
        });

        if (!response.ok) {
            throw new Error('Failed to generate ICS file');
        }

        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `calendme_schedule.ics`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showFeedback('Calendar exported successfully!', 'success');
    } catch (error) {
        console.error('Export error:', error);
        showFeedback('Failed to export calendar', 'error');
    }
}

function exportToJSON() {
    if (events.length === 0) {
        showFeedback('No events to export', 'error');
        return;
    }

    const dataStr = JSON.stringify(events, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    const timestamp = new Date().toISOString().split('T')[0];
    a.href = url;
    a.download = `calendme_schedule_${timestamp}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    showFeedback('Schedule saved as JSON', 'success');
}

function importFromJSON(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
        try {
            const imported = JSON.parse(event.target.result);

            if (!Array.isArray(imported)) {
                throw new Error('Invalid format');
            }

            events = imported;
            sortEvents();
            saveToLocalStorage();
            renderEvents();
            updateUI();
            showFeedback(`Loaded ${imported.length} events`, 'success');
        } catch (error) {
            console.error('Import error:', error);
            showFeedback('Failed to load schedule. Invalid file.', 'error');
        }
    };
    reader.readAsText(file);

    // Reset input
    jsonFileInput.value = '';
}

function handleClearAll() {
    if (events.length === 0) return;

    const confirmed = confirm(`Are you sure you want to delete all ${events.length} events? This cannot be undone.`);

    if (confirmed) {
        events = [];
        saveToLocalStorage();
        renderEvents();
        updateUI();
        showFeedback('All events cleared', 'success');
    }
}

// ===========================
// Utility Functions
// ===========================

function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

function formatDate(dateStr) {
    const date = new Date(dateStr + 'T00:00:00');
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    // Check if today or tomorrow
    if (date.toDateString() === today.toDateString()) {
        return 'Today';
    }
    if (date.toDateString() === tomorrow.toDateString()) {
        return 'Tomorrow';
    }

    // Otherwise format as "Mon, Jan 15"
    const options = { weekday: 'short', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===========================
// Import Guide Modal
// ===========================

function openImportGuideModal() {
    importGuideModal.style.display = 'flex';
}

function closeImportGuideModal() {
    importGuideModal.style.display = 'none';
}

function switchGuideTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.guide-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    // Update panels
    document.querySelectorAll('.guide-panel').forEach(panel => {
        panel.classList.remove('active');
    });

    const targetPanel = document.getElementById(`${tabName}-guide`);
    if (targetPanel) {
        targetPanel.classList.add('active');
    }
}

// Make functions globally accessible for onclick handlers
window.editEvent = editEvent;
window.deleteEvent = deleteEvent;
