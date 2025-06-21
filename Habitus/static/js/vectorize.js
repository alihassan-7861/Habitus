const CONFIG = {
    tooltips: {
        maxColors: 549,
        defaultValues: {
            width: 10,
            height: 10,
            detail: 0.1,
            minArea: 60,
            maxColors: 36
        }
    },
    validation: {
        minWidth: 1,
        minHeight: 1,
        minDetail: 0.1,
        maxDetail: 1,
        minArea: 1,
        minColors: 1,
        maxColors: 549
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
            info: '#3498db',
            success: '#2ecc71',
            warning: '#f39c12',
            error: '#e74c3c'
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
            this.uploadArea.innerHTML = `<img src="${e.target.result}" alt="Uploaded image" class="uploaded-image">`;
        };
        reader.readAsDataURL(file);
    }
    showOutput(svgUrl) {
        fetch(svgUrl)
            .then(res => res.text())
            .then(svgText => {
                this.outputArea.innerHTML = `
                    <div style="text-align: center; padding: 20px;">
                        <p style="margin-bottom: 15px; color: #2ecc71;">✓ Vectorization Complete!</p>
                        <div class="svg-preview" style="max-height:400px; overflow:auto;">${svgText}</div>
                        <a href="${svgUrl}" download style="display:block; margin-top:10px; color:#3498db;">Download Vector</a>
                    </div>
                `;
            });
    }
}

class FormValidator {
    constructor() {
        this.rules = CONFIG.validation;
    }
    validate(data) {
        const errors = [];
        if (!Utils.validateNumber(data.width, this.rules.minWidth)) errors.push(`Width must be at least ${this.rules.minWidth}`);
        if (!Utils.validateNumber(data.height, this.rules.minHeight)) errors.push(`Height must be at least ${this.rules.minHeight}`);
        if (!Utils.validateNumber(data.level_of_details, this.rules.minDetail, this.rules.maxDetail))
            errors.push(`Detail level must be between ${this.rules.minDetail} and ${this.rules.maxDetail}`);
        if (!Utils.validateNumber(data.minimum_area, this.rules.minArea))
            errors.push(`Minimum area must be at least ${this.rules.minArea}`);
        if (!Utils.validateNumber(data.maximum_colors, this.rules.minColors, this.rules.maxColors))
            errors.push(`Maximum colors must be between ${this.rules.minColors} and ${this.rules.maxColors}`);
        return errors;
    }
}

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
        const inputs = ['width', 'height', 'detail', 'minArea', 'maxColors'];
        inputs.forEach(id => {
            const input = Utils.getEl(id);
            if (input) {
                input.addEventListener('input', () => this.validateInput(input));
            }
        });
    }

    validateInput(input) {
        const id = input.id;
        const value = input.value;
        const rules = CONFIG.validation;
        let valid = true;
        let message = '';

        switch (id) {
            case 'width':
                if (!Utils.validateNumber(value, rules.minWidth)) {
                    valid = false;
                    message = `Width must be ≥ ${rules.minWidth}`;
                }
                break;
            case 'height':
                if (!Utils.validateNumber(value, rules.minHeight)) {
                    valid = false;
                    message = `Height must be ≥ ${rules.minHeight}`;
                }
                break;
            case 'detail':
                if (!Utils.validateNumber(value, rules.minDetail, rules.maxDetail)) {
                    valid = false;
                    message = `Detail must be ${rules.minDetail}–${rules.maxDetail}`;
                }
                break;
            case 'minArea':
                if (!Utils.validateNumber(value, rules.minArea)) {
                    valid = false;
                    message = `Min area must be ≥ ${rules.minArea}`;
                }
                break;
            case 'maxColors':
                if (!Utils.validateNumber(value, rules.minColors, rules.maxColors)) {
                    valid = false;
                    message = `Max colors must be ${rules.minColors}–${rules.maxColors}`;
                }
                break;
        }

        if (!valid) {
            input.classList.add('input-error');
            input.setCustomValidity(message);
            input.reportValidity();
        } else {
            input.classList.remove('input-error');
            input.setCustomValidity('');
        }
    }

    initInputConstraints() {
        const constraints = [
            { id: 'width', min: CONFIG.validation.minWidth },
            { id: 'height', min: CONFIG.validation.minHeight },
            { id: 'detail', min: CONFIG.validation.minDetail, max: CONFIG.validation.maxDetail, step: 0.1 },
            { id: 'minArea', min: CONFIG.validation.minArea },
            { id: 'maxColors', min: CONFIG.validation.minColors, max: CONFIG.validation.maxColors }
        ];
        constraints.forEach(constraint => {
            const input = Utils.getEl(constraint.id);
            if (input) {
                input.setAttribute('min', constraint.min);
                if (constraint.max) input.setAttribute('max', constraint.max);
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
        data.append('width', formData.width);
        data.append('height', formData.height);
        data.append('mode', formData.mode || 'test');
        data.append('output_format', formData.output_format);
        data.append('level_of_details', formData.level_of_details);
        data.append('smoothing', formData.smoothing);
        data.append('minimum_area', formData.minimum_area);
        data.append('maximum_colors', formData.maximum_colors);

        Utils.showNotification('Submitting to server...', 'info');
        Utils.getEl('loadingSpinner').style.display = 'block';

        fetch('/vectorize/', {
            method: 'POST',
            body: data
        })
        .then(res => res.json())
        .then(res => {
            Utils.getEl('loadingSpinner').style.display = 'none';
            if (res.media_url) {
                this.uploadManager.showOutput(res.media_url);
                Utils.showNotification('✅ Vectorization completed!', 'success');
            } else {
                Utils.showNotification(res.error || 'Vectorization failed.', 'error');
            }
        })
        .catch(err => {
            console.error(err);
            Utils.getEl('loadingSpinner').style.display = 'none';
            Utils.showNotification('Server error. Please try again.', 'error');
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new VectorizerApp();
});
