class MovieSelfieMatcher {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.setupDragAndDrop();
    }

    initializeElements() {
        // --- Input Elements ---
        this.uploadArea = document.getElementById('uploadArea');
        this.uploadPlaceholder = document.getElementById('uploadPlaceholder');
        this.fileInput = document.getElementById('fileInput');
        this.previewImage = document.getElementById('previewImage');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.clearBtn = document.getElementById('clearBtn');

        // --- Results Elements ---
        this.resultsContent = document.getElementById('resultsContent');
        this.resultsPlaceholder = document.getElementById('resultsPlaceholder');
        this.resultsDisplay = document.getElementById('resultsDisplay');
        this.loadingState = document.getElementById('loadingState');
        this.resultsActions = document.getElementById('resultsActions');
        
        // --- Match Data Elements ---
        this.matchedImage = document.getElementById('matchedImage');
        this.matchedName = document.getElementById('matchedName');
        this.matchedMovie = document.getElementById('matchedMovie');
        
        // --- AI Roast Elements ---
        this.roastContainer = document.getElementById('roastContainer');
        this.roastMessage = document.getElementById('roastMessage');

        // --- Action Buttons ---
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
            if (files && files.length > 0) {
                this.handleFile(files[0]);
            }
        }, false);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files && files.length > 0) {
            this.handleFile(files[0]);
        }
    }

    handleFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            this.showError('Please select a valid image file.');
            return;
        }
        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            this.showError('File size must be less than 10MB.');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            this.displayPreview(e.target.result);
            this.processImage(file); 
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
        this.resetResults();
    }

    resetResults() {
        this.resultsPlaceholder.style.display = 'flex';
        this.resultsDisplay.style.display = 'none';
        this.loadingState.style.display = 'none';
        this.resultsActions.style.display = 'none';
        this.roastContainer.style.display = 'none';
        this.roastMessage.textContent = '';
    }
    
    async processImage(file) {
        if (!file) {
            this.showError("Something went wrong. No file to process.");
            return;
        }
        
        this.showLoading();
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/find-match', { method: 'POST', body: formData });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'An unknown server error occurred.' }));
                this.showError(errorData.error);
                this.resetResults();
                return;
            }

            const data = await response.json();

            if (data.success) {
                this.displayResults(data);
            } else {
                this.showError(data.error || 'The server reported an issue.');
                this.resetResults();
            }
        } catch (error) {
            console.error("Fetch Error:", error);
            this.showError('Cannot connect to the AI server. Please make sure it is running and try again.');
            this.resetResults();
        }
    }

    showLoading() {
        this.resultsPlaceholder.style.display = 'none';
        this.resultsDisplay.style.display = 'none';
        this.loadingState.style.display = 'flex';
        this.resultsActions.style.display = 'none';
        this.roastContainer.style.display = 'none';
    }

    displayResults(data) {
        this.loadingState.style.display = 'none';
        
        this.matchedImage.src = data.matched_image_url;
        
        const urlParts = data.matched_image_url.split('/');
        const filename = urlParts[urlParts.length - 1];
        const actorNumber = filename.split('.')[0].split('_')[1] || 'X';
        
        this.matchedName.textContent = `Doppelgänger #${actorNumber}`;
        this.matchedMovie.textContent = 'From the Movie Database -- custom made';
        
        // Display the roast message from the server
        if (data.roast_message) {
            this.roastMessage.textContent = data.roast_message;
            this.roastContainer.style.display = 'block';
        } else {
            this.roastContainer.style.display = 'none';
        }
        
        this.resultsDisplay.style.display = 'block';
        this.resultsActions.style.display = 'flex';
    }
    
    shareResult() {
        alert("Sharing feature coming soon!");
    }

    resetApplication() {
        this.clearImage();
    }

    showError(message) {
        alert(`Oops! Something went wrong:\n\n${message}`);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new MovieSelfieMatcher();
});                     