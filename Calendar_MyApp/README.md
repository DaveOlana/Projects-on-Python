# CalendME - Smart Schedule Builder

A modern Progressive Web App (PWA) that lets you create and organize your schedule using natural language. Simply type events like "Monday 10am Team Meeting for 2 hours" and CalendME automatically parses, sorts, and exports them to any calendar app.

---

## ✨ Features

- **🗣️ Natural Language Input** - Type events conversationally without complex forms
- **🎨 Priority Color-Coding** - Organize by urgency: Red (Urgent), Yellow (Important), Green (Normal)
- **⚡ Auto-Chronological Sorting** - Events automatically organize by date/time
- **🔍 Conflict Detection** - Warns when events overlap at the same time
- **💾 Auto-Save** - Local storage ensures your schedule persists offline
- **🌓 Multiple Themes** - Light, Dark, and Ambient modes
- **📤 Universal Export** - WebCal one-click or `.ics` download for all calendar apps
- **💿 JSON Backup** - Save and load schedules for backup or sharing
- **📱 PWA Ready** - Install as a standalone app
- **🎯 Sleek, Minimalist UI** - Apple-inspired design with smooth animations

---

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

---

## 📖 Complete User Guide

### 1. Adding Events

#### Using Natural Language Input

CalendME understands conversational, natural language. Simply type your event in the input box:

**Examples:**
```
"Monday 10am Team Meeting for 2 hours"
"Tomorrow 3pm Football match"
"4th of January, study from 6am to 10am"
"Next Friday 2pm Project review for 90 minutes"
"Jan 15 9:30am Dentist appointment"
"Today 6pm Dinner. Reminder 30 minutes before"
```

**Supported Formats:**

- **Dates:**
  - Relative: `today`, `tomorrow`, `next Friday`, `in 3 days`
  - Explicit: `Jan 15`, `January 4th`, `4th of January`
  
- **Times:**
  - Single time: `10am`, `9:30pm`, `14:00`
  - Time ranges: `6am to 10am`, `from 2pm to 5pm`
  - Durations: `for 2 hours`, `for 90 minutes`

- **Reminders:**
  - `reminder 30 minutes before`
  - `set a reminder 1 hour before the event`

#### Priority Selection

Before adding an event, select the priority level:
- 🔴 **Red** - Urgent tasks (exams, deadlines, critical meetings)
- 🟡 **Yellow** - Important tasks (assignments, appointments)
- 🟢 **Green** - Normal tasks (leisure, optional activities)

Priority defaults to Green if not selected.

#### Adding the Event

1. Type your event in natural language
2. Select priority color
3. Click **"Add Event"** or press **Enter**
4. Event appears in chronological order automatically!

---

### 2. Managing Events

#### Viewing Events

- Events display as **cards** sorted chronologically (earliest first)
- Each card shows:
  - Event title
  - Date (displays as "Today", "Tomorrow", or formatted date)
  - Time range
  - Priority color-coded stripe on the left

#### Editing Events

1. Click the **pencil icon** (✏️) on any event card
2. Modal opens with editable fields:
   - Title
   - Date
   - Start Time
   - End Time
   - Priority
   - Notes (optional)
3. Make your changes
4. Click **"Save Changes"**

#### Deleting Events

- Click the **× icon** on any event card
- Event animates out and is removed
- Changes auto-save to browser storage

#### Conflict Detection

If you add an event that overlaps with an existing event:
- A warning popup appears showing conflicting events
- You can choose to add anyway or cancel
- Helps prevent double-booking

---

### 3. Exporting Your Calendar

CalendME offers two export methods:

#### Option A: One-Click Add to Calendar (WebCal) - **Recommended**

**When to use:** You're online and want instant calendar integration

**How it works:**
1. Ensure you have events in your schedule
2. The button will show **"Add to Calendar"** when online
3. Click the button
4. Your default calendar app opens automatically
5. Confirm to add all events at once

**Supported Apps:**
- Google Calendar (desktop/mobile)
- Apple Calendar (Mac/iPhone/iPad)
- Microsoft Outlook
- Any calendar app that supports `.ics` files

**Note:** Files are temporarily stored on the server for 6 hours, then automatically deleted.

#### Option B: Download .ics File - **Universal Compatibility**

**When to use:** You're offline, or prefer manual import

**How it works:**
1. Button shows **"Download .ics"** when offline
2. Click the button
3. Enter a custom filename (e.g., "My January Schedule")
4. File downloads to your device
5. Import manually into your calendar app (see Import Guide)

---

### 4. Import Guide - Step-by-Step Instructions

Click the **"📖 Import guide to calendar"** button to view detailed instructions for:
- **Google Calendar** (Desktop/Web & Mobile)
- **Apple Calendar** (Mac & iPhone/iPad)
- **Microsoft Outlook** (Desktop, Web, Mobile)

Each guide includes:
- Desktop/web instructions
- Mobile-specific steps
- Email method (easiest for mobile)
- Alternative methods

---

### 5. Theme Customization

CalendME offers three beautiful themes:

#### Switching Themes

Click the **theme toggle icon** (☀️/🌙/🌓) in the header to cycle through:

1. **☀️ Light Mode**
   - Clean white background
   - Perfect for daytime use
   - High contrast for readability

2. **🌙 Dark Mode**
   - Dark charcoal background
   - Easy on the eyes at night
   - Reduces eye strain

3. **🌓 Ambient Mode**
   - Auto-adapts to time of day
   - Warm tones in evening
   - Cool tones in morning

Your theme preference is saved automatically.

---

### 6. Backup & Restore

#### Saving as JSON Backup

1. Click **"Save JSON"** button
2. Downloads a `.json` file with all your events
3. Store safely for backup or sharing

#### Loading from JSON Backup

1. Click **"Load JSON"** button
2. Select your previously saved `.json` file
3. All events restore instantly
4. Merges with existing events (doesn't replace)

#### Clearing All Events

1. Click **"Clear All"** button
2. Confirmation dialog appears
3. Confirm to delete all events
4. **Warning:** This cannot be undone! Save JSON backup first.

---

### 7. Advanced Features

#### Offline Mode

- **Auto-Save:** Every change saves to browser localStorage
- Events persist even after:
  - Closing the browser
  - Refreshing the page
  - System restart
- **Note:** Clearing browser data will erase events (save JSON backup!)

#### PWA Installation

Install CalendME as a standalone app:

**Desktop (Chrome/Edge):**
1. Click install icon (+) in address bar
2. Click "Install"
3. App opens in its own window

**Mobile (iOS Safari):**
1. Tap Share button
2. "Add to Home Screen"
3. Tap "Add"

**Mobile (Android Chrome):**
1. Tap menu (⋮)
2. "Install app"
3. Tap "Install"

#### Keyboard Shortcuts

- **Enter** - Add event (when input is focused)
- **Ctrl + Shift + R** - Hard refresh (clears cache)

---

## 🎨 Natural Language Parsing Examples

### Date Formats

```
"today 10am Meeting"               → Today at 10:00 AM
"tomorrow 3pm Football"            → Tomorrow at 3:00 PM
"monday 9am Dentist"               → Next Monday at 9:00 AM
"next friday 2pm Review"           → Next Friday at 2:00 PM
"in 3 days 4pm Call"               → 3 days from now at 4:00 PM
"Jan 15 10am Exam"                 → January 15th at 10:00 AM
"4th of January 6am Study"         → January 4th at 6:00 AM
```

### Time Formats

```
"Monday 10am Team Meeting"         → 10:00 AM - 11:00 AM (default 1hr)
"Tomorrow 3pm Football for 2 hours" → 3:00 PM - 5:00 PM
"Friday 9am to 11am Study"         → 9:00 AM - 11:00 AM
"Today 6pm Dinner for 90 minutes"  → 6:00 PM - 7:30 PM
```

### With Reminders

```
"Monday 10am Meeting. Reminder 30 minutes before"
"Tomorrow 3pm Dentist. Set a reminder 1 hour before"
```

---

## 🛠️ Tech Stack

- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python/Flask
- **Smart Parsing:** `dateparser`, `parsedatetime`, `python-dateutil`
- **Calendar Export:** `python-ics`
- **Storage:** Browser LocalStorage
- **PWA:** Service Worker, Manifest

---

## 🌐 Browser Compatibility

- ✅ Chrome/Edge (Recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

---

## 📋 Deployment Tips

### For Production Hosting

1. **Update `app.py`:**
   - Set `debug=False`
   - Configure proper WSGI server (gunicorn, waitress)

2. **Environment Variables:**
   - Set `FLASK_ENV=production`
   - Configure secret keys if needed

3. **Hosting Platforms:**
   - **Render** - Best for Flask apps with file storage
   - **Railway** - Simple deployment, persistent filesystem
   - **PythonAnywhere** - Easy Python hosting
   - **Vercel** - Requires WSGI adapter, serverless limitations

4. **File Cleanup:**
   - Lazy cleanup runs automatically every 6 hours
   - No cron jobs required (works on all platforms)

---

## ❓ Troubleshooting

### Events not saving?
- Check if browser allows localStorage
- Don't use Private/Incognito mode
- Save JSON backup regularly

### Natural language parser not working?
- Use supported date/time formats (see examples)
- Check server console for parsing errors
- Try explicit dates: "Jan 15 10am Meeting"

### WebCal not opening calendar app?
- Use "Download .ics" as fallback
- Check browser allows opening external apps
- Refer to Import Guide for manual steps

### Button shows "Checking..."?
- Wait 2-3 seconds for server ping
- If stuck, refresh page
- Check if server is running

---

## 🤝 Contributing

Suggestions and improvements are welcome! This is a personal project built for seamless schedule management.

---

## 📄 License

MIT License - Feel free to use and modify for your projects!

---

**Built with ❤️ using natural language processing and modern web technologies**
