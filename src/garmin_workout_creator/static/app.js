// DOM Elements
const workoutInput = document.getElementById('workoutInput');
const parseBtn = document.getElementById('parseBtn');
const previewSection = document.getElementById('previewSection');
const workoutPreview = document.getElementById('workoutPreview');
const metadataSection = document.getElementById('metadataSection');
const metadataForm = document.getElementById('metadataForm');
const statusMessage = document.getElementById('statusMessage');

// State
let parsedWorkout = null;

// Event Listeners
parseBtn.addEventListener('click', handleParse);
metadataForm.addEventListener('submit', handleUpload);

// Parse workout on input (debounced)
let parseTimeout;
workoutInput.addEventListener('input', () => {
    clearTimeout(parseTimeout);
    parseTimeout = setTimeout(() => {
        if (workoutInput.value.trim()) {
            handleParse();
        }
    }, 1000);
});

// Functions
async function handleParse() {
    const text = workoutInput.value.trim();

    if (!text) {
        showStatus('Please enter a workout description', 'error');
        return;
    }

    parseBtn.disabled = true;
    parseBtn.textContent = 'Parsing...';
    hideStatus();

    try {
        const response = await fetch('/api/parse', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });

        const data = await response.json();

        if (data.success) {
            parsedWorkout = data.workout;
            displayWorkoutPreview(data.workout);
            previewSection.classList.remove('hidden');
            metadataSection.classList.remove('hidden');
            showStatus('Workout parsed successfully!', 'success');
        } else {
            showStatus(`Parse error: ${data.error}`, 'error');
            previewSection.classList.add('hidden');
            metadataSection.classList.add('hidden');
        }
    } catch (error) {
        showStatus(`Network error: ${error.message}`, 'error');
    } finally {
        parseBtn.disabled = false;
        parseBtn.textContent = 'Parse Workout';
    }
}

async function handleUpload(e) {
    e.preventDefault();

    if (!parsedWorkout) {
        showStatus('Please parse a workout first', 'error');
        return;
    }

    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Uploading...';
    hideStatus();

    const metadata = {
        name: document.getElementById('workoutName').value,
        scheduled_date: document.getElementById('scheduledDate').value || null,
        notes: document.getElementById('notes').value || null,
    };

    const requestData = {
        workout_text: workoutInput.value.trim(),
        metadata,
        garmin_email: document.getElementById('garminEmail').value || null,
        garmin_password: document.getElementById('garminPassword').value || null,
    };

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
        });

        const data = await response.json();

        if (data.success) {
            showStatus(
                `${data.message} Workout ID: ${data.workout_id}`,
                'success'
            );
            // Clear password field for security
            document.getElementById('garminPassword').value = '';
        } else {
            showStatus(
                `Upload failed: ${data.error || data.message}`,
                'error'
            );
        }
    } catch (error) {
        showStatus(`Network error: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Upload to Garmin Connect';
    }
}

function displayWorkoutPreview(workout) {
    workoutPreview.innerHTML = '';

    if (!workout || !workout.steps || workout.steps.length === 0) {
        workoutPreview.innerHTML = '<p>No steps found in workout</p>';
        return;
    }

    workout.steps.forEach((step, index) => {
        const stepElement = createStepElement(step, index + 1);
        workoutPreview.appendChild(stepElement);
    });
}

function createStepElement(step, stepNumber) {
    if (step.step_type === 'repeat') {
        return createRepeatElement(step, stepNumber);
    }

    const stepDiv = document.createElement('div');
    stepDiv.className = 'workout-step';

    const typeDiv = document.createElement('div');
    typeDiv.className = 'step-type';
    typeDiv.textContent = `Step ${stepNumber}: ${step.step_type}`;

    const durationDiv = document.createElement('div');
    durationDiv.className = 'step-duration';
    durationDiv.textContent = formatDuration(step);

    const targetDiv = document.createElement('div');
    targetDiv.className = 'step-target';
    targetDiv.textContent = formatTarget(step);

    stepDiv.appendChild(typeDiv);
    stepDiv.appendChild(durationDiv);
    stepDiv.appendChild(targetDiv);

    return stepDiv;
}

function createRepeatElement(step, stepNumber) {
    const repeatDiv = document.createElement('div');
    repeatDiv.className = 'repeat-container';

    const headerDiv = document.createElement('div');
    headerDiv.className = 'repeat-header';
    headerDiv.textContent = `Step ${stepNumber}: Repeat ${step.repeat_count || 1}x`;

    repeatDiv.appendChild(headerDiv);

    if (step.steps && step.steps.length > 0) {
        step.steps.forEach((childStep, index) => {
            const childElement = createStepElement(childStep, index + 1);
            repeatDiv.appendChild(childElement);
        });
    }

    return repeatDiv;
}

function formatDuration(step) {
    if (!step.duration_type || !step.duration_value) {
        return 'Open (press lap to end)';
    }

    const value = step.duration_value;
    const type = step.duration_type;

    if (type === 'distance') {
        return `${value} ${step.duration_unit || 'km'}`;
    } else if (type === 'time') {
        const unit = step.duration_unit || 'min';
        return `${value} ${unit}`;
    } else if (type === 'lap_button') {
        return 'Open (press lap to end)';
    }

    return `${value} ${step.duration_unit || ''}`;
}

function formatTarget(step) {
    if (!step.target_type || step.target_type === 'open') {
        return 'No target (open pace/effort)';
    }

    if (step.target_type === 'pace') {
        const pace = step.target_value;
        if (typeof pace === 'object' && pace.min_pace && pace.max_pace) {
            return `Target: ${pace.min_pace} - ${pace.max_pace} per ${step.target_unit || 'km'}`;
        } else if (pace) {
            return `Target: ${pace} per ${step.target_unit || 'km'}`;
        }
    } else if (step.target_type === 'heart_rate') {
        const hr = step.target_value;
        if (typeof hr === 'object' && hr.min_hr && hr.max_hr) {
            return `Target: ${hr.min_hr} - ${hr.max_hr} bpm`;
        } else if (hr) {
            return `Target: ${hr} bpm`;
        }
    }

    return 'No target';
}

function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = type;
    statusMessage.classList.remove('hidden');

    // Scroll to status message
    statusMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideStatus() {
    statusMessage.classList.add('hidden');
}

// Set today as default scheduled date
document.addEventListener('DOMContentLoaded', () => {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('scheduledDate').value = today;
});
