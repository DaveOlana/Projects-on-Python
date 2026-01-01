# CalendME - Smart Schedule Builder

A modern Progressive Web App (PWA) that lets you create and organize your schedule using natural language. Simply type events like "Monday 10am Team Meeting for 2 hours" and CalendME automatically parses, sorts, and exports them to any calendar app.

## ✨ Features

- **🗣️ Natural Language Input** - Type events conversationally: "Tomorrow 3pm Football match"
- **🎨 Priority Color-Coding** - Organize by urgency: Red (Urgent), Yellow (Important), Green (Normal)
- **⚡ Auto-Chronological Sorting** - Events automatically organize by date/time regardless of input order
- **💾 Auto-Save** - Local storage ensures your schedule persists offline
- **🌓 Multiple Themes** - Light, Dark, and Ambient modes with auto-adaptive lighting
- **📤 Universal Export** - Generate `.ics` files compatible with Google Calendar, Apple Calendar, Outlook, etc.
- **💿 JSON Backup** - Save and load schedules as JSON files for backup or sharing
- **📱 PWA Ready** - Install as a standalone app on desktop and mobile
- **🎯 Sleek, Minimalist UI** - Apple-inspired design with smooth animations and premium feel

## 🚀 Quick Start

### Installation

1. **Clone or download this repository**
   ```bash
   cd Calendar_MyApp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open in browser**
   Navigate to `http://localhost:5000`

### Usage

1. **Add Events**
   - Type in natural language: "Monday 10am Team Meeting for 2 hours"
   - Select priority level (Red/Yellow/Green)
   - Click "Add Event"

2. **Manage Events**
   - Events auto-sort chronologically
   - Click "Edit" to modify details
   - Click "×" to delete

3. **Export Calendar**
   - Click "Generate Calendar (.ics)"
   - Import the downloaded file into any calendar app
   - Or save as JSON for backup

## 🎨 Natural Language Examples

CalendME understands conversational input:

```text
- "Monday 10am Team Meeting"
- "Tomorrow 3pm Football match for 2 hours"
- "Jan 15 9:30am Dentist appointment"
- "Next Friday 2pm Project review for 90 minutes"
- "Today 6pm Dinner"
```

## 🛠️ Tech Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python/Flask
- **Smart Parsing**: `dateparser`, `parsedatetime`
- **Calendar Export**: `python-ics`
- **Storage**: Browser LocalStorage
- **PWA**: Service Worker, Manifest

## 📱 PWA Installation

### Desktop (Chrome/Edge)
1. Click the install icon (+) in the address bar
2. Click "Install"
3. CalendME opens as a standalone app

### Mobile (iOS Safari)
1. Tap the Share button
2. Select "Add to Home Screen"
3. Tap "Add"

### Mobile (Android Chrome)
1. Tap the menu (⋮)
2. Select "Install app"
3. Tap "Install"

## 🌐 Browser Compatibility

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## 📄 License

MIT License - Feel free to use and modify for your projects!

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

---

**Built with ❤️ for seamless schedule management**
