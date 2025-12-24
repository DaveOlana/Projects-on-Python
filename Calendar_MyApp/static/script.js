document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.querySelector('.browse-btn');
    const previewSection = document.getElementById('preview-section');
    const eventsBody = document.getElementById('events-body');
    const exportBtn = document.getElementById('export-btn');

    let currentEvents = [];

    // Drag & Drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) handleFile(files[0]);
    });

    // Click handlers
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) handleFile(fileInput.files[0]);
    });

    function handleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        // Show loading state
        dropZone.innerHTML = `<p>Processing ${file.name}...</p>`;

        fetch('/parse', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.events) {
                    currentEvents = data.events;
                    renderTable(currentEvents);
                    previewSection.classList.remove('hidden');
                    dropZone.innerHTML = `<p>File uploaded! Drag another to replace.</p>`;
                } else {
                    alert('Error parsing file: ' + (data.error || 'Unknown error'));
                    resetDropZone();
                }
            })
            .catch(err => {
                console.error(err);
                alert('Upload failed.');
                resetDropZone();
            });
    }

    function resetDropZone() {
        dropZone.innerHTML = `<p>Drag & drop your file here or <span class="browse-btn">browse</span></p>`;
    }

    function renderTable(events) {
        eventsBody.innerHTML = '';
        events.forEach((event, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td contenteditable="true" data-field="course">${event.course || ''}</td>
                <td contenteditable="true" data-field="title">${event.title || ''}</td>
                <td contenteditable="true" data-field="date">${event.date || ''}</td>
                <td contenteditable="true" data-field="time">${event.time || ''}</td>
                <td contenteditable="true" data-field="location">${event.location || ''}</td>
                <td><button onclick="removeEvent(${index})">❌</button></td>
            `;
            // Add listeners for edits
            row.querySelectorAll('[contenteditable]').forEach(cell => {
                cell.addEventListener('blur', (e) => {
                    const field = e.target.dataset.field;
                    currentEvents[index][field] = e.target.innerText;
                });
            });
            eventsBody.appendChild(row);
        });
    }

    window.removeEvent = function (index) {
        currentEvents.splice(index, 1);
        renderTable(currentEvents);
    };

    exportBtn.addEventListener('click', () => {
        fetch('/generate_ics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ events: currentEvents })
        })
            .then(response => response.blob())
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'exam_schedule.ics';
                document.body.appendChild(a);
                a.click();
                a.remove();
            })
            .catch(err => alert('Export failed'));
    });
});
