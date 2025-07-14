
const CONFIG = {
    tooltips: {
        defaultValues: {
            width: 10,
            height: 10,
            detail: 0.5,
            minArea: 60,
        }
    },
    validation: {
        minWidth: 0.0,
        maxWidth: 1.0e12,
        minHeight: 0.0,
        maxHeight: 1.0e12,
        minDetail: 0.001,
        maxDetail: 1.0,
        minArea: 45.0,
        maxArea: 100.0,
       
    },
    allowedImageTypes: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
};

const Utils = {
    getEl: (id) => document.getElementById(id),
    getFormData: (form) => {
        const formData = new FormData(form);
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        return data;
    },
    validateNumber: (value, min, max) => {
        const num = parseFloat(value);
        return !isNaN(num) && num >= min && (max === undefined || num <= max);
    },
    validateFileType: (file) => CONFIG.allowedImageTypes.includes(file.type),
    showNotification: (message, type = 'info') => {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        Object.assign(notification.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 20px',
            borderRadius: '6px',
            color: 'white',
            zIndex: '9999',
            fontSize: '14px',
            fontWeight: '500',
            transform: 'translateX(400px)',
            transition: 'transform 0.3s ease'
        });
       const colors = {
                info: getComputedStyle(document.documentElement).getPropertyValue('--accent').trim() || '#3498db',
                success: getComputedStyle(document.documentElement).getPropertyValue('--success').trim() || '#2ecc71',
                warning: getComputedStyle(document.documentElement).getPropertyValue('--warning').trim() || '#f39c12',
                error: getComputedStyle(document.documentElement).getPropertyValue('--error').trim() || '#e74c3c'
            };
notification.style.backgroundColor = colors[type] || colors.info;
        document.body.appendChild(notification);
        setTimeout(() => { notification.style.transform = 'translateX(0)'; }, 100);
        setTimeout(() => {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => {
                if (document.body.contains(notification)) {
                    document.body.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
};

class TooltipManager {
    constructor() {
        this.tooltip = Utils.getEl('tooltip');
        this.initTooltips();
    }
    initTooltips() {
        document.querySelectorAll('.tooltip-btn').forEach(btn => {
            btn.addEventListener('mouseenter', (e) => this.showTooltip(e));
            btn.addEventListener('mouseleave', () => this.hideTooltip());
            btn.addEventListener('mousemove', (e) => this.moveTooltip(e));
        });
    }
    showTooltip(e) {
        const text = e.target.getAttribute('data-tooltip');
        this.tooltip.textContent = text;
        this.tooltip.classList.add('show');
        this.moveTooltip(e);
    }
    hideTooltip() {
        this.tooltip.classList.remove('show');
    }
    moveTooltip(e) {
        const rect = this.tooltip.getBoundingClientRect();
        const x = e.pageX - rect.width / 2;
        const y = e.pageY - rect.height - 10;
        this.tooltip.style.left = Math.max(10, x) + 'px';
        this.tooltip.style.top = Math.max(10, y) + 'px';
    }
}

class ImageUploadManager {
    constructor() {
        this.uploadArea = Utils.getEl('uploadArea');
        this.browseBtn = Utils.getEl('browseBtn');
        this.fileInput = Utils.getEl('fileInput');
        this.outputArea = Utils.getEl('outputArea');
        this.uploadedFile = null;
        this.imageOriginalWidth = 0;
        this.imageOriginalHeight = 0;
        this.initEventListeners();
    }

    initEventListeners() {
        this.browseBtn.addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });
        this.uploadArea.addEventListener('dragleave', () => this.uploadArea.classList.remove('dragover'));
        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            this.handleFileSelect(file);
        });
    }

    handleFileSelect(file) {
        if (!file) return;
        if (!Utils.validateFileType(file)) {
            Utils.showNotification('Please select a valid image file (JPEG, PNG, GIF, WebP)', 'error');
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            Utils.showNotification('File size must be less than 10MB', 'error');
            return;
        }
        this.uploadedFile = file;
        this.displayUploadedImage(file);
        Utils.showNotification('Image uploaded successfully!', 'success');
    }

    displayUploadedImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.uploadArea.innerHTML = `
                <div class="uploaded-wrapper">
                    <img src="${e.target.result}" alt="Uploaded image" class="uploaded-image">
                    <button class="browse-btn">Choose Another Image</button>
                </div>
            `;
            const newBrowseBtn = this.uploadArea.querySelector('.browse-btn');
            newBrowseBtn.addEventListener('click', () => this.fileInput.click());
        };
        reader.readAsDataURL(file);
    }

    showOutput(blob) {
    const ext = blob.type.includes('svg') ? 'svg' : 'png';
    const contentType = blob.type;

    const url = URL.createObjectURL(new Blob([blob], { type: contentType }));

    // Show image in output area
    this.outputArea.innerHTML = `
        <div class="output-result">
            <p class="vector-success">✓ Vectorization Complete!</p>
            <img id="vectorResultImage" src="${url}" alt="Vectorized Output" onerror="this.style.display='none'; Utils.showNotification('⚠️ Failed to render the output image', 'error');"/>
        </div>
    `;

    // Store DataURL for preview or download
    const reader = new FileReader();
    reader.onload = () => {
        sessionStorage.setItem("vectorizedImage", reader.result);
    };
    reader.readAsDataURL(blob);

    // Show Continue button
    const continueBtnWrapper = Utils.getEl("continueBtnWrapper");
    if (continueBtnWrapper) continueBtnWrapper.style.display = "block";

    // Remove any old download buttons
    const existingWrapper = document.querySelector('.download-wrapper');
    if (existingWrapper) existingWrapper.remove();
}
}

// VectorizerApp — unchanged except handleSubmit
class VectorizerApp {
    constructor() {
        this.form = Utils.getEl('parametersForm');
        this.tooltipManager = new TooltipManager();
        this.validator = new FormValidator();
        this.uploadManager = new ImageUploadManager();
        this.initEventListeners();
        this.initInputConstraints();
    }

    initEventListeners() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));

        const widthInput = Utils.getEl('width');
        const heightInput = Utils.getEl('height');

        const pairMapping = { "45": "30", "60": "40", "90": "60" };
        let isSyncing = false;

        widthInput.addEventListener('change', () => {
            if (isSyncing) return;
            isSyncing = true;
            const w = widthInput.value;
            if (pairMapping[w]) heightInput.value = pairMapping[w];
            isSyncing = false;
        });

        heightInput.addEventListener('change', () => {
            if (isSyncing) return;
            isSyncing = true;
            const h = heightInput.value;
            const reverseMatch = Object.entries(pairMapping).find(([k, v]) => v === h);
            if (reverseMatch) widthInput.value = reverseMatch[0];
            isSyncing = false;
        });
    }

    initInputConstraints() {
        const constraints = [];
        constraints.forEach(constraint => {
            const input = Utils.getEl(constraint.id);
            if (input) {
                input.setAttribute('min', constraint.min);
                if (constraint.max !== undefined) input.setAttribute('max', constraint.max);
                if (constraint.step) input.setAttribute('step', constraint.step);
            }
        });
    }

    handleSubmit(e) {
        e.preventDefault();
        const formData = Utils.getFormData(this.form);
        const errors = this.validator.validate(formData);
        if (errors.length > 0) {
            Utils.showNotification(errors.join('. '), 'error');
            return;
        }
        if (!this.uploadManager.uploadedFile) {
            Utils.showNotification('Please upload an image first.', 'error');
            return;
        }

        const data = new FormData();
        data.append('image', this.uploadManager.uploadedFile);

        const selectedFormat = document.querySelector('input[name="output_format"]:checked');
        if (selectedFormat) data.append('output_format', selectedFormat.value);

        Object.entries(formData).forEach(([key, value]) => {
            if (key !== 'maximum_colors' && key !== 'output_format') {
                data.append(key, value);
            }
        });

        Utils.showNotification('Submitting to server...', 'info');
        Utils.getEl('loadingSpinner').style.display = 'block';

        fetch('/vectorize/', {
            method: 'POST',
            body: data
        })
        .then(res => {
            Utils.getEl('loadingSpinner').style.display = 'none';
            if (!res.ok) throw new Error('Request failed');
            return res.blob();
        })
        .then(blob => {
            this.uploadManager.showOutput(blob);
            Utils.showNotification('✅ Vectorization completed!', 'success');
        })
        .catch(err => {
            console.error(err);
            Utils.getEl('loadingSpinner').style.display = 'none';
            Utils.showNotification('Server error. Please try again.', 'error');
        });
    }
}

// ✅ Continue Button Logic (used in HTML)
function continueToNextPage() {
    window.location.href = "/test-pbn/";
}

// Start the app

class FormValidator {
    constructor() {
        this.rules = CONFIG.validation;
    }
    validate(data) {
        const errors = [];
        if (!Utils.validateNumber(data.width, this.rules.minWidth, this.rules.maxWidth)) 
            errors.push(`Width must be between ${this.rules.minWidth} and ${this.rules.maxWidth}`);
        if (!Utils.validateNumber(data.height, this.rules.minHeight, this.rules.maxHeight)) 
            errors.push(`Height must be between ${this.rules.minHeight} and ${this.rules.maxHeight}`);
        if (!Utils.validateNumber(data.level_of_details, this.rules.minDetail, this.rules.maxDetail))
            errors.push(`Detail level must be between ${this.rules.minDetail} and ${this.rules.maxDetail}`);
        if (!Utils.validateNumber(data.minimum_area, this.rules.minArea, this.rules.maxArea))
            errors.push(`Minimum area must be between ${this.rules.minArea} and ${this.rules.maxArea}`);
        return errors;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new VectorizerApp();
});
