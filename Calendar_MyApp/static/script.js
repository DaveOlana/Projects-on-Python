document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const views = {
        upload: document.getElementById('step-upload'),
        mapping: document.getElementById('step-mapping'),
        preview: document.getElementById('step-preview')
    };
    const indicators = {
        1: document.getElementById('step-1-ind'),
        2: document.getElementById('step-2-ind'),
        3: document.getElementById('step-3-ind')
    };

    // State
    const state = {
        rawRows: [],
        filename: '',
        events: []
    };

    // --- Navigation ---
    window.goToStep = function (stepName) {
        // Hide all
        Object.values(views).forEach(el => el.classList.add('hidden'));
        // Show target
        views[stepName.replace('step-', '')].classList.remove('hidden');

        // Update indicators
        const stepNum = stepName === 'step-upload' ? 1 : stepName === 'step-mapping' ? 2 : 3;
        [1, 2, 3].forEach(n => {
            if (n <= stepNum) indicators[n].classList.add('active');
            else indicators[n].classList.remove('active');
        });
    };

    // --- Step 1: Upload Logic ---
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) handleFileUpload(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) handleFileUpload(fileInput.files[0]);
    });

    function handleFileUpload(file) {
        toggleLoader(true);
        const formData = new FormData();
        formData.append('file', file);

        fetch('/parse', { method: 'POST', body: formData })
            .then(res => res.json())
            .then(data => {
                toggleLoader(false);
                if (data.raw_rows) {
                    state.rawRows = data.raw_rows;
                    state.filename = data.filename;
                    renderMappingTable(state.rawRows.slice(0, 10)); // Show top 10 rows
                    goToStep('step-mapping');
                } else {
                    alert('Error: ' + (data.error || 'Failed to parse file.'));
                }
            })
            .catch(err => {
                toggleLoader(false);
                console.error(err);
                alert('Upload failed.');
            });
    }

    // --- Step 2: Mapping Logic ---
    function renderMappingTable(rows) {
        const thead = document.getElementById('mapping-head');
        const tbody = document.getElementById('mapping-body');

        if (!rows.length) return;

        // Create Header with Role Selectors
        let maxCols = Math.max(...rows.map(r => r.length));

        let headerHTML = '<tr>';
        for (let i = 0; i < maxCols; i++) {
            headerHTML += `
                <th>
                    <select class="column-mapper" data-col-index="${i}">
                        <option value="ignore">Ignore</option>
                        <option value="course">Course Code</option>
                        <option value="title">Course Title</option>
                        <option value="date">Date</option>
                        <option value="time">Time</option>
                        <option value="location">Location</option>
                    </select>
                </th>`;
        }
        headerHTML += '</tr>';
        thead.innerHTML = headerHTML;

        // Render Data Rows
        tbody.innerHTML = rows.map(row => {
            let tr = '<tr>';
            for (let i = 0; i < maxCols; i++) {
                tr += `<td>${row[i] || ''}</td>`;
            }
            tr += '</tr>';
            return tr;
        }).join('');
    }

    document.getElementById('process-btn').addEventListener('click', () => {
        // Gather mapping
        const selects = document.querySelectorAll('.column-mapper');
        const mapping = {};
        selects.forEach(sel => {
            if (sel.value !== 'ignore') {
                mapping[sel.value] = parseInt(sel.dataset.colIndex);
            }
        });

        const filterVal = document.getElementById('filter-input').value;

        // Validation
        if (mapping['course'] === undefined && mapping['title'] === undefined) {
            alert("Please map at least a 'Course Code' or 'Course Title' column.");
            return;
        }

        toggleLoader(true);
        fetch('/process_mapping', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                raw_rows: state.rawRows,
                mapping: mapping,
                filters: filterVal
            })
        })
            .then(res => res.json())
            .then(data => {
                toggleLoader(false);
                if (data.events) {
                    state.events = data.events;
                    renderPreviewTable(state.events);
                    goToStep('step-preview');
                }
            })
            .catch(err => {
                toggleLoader(false);
                alert("Processing failed.");
            });
    });

    // --- Step 3: Preview Logic ---
    const previewBody = document.getElementById('preview-body');

    function renderPreviewTable(events) {
        previewBody.innerHTML = '';
        if (events.length === 0) {
            previewBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No events found matching your criteria. Try adjusting filters or mapping.</td></tr>';
            return;
        }

        events.forEach((event, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td contenteditable="true" data-field="course">${event.course}</td>
                <td contenteditable="true" data-field="title">${event.title}</td>
                <td contenteditable="true" data-field="date">${event.date}</td>
                <td contenteditable="true" data-field="time">${event.time}</td>
                <td contenteditable="true" data-field="location">${event.location}</td>
                <td><button class="remove-btn" onclick="removeEvent(${index})">❌</button></td>
            `;

            // Listeners for inline edit updates
            tr.querySelectorAll('[contenteditable]').forEach(cell => {
                cell.addEventListener('blur', (e) => {
                    state.events[index][e.target.dataset.field] = e.target.innerText;
                });
            });

            previewBody.appendChild(tr);
        });
    }

    window.removeEvent = function (index) {
        state.events.splice(index, 1);
        renderPreviewTable(state.events);
    };

    document.getElementById('export-btn').addEventListener('click', () => {
        fetch('/generate_ics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ events: state.events })
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

    function toggleLoader(show) {
        const loader = document.getElementById('loader');
        if (show) loader.classList.remove('hidden');
        else loader.classList.add('hidden');
    }
});
