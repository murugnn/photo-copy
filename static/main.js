// File: static/main.js

class MovieSelfieMatcher {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.setupDragAndDrop();
        this.uploadedFile = null;
    }

    initializeElements() {
        // This maps directly to the IDs in your new HTML
        this.uploadArea = document.getElementById('uploadArea');
        this.uploadPlaceholder = document.getElementById('uploadPlaceholder');
        this.fileInput = document.getElementById('fileInput');
        this.previewImage = document.getElementById('previewImage');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.clearBtn = document.getElementById('clearBtn');

        this.resultsContent = document.getElementById('resultsContent');
        this.resultsPlaceholder = document.getElementById('resultsPlaceholder');
        this.resultsDisplay = document.getElementById('resultsDisplay');
        this.loadingState = document.getElementById('loadingState');
        this.resultsActions = document.getElementById('resultsActions');

        this.matchedImage = document.getElementById('matchedImage');
        this.matchedName = document.getElementById('matchedName');
        this.matchedMovie = document.getElementById('matchedMovie');
        this.confidenceFill = document.getElementById('confidenceFill');
        this.confidenceValue = document.getElementById('confidenceValue');

        this.shareBtn = document.getElementById('shareBtn');
        this.retryBtn = document.getElementById('retryBtn');
    }

    bindEvents() {
        this.uploadBtn.addEventListener('click', () => this.fileInput.click());
        this.clearBtn.addEventListener('click', () => this.clearImage());
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.shareBtn.addEventListener('click', () => this.shareResult());
        this.retryBtn.addEventListener('click', () => this.resetApplication());
    }

    setupDragAndDrop() {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => this.uploadArea.classList.add('drag-over'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.uploadArea.addEventListener(eventName, () => this.uploadArea.classList.remove('drag-over'), false);
        });

        this.uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) this.handleFile(files[0]);
        }, false);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) this.handleFile(file);
    }

    handleFile(file) {
        if (!file.type.startsWith('image/')) {
            this.showError('Please select an image file.');
            return;
        }
        if (file.size > 10 * 1024 * 1024) {
            this.showError('File size must be less than 10MB.');
            return;
        }
        
        this.uploadedFile = file;

        const reader = new FileReader();
        reader.onload = (e) => {
            this.displayPreview(e.target.result);
            this.processImage();
        };
        reader.readAsDataURL(file);
    }
    
    displayPreview(imageSrc) {
        this.previewImage.src = imageSrc;
        this.previewImage.style.display = 'block';
        this.uploadPlaceholder.style.display = 'none';
        this.clearBtn.style.display = 'inline-flex';
    }

    clearImage() {
        this.previewImage.style.display = 'none';
        this.uploadPlaceholder.style.display = 'flex';
        this.clearBtn.style.display = 'none';
        this.fileInput.value = '';
        this.uploadedFile = null;
        this.resetResults();
    }

    resetResults() {
        this.resultsPlaceholder.style.display = 'flex';
        this.resultsDisplay.style.display = 'none';
        this.loadingState.style.display = 'none';
        this.resultsActions.style.display = 'none';
        this.confidenceFill.style.width = '0%';
    }
    
    async processImage() {
        if (!this.uploadedFile) return;
        
        this.showLoading();
        const formData = new FormData();
        formData.append('file', this.uploadedFile);

        try {
            const response = await fetch('/find-match', { method: 'POST', body: formData });
            const data = await response.json();

            if (data.success) {
                this.displayResults(data);
            } else {
                this.showError(data.error || 'An unknown server error occurred.');
                this.resetResults();
            }
        } catch (error) {
            this.showError('Cannot connect to the AI server. Please try again later.');
            this.resetResults();
        }
    }

    showLoading() {
        this.resultsPlaceholder.style.display = 'none';
        this.resultsDisplay.style.display = 'none';
        this.loadingState.style.display = 'flex';
        this.resultsActions.style.display = 'none';
    }

    displayResults(data) {
        this.loadingState.style.display = 'none';
        
        this.matchedImage.src = data.matched_image_url;
        const confidence = data.confidence;
        
        const urlParts = data.matched_image_url.split('/');
        const filename = urlParts[urlParts.length - 1];
        const actorNumber = filename.split('.')[0].split('_')[1];
        
        this.matchedName.textContent = `Doppelgänger #${actorNumber}`;
        this.matchedMovie.textContent = 'From the AI Database';
        this.confidenceValue.textContent = `${confidence}%`;
        
        this.resultsDisplay.style.display = 'block';
        this.resultsActions.style.display = 'flex';

        setTimeout(() => {
            this.confidenceFill.style.width = `${confidence}%`;
        }, 100);
    }
    
    shareResult() {
        alert("Sharing feature coming soon!");
    }

    resetApplication() {
        this.clearImage();
    }

    showError(message) {
        alert(`Error: ${message}`);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new MovieSelfieMatcher();
});