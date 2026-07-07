document.addEventListener('DOMContentLoaded', function() {
    const lessonDisplayArea = document.getElementById('lesson-display-area');
    const openLessonButtons = document.querySelectorAll('.open-lesson-btn');
    const moduleTitles = document.querySelectorAll('.module-title');
    const navItems = document.querySelectorAll('.sidebar-nav > .nav-item'); // Seleciona apenas os itens de navegação principais
    const contentDropdownToggle = document.getElementById('content-dropdown-toggle');
    const contentDropdown = document.querySelector('.nav-item-dropdown');
    const dashboardContents = document.querySelectorAll('.dashboard-content');

    // --- Função de Som ---
    const soundUrl = document.body.dataset.clickSoundUrl;
    const clickSound = new Audio(soundUrl);
    function playClickSound() {
        if (soundUrl) {
            clickSound.currentTime = 0;
            clickSound.play().catch(err => console.error("Erro ao tocar o som:", err));
        }
    }

    // Lógica para abrir/fechar o dropdown de conteúdo
    if (contentDropdownToggle) {
        contentDropdownToggle.addEventListener('click', function(e) {
            e.preventDefault();
            playClickSound();
            contentDropdown.classList.toggle('open');
        });
    }

    // Lógica do Acordeão para Módulos internos
    moduleTitles.forEach(title => {
        title.addEventListener('click', function() {
            playClickSound();
            this.closest('.module').classList.toggle('active');
        });
    });

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Lógica para abrir aulas
    openLessonButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            playClickSound();

            // Ativa a seção de conteúdo da aula
            navItems.forEach(nav => nav.classList.remove('active'));
            dashboardContents.forEach(content => content.classList.remove('active'));
            document.getElementById('course-content-area').classList.add('active');

            const lessonItem = this.closest('.lesson-item');
            document.querySelectorAll('.lesson-item').forEach(li => li.classList.remove('active'));
            lessonItem.classList.add('active');

            const url = this.dataset.url;
            const type = this.dataset.type.toLowerCase();
            const lessonId = this.dataset.lessonId;

            fetch(`/cursos/aula/${lessonId}/marcar-como-concluida/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrftoken, 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.created) {
                    lessonItem.classList.add('completed');
                    const counter = lessonItem.closest('.module-box').querySelector('.lesson-counter');
                    if (counter) {
                        const parts = counter.textContent.match(/(\d+)\/(\d+)/);
                        const newCount = parseInt(parts[1]) + 1;
                        counter.textContent = `(${newCount}/${parts[2]})`;
                    }
                }
            });

            lessonDisplayArea.style.opacity = 0;
            setTimeout(() => {
                lessonDisplayArea.innerHTML = '';
                if (type === 'pdf') {
                    const pdfViewer = document.createElement('iframe');
                    pdfViewer.src = url;
                    pdfViewer.className = 'lesson-viewer';
                    lessonDisplayArea.appendChild(pdfViewer);
                } else if (['mp4', 'webm', 'ogg'].includes(type)) {
                    const videoPlayer = document.createElement('video');
                    videoPlayer.src = url;
                    videoPlayer.controls = true;
                    videoPlayer.autoplay = true;
                    videoPlayer.className = 'lesson-viewer';
                    lessonDisplayArea.appendChild(videoPlayer);
                } else {
                    const downloadContainer = document.createElement('div');
                    downloadContainer.className = 'download-container';
                    downloadContainer.innerHTML = `<p>Este arquivo não pode ser pré-visualizado.</p><a href="${url}" class="course-card-btn" download>Baixar arquivo</a>`;
                    lessonDisplayArea.appendChild(downloadContainer);
                }
                lessonDisplayArea.style.opacity = 1;
            }, 400);
        });
    });

    // Lógica de navegação para os itens principais (que não são o dropdown)
    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            playClickSound();
            
            navItems.forEach(nav => nav.classList.remove('active'));
            dashboardContents.forEach(content => content.classList.remove('active'));
            this.classList.add('active');
            const targetId = this.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });
});