document.addEventListener("DOMContentLoaded", function () {
    // Upload page functionality
    let dropArea = document.getElementById("drop-area");
    let fileInput = document.getElementById("resumeFile");

    if (dropArea && fileInput) {
        dropArea.addEventListener("click", () => fileInput.click());

        dropArea.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropArea.classList.add('dragover');
        });

        dropArea.addEventListener("dragleave", () => {
            dropArea.classList.remove('dragover');
        });

        dropArea.addEventListener("drop", (e) => {
            e.preventDefault();
            dropArea.classList.remove('dragover');
            fileInput.files = e.dataTransfer.files;
            if (e.dataTransfer.files.length > 0) {
                updateFileName(e.dataTransfer.files[0]);
            }
        });
    }

    // Home page functionality
    // Show alert function
    function showAlert(message, type) {
        const alertBox = document.getElementById('alertBox');
        if (alertBox) {
            alertBox.className = `alert alert-${type} animate__animated animate__fadeIn`;
            alertBox.textContent = message;
            alertBox.style.display = 'block';
            setTimeout(() => {
                alertBox.classList.add('animate__fadeOut');
                setTimeout(() => {
                    alertBox.style.display = 'none';
                }, 500);
            }, 3000);
        } else {
            // For upload page
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} animate__animated animate__fadeIn`;
            alertDiv.innerHTML = `
                <i class="fas fa-${type === 'danger' ? 'exclamation-circle' : 'check-circle'} me-2"></i>
                ${message}
            `;
            document.querySelector('.card').insertBefore(alertDiv, document.getElementById('uploadForm'));
            
            setTimeout(() => {
                alertDiv.classList.add('animate__fadeOut');
                setTimeout(() => alertDiv.remove(), 500);
            }, 3000);
        }
    }

    // Password toggle functionality
    document.querySelectorAll('.password-toggle').forEach(toggle => {
        toggle.addEventListener('click', (e) => {
            const input = e.target.closest('.form-floating').querySelector('input');
            const type = input.type === 'password' ? 'text' : 'password';
            input.type = type;
            e.target.classList.toggle('fa-eye');
            e.target.classList.toggle('fa-eye-slash');
        });
    });

    // Switch between login and signup forms
    const authTabs = document.getElementById('authTabs');
    if (authTabs) {
        document.querySelectorAll('#authTabs .nav-link').forEach(tab => {
            tab.addEventListener('click', (e) => {
                document.querySelectorAll('#authTabs .nav-link').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
                
                e.target.classList.add('active');
                document.getElementById(e.target.dataset.form + 'Form').classList.add('active');
            });
        });
    }

    // Handle login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();
                if (response.ok) {
                    showAlert('Login successful! Redirecting...', 'success');
                    setTimeout(() => {
                        window.location.href = '/upload';
                    }, 1000);
                } else {
                    showAlert(data.error || 'Login failed', 'danger');
                }
            } catch (error) {
                showAlert('Error: ' + error.message, 'danger');
            }
        });
    }

    // Handle signup form submission
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('signupUsername').value;
            const password = document.getElementById('signupPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (password !== confirmPassword) {
                showAlert('Passwords do not match!', 'danger');
                return;
            }

            try {
                const response = await fetch('/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();
                if (response.ok) {
                    showAlert('Account created successfully!', 'success');
                    setTimeout(() => {
                        document.querySelector('[data-form="login"]').click();
                    }, 1000);
                } else {
                    showAlert(data.error || 'Signup failed', 'danger');
                }
            } catch (error) {
                showAlert('Error: ' + error.message, 'danger');
            }
        });
    }

    // Typing animation
    const typingText = document.querySelector('.typing-text');
    if (typingText) {
        const words = ['Match your profile with job requirements instantly', 'Get detailed analysis of your resume', 'Improve your job application success rate'];
        let wordIndex = 0;
        let charIndex = 0;
        let isDeleting = false;
        let isWaiting = false;

        function type() {
            const currentWord = words[wordIndex];
            if (isDeleting) {
                typingText.textContent = currentWord.substring(0, charIndex - 1);
                charIndex--;
            } else {
                typingText.textContent = currentWord.substring(0, charIndex + 1);
                charIndex++;
            }

            if (!isDeleting && charIndex === currentWord.length) {
                isWaiting = true;
                setTimeout(() => {
                    isDeleting = true;
                    isWaiting = false;
                }, 2000);
            } else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                wordIndex = (wordIndex + 1) % words.length;
            }

            const typingSpeed = isDeleting ? 50 : 100;
            if (!isWaiting) {
                setTimeout(type, typingSpeed);
            } else {
                setTimeout(type, 2000);
            }
        }

        type();
    }

    // Upload page specific functionality
    // Show loading overlay
    function showLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'block';
        }
    }

    // Hide loading overlay
    function hideLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }

    // Handle drag and drop for upload page
    const uploadDropArea = document.getElementById('drop-area');
    if (uploadDropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadDropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadDropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadDropArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            uploadDropArea.classList.add('dragover');
        }

        function unhighlight(e) {
            uploadDropArea.classList.remove('dragover');
        }

        uploadDropArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            document.getElementById('resumeFile').files = files;
            updateFileName(files[0]);
        }

        // Handle file selection
        const resumeFileInput = document.getElementById('resumeFile');
        if (resumeFileInput) {
            resumeFileInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                updateFileName(file);
            });
        }

        function updateFileName(file) {
            const fileNameElement = document.getElementById('fileName');
            if (fileNameElement) {
                const fileName = file?.name || 'No file selected';
                fileNameElement.innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-file-pdf me-2"></i>${fileName}
                    </div>
                `;
            }
        }
    }

    // Handle form submission for upload page
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            showLoading();

            const formData = new FormData();
            const file = document.getElementById('resumeFile').files[0];
            const jobDescription = document.getElementById('jobDescription').value;

            formData.append('resume', file);
            formData.append('job_description', jobDescription);

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                if (response.ok) {
                    // Show results
                    document.getElementById('result').style.display = 'block';
                    
                    // Update score circle
                    const scoreCircle = document.getElementById('scoreCircle');
                    scoreCircle.style.setProperty('--progress', `${data.match_percentage}%`);
                    scoreCircle.setAttribute('data-value', Math.round(data.match_percentage));
                    
                    // Update match percentage
                    document.getElementById('matchPercentage').textContent = 
                        `${data.match_percentage.toFixed(1)}% match with job description`;
                    
                    // Update keywords
                    const keywordsDiv = document.getElementById('keywords');
                    keywordsDiv.innerHTML = data.common_keywords
                        .map(keyword => `<span class="keyword-badge">${keyword}</span>`)
                        .join('');
                    
                    // Show download button
                    document.getElementById('downloadBtn').style.display = 'inline-block';
                    document.getElementById('downloadBtn').setAttribute('data-resume-id', data.resume_id);
                    
                    // Scroll to results
                    document.getElementById('result').scrollIntoView({ behavior: 'smooth' });
                } else {
                    showAlert(data.error || 'Upload failed', 'danger');
                }
            } catch (error) {
                showAlert('Error: ' + error.message, 'danger');
            } finally {
                hideLoading();
            }
        });
    }

    // Handle logout
    const logoutButton = document.querySelector('button[onclick="logout()"]');
    if (logoutButton) {
        logoutButton.removeAttribute('onclick');
        logoutButton.addEventListener('click', async function() {
            try {
                showLoading();
                const response = await fetch('/logout', {
                    method: 'POST'
                });

                if (response.ok) {
                    window.location.href = '/';
                } else {
                    showAlert('Logout failed', 'danger');
                }
            } catch (error) {
                showAlert('Error: ' + error.message, 'danger');
            } finally {
                hideLoading();
            }
        });
    }

    // Handle resume download
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.removeAttribute('onclick');
        downloadBtn.addEventListener('click', async function() {
            try {
                showLoading();
                const resumeId = this.getAttribute('data-resume-id');
                window.location.href = `/api/resumes/${resumeId}/download`;
            } catch (error) {
                showAlert('Error: ' + error.message, 'danger');
            } finally {
                setTimeout(hideLoading, 1000);
            }
        });
    }
});
