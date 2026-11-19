// NexCode Frontend Application

class NexCodeApp {
    constructor() {
        this.currentNotebook = null;
        this.notebooks = [];
        this.currentTokens = 0;
        this.maxTokens = 200000;
        this.files = {};
        this.openFiles = [];
        this.activeFile = null;
        this.selectedModel = 'openrouter';
        this.isRecording = false;
        this.recognition = null;
        
        this.init();
    }
    
    async init() {
        this.bindEvents();
        this.initSpeechRecognition();
        await this.loadNotebooks();
        
        // Auto-create first notebook if none exist
        if (this.notebooks.length === 0) {
            await this.createNewNotebook('Default Session');
        } else {
            // Load the first notebook
            await this.loadNotebook(this.notebooks[0].id);
        }
    }
    
    bindEvents() {
        // New notebook
        document.getElementById('newNotebookBtn').addEventListener('click', () => this.createNewNotebook());
        
        // Model selection
        document.getElementById('modelSelect').addEventListener('change', (e) => {
            this.selectedModel = e.target.value;
        });
        
        // Folder input
        document.getElementById('browseFolderBtn').addEventListener('click', () => this.handleFolderSelect());
        document.getElementById('folderInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.loadFolderFromPath();
            }
        });
        
        // Chat input
        document.getElementById('sendBtn').addEventListener('click', () => this.sendMessage());
        document.getElementById('promptInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Dictation button
        document.getElementById('dictationBtn').addEventListener('click', () => this.toggleDictation());
        
        // Export and sync buttons
        document.getElementById('exportBtn').addEventListener('click', () => this.downloadZip());
        document.getElementById('syncGithubBtn').addEventListener('click', () => this.syncGithub());
    }
    
    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = true;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
            
            this.recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript;
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                const promptInput = document.getElementById('promptInput');
                if (finalTranscript) {
                    promptInput.value += finalTranscript + ' ';
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.stopDictation();
                alert('Speech recognition error: ' + event.error);
            };
            
            this.recognition.onend = () => {
                if (this.isRecording) {
                    this.recognition.start();
                }
            };
        } else {
            document.getElementById('dictationBtn').style.display = 'none';
            console.warn('Speech recognition not supported in this browser');
        }
    }
    
    toggleDictation() {
        if (this.isRecording) {
            this.stopDictation();
        } else {
            this.startDictation();
        }
    }
    
    startDictation() {
        if (!this.recognition) {
            alert('Speech recognition is not supported in your browser');
            return;
        }
        
        this.isRecording = true;
        this.recognition.start();
        document.getElementById('dictationBtn').classList.add('recording');
    }
    
    stopDictation() {
        this.isRecording = false;
        if (this.recognition) {
            this.recognition.stop();
        }
        document.getElementById('dictationBtn').classList.remove('recording');
    }
    
    async loadNotebooks() {
        try {
            const response = await fetch('/api/notebook/');
            this.notebooks = await response.json();
            this.renderNotebooks();
        } catch (error) {
            console.error('Failed to load notebooks:', error);
        }
    }
    
    renderNotebooks() {
        const notebookList = document.getElementById('notebookList');
        notebookList.innerHTML = '';
        
        if (this.notebooks.length === 0) {
            notebookList.innerHTML = '<div class="empty-state">No notebooks yet</div>';
            return;
        }
        
        this.notebooks.forEach(notebook => {
            const item = document.createElement('div');
            item.className = 'notebook-item';
            if (this.currentNotebook && this.currentNotebook.id === notebook.id) {
                item.classList.add('active');
            }
            item.innerHTML = `
                <span class="notebook-name">${this.escapeHtml(notebook.name)}</span>
                <span class="notebook-time">${this.formatTime(notebook.updated_at)}</span>
                <button class="delete-btn" title="Delete">🗑</button>
            `;
            
            item.addEventListener('click', (e) => {
                if (!e.target.classList.contains('delete-btn')) {
                    this.loadNotebook(notebook.id);
                }
            });
            
            item.querySelector('.delete-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteNotebook(notebook.id);
            });
            
            notebookList.appendChild(item);
        });
    }
    
    async createNewNotebook(name = null) {
        const notebookName = name || prompt('Enter notebook name:', 'New Session');
        if (!notebookName) return;
        
        try {
            const response = await fetch('/api/notebook/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: notebookName })
            });
            
            const notebook = await response.json();
            this.currentNotebook = notebook;
            this.notebooks.unshift(notebook);
            this.renderNotebooks();
            
            // Clear files and chat
            this.files = {};
            this.openFiles = [];
            this.activeFile = null;
            this.currentTokens = 0;
            this.updateTokenDisplay();
            this.renderFileTabs();
            this.clearChat();
            
            if (!name) {
                alert('New notebook created: ' + notebook.name);
            }
        } catch (error) {
            console.error('Failed to create notebook:', error);
            alert('Failed to create notebook. Please try again.');
        }
    }
    
    async loadNotebook(notebookId) {
        try {
            const response = await fetch(`/api/notebook/${notebookId}`);
            const notebook = await response.json();
            this.currentNotebook = notebook;
            
            // Load context if available
            if (notebook.context) {
                this.files = notebook.context.files || {};
                this.currentTokens = notebook.context.total_tokens || 0;
                this.updateTokenDisplay();
                
                // Open first few files
                const fileNames = Object.keys(this.files).slice(0, 5);
                this.openFiles = fileNames;
                if (fileNames.length > 0) {
                    this.activeFile = fileNames[0];
                }
                this.renderFileTabs();
                this.renderCodePreview();
            }
            
            this.renderNotebooks();
        } catch (error) {
            console.error('Failed to load notebook:', error);
            alert('Failed to load notebook. Please try again.');
        }
    }
    
    async deleteNotebook(notebookId) {
        if (!confirm('Delete this notebook?')) return;
        
        try {
            await fetch(`/api/notebook/${notebookId}`, { method: 'DELETE' });
            this.notebooks = this.notebooks.filter(n => n.id !== notebookId);
            this.renderNotebooks();
            
            if (this.currentNotebook && this.currentNotebook.id === notebookId) {
                this.currentNotebook = null;
                this.files = {};
                this.openFiles = [];
                this.activeFile = null;
                this.renderFileTabs();
                this.renderCodePreview();
            }
        } catch (error) {
            console.error('Failed to delete notebook:', error);
            alert('Failed to delete notebook. Please try again.');
        }
    }
    
    handleFolderSelect() {
        const input = document.createElement('input');
        input.type = 'file';
        input.webkitdirectory = true;
        input.multiple = true;
        
        input.onchange = (e) => this.processFiles(e.target.files);
        input.click();
    }
    
    async loadFolderFromPath() {
        const path = document.getElementById('folderInput').value.trim();
        if (!path) return;
        
        alert('Loading from path is not supported in browser. Please use the Browse button to select a folder.');
    }
    
    async processFiles(fileList) {
        this.files = {};
        let fileCount = 0;
        
        for (const file of fileList) {
            if (this.shouldExcludeFile(file.name)) {
                continue;
            }
            
            try {
                const content = await this.readFile(file);
                this.files[file.webkitRelativePath || file.name] = content;
                fileCount++;
            } catch (error) {
                console.error(`Failed to read ${file.name}:`, error);
            }
        }
        
        // Update UI
        document.getElementById('folderInput').value = `Loaded ${fileCount} files`;
        
        // Open first few files
        const fileNames = Object.keys(this.files).slice(0, 5);
        this.openFiles = fileNames;
        if (fileNames.length > 0) {
            this.activeFile = fileNames[0];
        }
        
        this.renderFileTabs();
        this.renderCodePreview();
        await this.updateTokenCount();
        
        // Save to notebook
        if (this.currentNotebook) {
            await this.saveNotebookContext();
        }
    }
    
    shouldExcludeFile(filename) {
        const exclusions = ['.git', 'node_modules', 'venv', '__pycache__', '.pyc', '.DS_Store'];
        return exclusions.some(excl => filename.includes(excl));
    }
    
    readFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }
    
    renderFileTabs() {
        const fileTabs = document.getElementById('fileTabs');
        fileTabs.innerHTML = '';
        
        if (this.openFiles.length === 0) {
            return;
        }
        
        this.openFiles.forEach(filename => {
            const tab = document.createElement('div');
            tab.className = 'file-tab';
            if (this.activeFile === filename) {
                tab.classList.add('active');
            }
            tab.innerHTML = `
                ${this.getShortFileName(filename)}
                <span class="close-tab">✕</span>
            `;
            
            tab.addEventListener('click', (e) => {
                if (!e.target.classList.contains('close-tab')) {
                    this.activeFile = filename;
                    this.renderFileTabs();
                    this.renderCodePreview();
                }
            });
            
            tab.querySelector('.close-tab').addEventListener('click', (e) => {
                e.stopPropagation();
                this.closeFile(filename);
            });
            
            fileTabs.appendChild(tab);
        });
    }
    
    getShortFileName(filename) {
        const parts = filename.split('/');
        return parts[parts.length - 1];
    }
    
    closeFile(filename) {
        this.openFiles = this.openFiles.filter(f => f !== filename);
        if (this.activeFile === filename) {
            this.activeFile = this.openFiles.length > 0 ? this.openFiles[0] : null;
        }
        this.renderFileTabs();
        this.renderCodePreview();
    }
    
    renderCodePreview() {
        const codePreview = document.getElementById('codePreview');
        
        if (!this.activeFile || !this.files[this.activeFile]) {
            codePreview.innerHTML = '<div class="empty-code">No file selected</div>';
            return;
        }
        
        const content = this.files[this.activeFile];
        const lines = content.split('\n');
        
        codePreview.innerHTML = lines.map((line, i) => `
            <div class="code-line">
                <div class="code-line-number">${i + 1}</div>
                <div class="code-line-content">${this.escapeHtml(line) || ' '}</div>
            </div>
        `).join('');
    }
    
    async updateTokenCount() {
        try {
            const response = await fetch('/api/llm/analyze-workspace', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.files)
            });
            
            const data = await response.json();
            this.currentTokens = data.total_tokens;
            this.updateTokenDisplay();
        } catch (error) {
            console.error('Failed to analyze workspace:', error);
        }
    }
    
    async saveNotebookContext() {
        if (!this.currentNotebook) return;
        
        try {
            await fetch(`/api/notebook/${this.currentNotebook.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    files: this.files,
                    total_tokens: this.currentTokens
                })
            });
        } catch (error) {
            console.error('Failed to save notebook context:', error);
        }
    }
    
    updateTokenDisplay() {
        const percentage = (this.currentTokens / this.maxTokens) * 100;
        document.getElementById('tokenCount').textContent = this.currentTokens.toLocaleString();
        document.getElementById('tokenPercent').textContent = percentage.toFixed(1);
    }
    
    async sendMessage() {
        const input = document.getElementById('promptInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        // Update status to working
        this.updateStatus('working');
        
        // Add user message
        this.addMessage('user', message);
        input.value = '';
        
        // Stop dictation if recording
        if (this.isRecording) {
            this.stopDictation();
        }
        
        // Add loading indicator
        const loadingId = this.addLoadingMessage();
        
        try {
            const response = await fetch('/api/llm/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    notebook_id: this.currentNotebook?.id || 'default',
                    message: message,
                    mode: 'file',
                    model: this.selectedModel,
                    files: Object.keys(this.files),
                    context: {
                        files: this.files,
                        total_tokens: this.currentTokens
                    }
                })
            });
            
            const data = await response.json();
            
            // Remove loading
            document.getElementById(loadingId).remove();
            
            // Add assistant response
            this.addMessage('assistant', data.response);
            
            // Update token usage
            this.currentTokens = data.token_usage?.total_tokens || this.currentTokens;
            this.updateTokenDisplay();
            
            // Check if response contains file modifications
            if (data.modified_files) {
                this.handleFileModifications(data.modified_files);
            }
            
            // Update status back to working
            this.updateStatus('working');
            
        } catch (error) {
            document.getElementById(loadingId).remove();
            this.addMessage('assistant', 'Error: Failed to get response. Please check your API configuration.');
            console.error('Chat error:', error);
            
            // Update status to error
            this.updateStatus('error');
        }
    }
    
    updateStatus(status) {
        const statusBadge = document.getElementById('statusBadge');
        statusBadge.className = 'status-badge ' + status;
        
        if (status === 'working') {
            statusBadge.textContent = 'Chatbot working';
        } else if (status === 'error') {
            statusBadge.textContent = 'Chatbot not able to work';
        }
    }
    
    handleFileModifications(modifiedFiles) {
        // Update files with modifications
        Object.keys(modifiedFiles).forEach(filename => {
            if (this.files[filename]) {
                this.files[filename] = modifiedFiles[filename];
            }
        });
        
        // Refresh code preview if active file was modified
        if (this.activeFile && modifiedFiles[this.activeFile]) {
            this.renderCodePreview();
        }
        
        // Save to notebook
        this.saveNotebookContext();
    }
    
    addMessage(role, content) {
        const container = document.getElementById('chatMessages');
        const message = document.createElement('div');
        message.className = `chat-message ${role}`;
        message.innerHTML = `
            <div class="message-role">${role}</div>
            ${this.escapeHtml(content)}
        `;
        container.appendChild(message);
        container.scrollTop = container.scrollHeight;
    }
    
    addLoadingMessage() {
        const container = document.getElementById('chatMessages');
        const loadingId = 'loading-' + Date.now();
        const message = document.createElement('div');
        message.id = loadingId;
        message.className = 'chat-message assistant';
        message.innerHTML = `
            <div class="message-role">Assistant</div>
            Thinking...
        `;
        container.appendChild(message);
        container.scrollTop = container.scrollHeight;
        return loadingId;
    }
    
    clearChat() {
        const container = document.getElementById('chatMessages');
        container.innerHTML = `
            <div class="chat-message assistant">
                <div class="message-role">Assistant</div>
                Welcome to NexCode V2.0! Upload a folder or type your prompt below. Use the microphone button for voice input.
            </div>
        `;
    }
    
    downloadZip() {
        alert('Download .ZIP feature coming soon! This will package your workspace files into a downloadable archive.');
    }
    
    syncGithub() {
        alert('GitHub sync feature coming soon! This will allow you to sync your workspace with a GitHub repository.');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    formatTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return date.toLocaleDateString();
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.nexcode = new NexCodeApp();
});
