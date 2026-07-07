document.addEventListener('DOMContentLoaded', function() {
    // ============================================================
    // SIDEBAR & DROPDOWN LOGIC
    // ============================================================
    const moduleHeaders = document.querySelectorAll('.module-header');
    if (moduleHeaders) {
        moduleHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const moduleItem = this.parentElement;
                if (moduleItem) {
                    moduleItem.classList.toggle('active');
                    const lessonList = this.nextElementSibling;
                    if (lessonList) {
                        if (moduleItem.classList.contains('active')) {
                            lessonList.style.maxHeight = lessonList.scrollHeight + "px";
                        } else {
                            lessonList.style.maxHeight = null;
                        }
                    }
                }
            });
        });
    }

    // ============================================================
    // LESSON NAVIGATION & PLAYER LOGIC
    // ============================================================
    const lessonLinks = document.querySelectorAll('.lesson-link');
    const ytLayout = document.getElementById('youtube-layout');
    const placeholder = document.getElementById('video-placeholder');
    const currentLessonTitle = document.getElementById('current-lesson-title');
    const lessonDescriptionBox = document.getElementById('lesson-description-box');
    const pdfViewerContainer = document.getElementById('pdf-viewer-container');
    const driveFrameShield = document.getElementById('drive-frame-shield');
    const videoPlayerContainer = document.getElementById('video-player-container');
    const htmlViewerContainer = document.getElementById('html-viewer-container');
    const htmlContentInjectionPoint = document.getElementById('html-content-injection-point');
    const htmlIframe = document.getElementById('html-iframe');
    const htmlRawContent = document.getElementById('html-raw-content');
    const htmlStartOverlay = document.getElementById('html-start-overlay');
    const startHtmlBtn = document.getElementById('start-html-btn');
    const podcastContainer = document.getElementById('podcast-container');
    const simulacroContainer = document.getElementById('simulacro-container');
    const simulacroIframe = document.getElementById('simulacro-iframe');
    const specialContentContainer = document.getElementById('special-content-container');
    const specialContentLink = document.getElementById('special-content-link');
    const completeLessonBtn = document.getElementById('complete-lesson-btn');
    const likeBtn = document.getElementById('like-btn');
    const likeCount = document.getElementById('like-count');
    
    // --- Comment Elements ---
    const commentForm = document.getElementById('comment-form');
    const commentTextInput = document.getElementById('comment-text-input');
    const lessonIdInput = document.getElementById('lesson-id-input');
    const parentIdInput = document.getElementById('parent-id-input');
    const commentList = document.getElementById('comment-list');
    const commentCount = document.getElementById('comment-count');
    const replyIndicator = document.getElementById('reply-indicator');

    let player = null;
    const videoElement = document.getElementById('course-video-player');
    if (videoElement) {
        try {
            player = videojs('course-video-player', {
                fluid: true,
                responsive: true,
                controls: true,
                preload: 'auto',
                playbackRates: [0.5, 0.75, 1, 1.25, 1.5, 2],
                techOrder: ['html5', 'youtube'],
                controlBar: { pictureInPictureToggle: true },
                html5: { hls: { overrideNative: true }, nativeAudioTracks: false, nativeVideoTracks: false }
            });
        } catch (e) {
            console.error("Error al inicializar el reproductor de video:", e);
        }
    }

    // Global variables for podcast player
    let currentAudio = null;
    let currentPlayBtn = null;

    // Helper to format time (seconds -> MM:SS)
    function formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return "00:00";
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }

    // Save progress to localStorage
    function saveProgress(lessonId, time) {
        if (!lessonId) return;
        localStorage.setItem(`progress_${lessonId}`, time);
    }

    // Get progress from localStorage
    function getProgress(lessonId) {
        if (!lessonId) return 0;
        return parseFloat(localStorage.getItem(`progress_${lessonId}`)) || 0;
    }

    // Helper to convert URLs in text to clickable links
    function linkify(text) {
        if (!text) return '';
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return text.replace(urlRegex, function(url) {
            return '<a href="' + url + '" target="_blank" rel="noopener noreferrer">' + url + '</a>';
        });
    }

    function configureEmbedIframe(iframe, url, provider) {
        if (!iframe) return;

        iframe.src = '';
        iframe.allowFullscreen = true;
        iframe.setAttribute('allow', 'autoplay; fullscreen; encrypted-media; picture-in-picture');
        iframe.setAttribute('referrerpolicy', 'strict-origin-when-cross-origin');
        iframe.setAttribute('oncontextmenu', 'return false;');

        if (provider === 'google_drive') {
            iframe.setAttribute('sandbox', 'allow-scripts allow-same-origin allow-presentation');
            if (driveFrameShield) driveFrameShield.style.display = 'block';
        } else {
            iframe.removeAttribute('sandbox');
            if (driveFrameShield) driveFrameShield.style.display = 'none';
        }

        iframe.src = url;
    }

    // Handle Start HTML Button
    if (startHtmlBtn) {
        startHtmlBtn.addEventListener('click', function() {
            if (htmlStartOverlay) {
                htmlStartOverlay.style.display = 'none';
                if (htmlContentInjectionPoint) {
                    htmlContentInjectionPoint.style.overflow = 'auto';
                }
            }
        });
    }

    if (lessonLinks) {
        lessonLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();

                // Safe class removal
                lessonLinks.forEach(l => {
                    if (l && l.classList) l.classList.remove('active');
                });
                if (this.classList) this.classList.add('active');

                const lessonId = this.dataset.lessonId;
                const lessonTitle = this.dataset.title;
                const lessonType = this.dataset.lessonType;
                const lessonDescription = this.dataset.description;

                if(placeholder) placeholder.style.display = 'none';
                if(ytLayout) {
                    ytLayout.style.display = 'flex';
                    ytLayout.style.opacity = '0';
                    setTimeout(() => { if(ytLayout) ytLayout.style.opacity = '1'; }, 50);
                }

                if(currentLessonTitle) currentLessonTitle.textContent = lessonTitle;

                // Update Description Box
                if(lessonDescriptionBox) {
                    if (lessonDescription && lessonDescription.trim() !== "") {
                        lessonDescriptionBox.innerHTML = linkify(lessonDescription);
                        lessonDescriptionBox.style.display = 'block';
                    } else {
                        lessonDescriptionBox.style.display = 'none';
                        lessonDescriptionBox.innerHTML = '';
                    }
                }

                if(pdfViewerContainer) pdfViewerContainer.style.display = 'none';
                if(driveFrameShield) driveFrameShield.style.display = 'none';
                if(videoPlayerContainer) videoPlayerContainer.style.display = 'none';
                if(htmlViewerContainer) htmlViewerContainer.style.display = 'none';
                if(podcastContainer) podcastContainer.style.display = 'none';
                if(simulacroContainer) simulacroContainer.style.display = 'none';
                if(specialContentContainer) specialContentContainer.style.display = 'none';

                // Stop podcast audio if playing
                if (currentAudio) {
                    if (currentPlayBtn) {
                        const epId = currentPlayBtn.dataset.epId;
                        if (epId) saveProgress(`podcast_${epId}`, currentAudio.currentTime);
                    }
                    currentAudio.pause();
                    currentAudio = null;
                    if (currentPlayBtn) {
                         const icon = currentPlayBtn.querySelector('i');
                         if(icon && icon.classList) {
                             icon.classList.remove('fa-pause');
                             icon.classList.add('fa-play');
                         }
                         currentPlayBtn = null;
                    }
                }

                if (player) {
                    try {
                        const prevLessonId = lessonIdInput ? lessonIdInput.value : null;
                        if (prevLessonId && !player.paused()) {
                            saveProgress(`video_${prevLessonId}`, player.currentTime());
                        }
                        player.pause();
                        player.src('');
                    } catch(e) {
                        console.warn("Error al pausar el reproductor:", e);
                    }
                }

                if (completeLessonBtn) {
                    completeLessonBtn.dataset.lessonId = lessonId;
                    if (this.parentElement && this.parentElement.classList) {
                        updateCompleteButton(this.parentElement.classList.contains('completed'));
                    } else {
                        updateCompleteButton(false);
                    }
                }

                if (lessonIdInput) lessonIdInput.value = lessonId;
                if (parentIdInput) parentIdInput.value = '';
                if (replyIndicator) replyIndicator.style.display = 'none';

                fetchCommentsAndLikeStatus(lessonId);

                fetch(`/cursos/get_video_url/${lessonId}/`)
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(err => { throw new Error(err.error || 'Erro desconhecido'); });
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (lessonType === 'html') {
                            if(htmlViewerContainer && htmlContentInjectionPoint) {
                                htmlViewerContainer.style.display = 'block';

                                if (data.html_url) {
                                    if (htmlIframe) {
                                        htmlIframe.src = data.html_url;
                                        htmlIframe.style.display = 'block';
                                    }
                                    if (htmlRawContent) htmlRawContent.style.display = 'none';
                                } else {
                                    if (htmlRawContent) {
                                        htmlRawContent.innerHTML = data.html_content;
                                        htmlRawContent.style.display = 'block';
                                    }
                                    if (htmlIframe) htmlIframe.style.display = 'none';
                                }

                                if (htmlStartOverlay) {
                                    htmlStartOverlay.style.display = 'flex';
                                    htmlContentInjectionPoint.style.overflow = 'hidden';
                                }
                            }
                        } else if (lessonType === 'podcast') {
                            if(podcastContainer) {
                                podcastContainer.style.display = 'block';
                                renderPodcastEpisodes(data.podcast_episodes);
                            }
                        } else if (lessonType === 'simulacro') {
                            if (simulacroContainer && simulacroIframe) {
                                simulacroContainer.style.display = 'flex';
                                if (data.simulacro_url) {
                                    simulacroIframe.src = data.simulacro_url;
                                } else if (data.url) {
                                    simulacroIframe.src = data.url;
                                } else {
                                    simulacroIframe.src = '';
                                    alert("URL do simulacro não encontrada.");
                                }
                            }
                        } else if (lessonType === 'special_content') {
                            if (specialContentContainer && specialContentLink) {
                                specialContentContainer.style.display = 'flex';
                                if (data.special_content_url) {
                                    specialContentLink.href = data.special_content_url;
                                } else if (data.url) {
                                    specialContentLink.href = data.url;
                                } else {
                                    specialContentLink.href = '#';
                                    alert("URL do conteúdo especial não encontrada.");
                                }
                            }
                        } else if (data.url) {
                            if (lessonType === 'video') {
                                if (data.player === 'iframe') {
                                    if(pdfViewerContainer) {
                                        pdfViewerContainer.style.display = 'block';
                                        const iframe = pdfViewerContainer.querySelector('iframe');
                                        configureEmbedIframe(iframe, data.embed_url || data.url, data.provider);
                                    }
                                    return;
                                }

                                if(videoPlayerContainer) videoPlayerContainer.style.display = 'block';
                                if (player) {
                                    if (!data.url) {
                                        console.error("URL do vídeo vazia.");
                                        return;
                                    }

                                    let mimeType = data.mime_type || 'video/mp4';

                                    player.src({ type: mimeType, src: data.url });
                                    player.load();

                                    const savedTime = getProgress(`video_${lessonId}`);
                                    if (savedTime > 0) {
                                        player.currentTime(savedTime);
                                    }

                                    player.play().catch(e => console.log("Autoplay blocked:", e));

                                    player.on('timeupdate', () => {
                                        saveProgress(`video_${lessonId}`, player.currentTime());
                                    });
                                } else {
                                    console.error("Reproductor de video no inicializado.");
                                    alert("Error: Reproductor de video no disponible.");
                                }
                            } else if (lessonType === 'pdf') {
                                if(pdfViewerContainer) {
                                    pdfViewerContainer.style.display = 'block';
                                    const iframe = pdfViewerContainer.querySelector('iframe');
                                    configureEmbedIframe(iframe, data.url, data.provider);
                                }
                            }
                        } else {
                            console.warn("Resposta sem URL:", data);
                            alert("Contenido no encontrado para esta clase.");
                        }
                    })
                    .catch(error => {
                        console.error("Error en la solicitud:", error);
                        alert("Error al cargar la clase: " + error.message);
                    });
            });
        });
    }

    // --- PODCAST RENDERER ---
    function renderPodcastEpisodes(episodes) {
        const container = document.getElementById('podcast-episodes-list');
        if (!container) return;

        container.innerHTML = '';
        if (!episodes || episodes.length === 0) {
            container.innerHTML = '<p style="color:var(--muted); text-align:center;">No hay episodios disponibles.</p>';
            return;
        }

        episodes.forEach((ep, index) => {
            const item = document.createElement('div');
            item.className = 'podcast-item';
            const epId = ep.id || `ep_${index}`;

            item.innerHTML = `
                <button class="podcast-play-btn" data-src="${ep.url}" data-ep-id="${epId}">
                    <i class="fas fa-play"></i>
                </button>
                <div class="podcast-info">
                    <span class="podcast-ep-title">${ep.title}</span>
                    <div class="podcast-ep-meta">
                        <span>Episodio ${index + 1}</span>
                    </div>
                    <div class="podcast-controls" style="display:flex; align-items:center; gap:10px; margin-top:5px;">
                        <span class="current-time" style="font-size:0.75rem; color:#b3b3b3; min-width:35px;">00:00</span>
                        <input type="range" class="podcast-progress" min="0" max="100" value="0" style="flex:1; cursor:pointer;">
                        <span class="duration" style="font-size:0.75rem; color:#b3b3b3; min-width:35px;">--:--</span>
                    </div>
                </div>
            `;
            container.appendChild(item);
        });

        const playBtns = container.querySelectorAll('.podcast-play-btn');

        playBtns.forEach(btn => {
            const parent = btn.parentElement;
            const progressBar = parent.querySelector('.podcast-progress');
            const currentTimeEl = parent.querySelector('.current-time');
            const durationEl = parent.querySelector('.duration');
            const epId = btn.dataset.epId;

            const savedTime = getProgress(`podcast_${epId}`);
            if (savedTime > 0) {
                currentTimeEl.textContent = formatTime(savedTime);
            }

            btn.addEventListener('click', function() {
                const src = this.dataset.src;
                const icon = this.querySelector('i');

                if (currentPlayBtn === this && currentAudio) {
                    if (currentAudio.paused) {
                        currentAudio.play();
                        if(icon && icon.classList) {
                            icon.classList.remove('fa-play');
                            icon.classList.add('fa-pause');
                        }
                    } else {
                        currentAudio.pause();
                        if(icon && icon.classList) {
                            icon.classList.remove('fa-pause');
                            icon.classList.add('fa-play');
                        }
                        saveProgress(`podcast_${epId}`, currentAudio.currentTime);
                    }
                } else {
                    if (currentAudio) {
                        if (currentPlayBtn) {
                            const prevEpId = currentPlayBtn.dataset.epId;
                            saveProgress(`podcast_${prevEpId}`, currentAudio.currentTime);

                            const prevIcon = currentPlayBtn.querySelector('i');
                            if (prevIcon && prevIcon.classList) {
                                prevIcon.classList.remove('fa-pause');
                                prevIcon.classList.add('fa-play');
                            }
                        }
                        currentAudio.pause();
                    }

                    currentAudio = new Audio(src);
                    currentPlayBtn = this;

                    const savedTime = getProgress(`podcast_${epId}`);
                    if (savedTime > 0) {
                        currentAudio.currentTime = savedTime;
                    }

                    currentAudio.addEventListener('loadedmetadata', () => {
                        if(durationEl) durationEl.textContent = formatTime(currentAudio.duration);
                        if(progressBar) progressBar.max = currentAudio.duration;
                        if (savedTime > 0 && progressBar) progressBar.value = savedTime;
                    });

                    currentAudio.addEventListener('timeupdate', () => {
                        if (currentAudio) {
                            if(progressBar) progressBar.value = currentAudio.currentTime;
                            if(currentTimeEl) currentTimeEl.textContent = formatTime(currentAudio.currentTime);
                            if (Math.floor(currentAudio.currentTime) % 5 === 0) {
                                saveProgress(`podcast_${epId}`, currentAudio.currentTime);
                            }
                        }
                    });

                    currentAudio.addEventListener('ended', () => {
                        if(icon && icon.classList) {
                            icon.classList.remove('fa-pause');
                            icon.classList.add('fa-play');
                        }
                        saveProgress(`podcast_${epId}`, 0);
                        if(progressBar) progressBar.value = 0;
                        if(currentTimeEl) currentTimeEl.textContent = "00:00";
                        currentAudio = null;
                        currentPlayBtn = null;
                    });

                    currentAudio.play().catch(e => console.error("Audio play error:", e));
                    if(icon && icon.classList) {
                        icon.classList.remove('fa-play');
                        icon.classList.add('fa-pause');
                    }
                }
            });

            if(progressBar) {
                progressBar.addEventListener('input', function() {
                    const time = parseFloat(this.value);
                    if(currentTimeEl) currentTimeEl.textContent = formatTime(time);
                    if (currentPlayBtn === btn && currentAudio) {
                        currentAudio.currentTime = time;
                    } else {
                        saveProgress(`podcast_${epId}`, time);
                    }
                });
            }
        });
    }

    // ============================================================
    // COMPLETE LESSON LOGIC
    // ============================================================
    function updateCompleteButton(isCompleted) {
        if (completeLessonBtn) {
            completeLessonBtn.disabled = isCompleted;
            if (isCompleted) {
                if(completeLessonBtn.classList) completeLessonBtn.classList.add('completed');
                completeLessonBtn.innerHTML = '<i class="fas fa-check-double"></i> Completada';
            } else {
                if(completeLessonBtn.classList) completeLessonBtn.classList.remove('completed');
                completeLessonBtn.innerHTML = '<i class="fas fa-check"></i> Marcar como Completada';
            }
        }
    }

    if (completeLessonBtn) {
        completeLessonBtn.addEventListener('click', function() {
            const lessonId = this.dataset.lessonId;
            if (!lessonId || this.disabled) return;

            fetch(`/cursos/mark-lesson-complete/${lessonId}/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateCompleteButton(true);
                    const activeLink = document.querySelector(`.lesson-link[data-lesson-id="${lessonId}"]`);
                    if (activeLink && activeLink.parentElement && activeLink.parentElement.classList) {
                        activeLink.parentElement.classList.add('completed');
                        const icon = activeLink.querySelector('.lesson-status-icon');
                        if (icon && icon.classList) {
                            icon.classList.remove('far', 'fa-circle');
                            icon.classList.add('fas', 'fa-check-circle');
                        }
                    }
                }
            })
            .catch(error => console.error('Error:', error));
        });
    }

    // ============================================================
    // COMMENTS & LIKE LOGIC
    // ============================================================
    function fetchCommentsAndLikeStatus(lessonId) {
        fetch(`/cursos/lesson/${lessonId}/comments/`)
            .then(response => response.json())
            .then(data => {
                renderComments(data.comments);
                updateLikeButton(data.user_has_liked, data.like_count);
            })
            .catch(error => console.error('Error fetching data:', error));
    }

    function renderComments(comments) {
        if (!commentList) return;
        commentList.innerHTML = '';
        
        let totalCount = comments.length;
        comments.forEach(c => totalCount += c.replies.length);
        if(commentCount) commentCount.innerText = totalCount;

        if (comments.length > 0) {
            comments.forEach(comment => {
                const commentEl = createCommentElement(comment);
                commentList.appendChild(commentEl);

                if (comment.replies && comment.replies.length > 0) {
                    const repliesContainer = document.createElement('div');
                    repliesContainer.style.marginLeft = '50px';
                    repliesContainer.style.marginTop = '10px';
                    
                    comment.replies.forEach(reply => {
                        const replyEl = createCommentElement(reply, false);
                        repliesContainer.appendChild(replyEl);
                    });
                    commentList.appendChild(repliesContainer);
                }
            });
        } else {
            commentList.innerHTML = '<p style="color: var(--muted); text-align: center;">Sé el primero en comentar.</p>';
        }
    }

    function createCommentElement(data, canReply = true) {
        const el = document.createElement('div');
        el.classList.add('comment-item');
        
        let replyButtonHtml = '';
        if (canReply) {
            replyButtonHtml = `<div class="comment-action reply-btn" data-comment-id="${data.id}" data-author="${data.author}">Responder</div>`;
        }

        el.innerHTML = `
            <div class="user-avatar-small">${data.author_initial}</div>
            <div class="comment-content">
                <div class="comment-author">${data.author} <span class="comment-date">${data.created_at}</span></div>
                <div class="comment-text">${data.text}</div>
                <div class="comment-actions">
                    ${replyButtonHtml}
                </div>
            </div>
        `;
        return el;
    }

    if (commentList) {
        commentList.addEventListener('click', function(e) {
            if (e.target.classList.contains('reply-btn')) {
                const commentId = e.target.dataset.commentId;
                const author = e.target.dataset.author;
                
                if (parentIdInput) parentIdInput.value = commentId;
                if (commentTextInput) {
                    commentTextInput.placeholder = `Respondiendo a ${author}...`;
                    commentTextInput.focus();
                }

                if (replyIndicator) {
                    replyIndicator.style.display = 'flex';
                    replyIndicator.innerHTML = `Respondiendo a <strong>${author}</strong> <span id="cancel-reply" style="cursor:pointer; margin-left:10px; color:var(--danger);">✕</span>`;

                    const cancelBtn = document.getElementById('cancel-reply');
                    if(cancelBtn) {
                        cancelBtn.addEventListener('click', function() {
                            if(parentIdInput) parentIdInput.value = '';
                            if(commentTextInput) commentTextInput.placeholder = 'Añade un comentario...';
                            replyIndicator.style.display = 'none';
                        });
                    }
                }
            }
        });
    }

    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const lessonId = lessonIdInput ? lessonIdInput.value : null;
            const commentText = commentTextInput ? commentTextInput.value.trim() : null;
            const parentId = parentIdInput ? parentIdInput.value : null;

            if (!lessonId || !commentText) return;

            const payload = { text: commentText };
            if (parentId) payload.parent_id = parentId;

            fetch(`/cursos/lesson/${lessonId}/comments/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': CSRF_TOKEN,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    fetchCommentsAndLikeStatus(lessonId);
                    
                    if(commentTextInput) commentTextInput.value = '';
                    if (parentIdInput) parentIdInput.value = '';
                    if (commentTextInput) commentTextInput.placeholder = 'Añade un comentario...';
                    if (replyIndicator) replyIndicator.style.display = 'none';
                } else {
                    alert(data.message || 'Error al enviar el comentario.');
                }
            })
            .catch(error => console.error('Error submitting comment:', error));
        });
    }

    // --- LIKE LOGIC ---
    function updateLikeButton(liked, count) {
        if (likeBtn && likeCount) {
            likeCount.innerText = count;
            const icon = likeBtn.querySelector('i');
            if (liked) {
                if(likeBtn.classList) likeBtn.classList.add('active');
                if(icon && icon.classList) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                }
            } else {
                if(likeBtn.classList) likeBtn.classList.remove('active');
                if(icon && icon.classList) {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                }
            }
        }
    }

    if (likeBtn) {
        likeBtn.addEventListener('click', function() {
            const lessonId = lessonIdInput ? lessonIdInput.value : null;
            if (!lessonId) return;

            fetch(`/cursos/lesson/${lessonId}/like/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': CSRF_TOKEN,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateLikeButton(data.liked, data.like_count);
                }
            })
            .catch(error => console.error('Error toggling like:', error));
        });
    }
});
