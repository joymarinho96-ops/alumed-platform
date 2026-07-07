document.addEventListener('DOMContentLoaded', function() {
    // Efeito de Stagger nos Cards do Dashboard
    const courseCards = document.querySelectorAll('.course-card-panel');
    courseCards.forEach((card, index) => {
        card.style.setProperty('--delay', `${index * 100}ms`);
        card.classList.add('stagger-in');
    });

    // Efeito de Inclinação 3D nos Cards
    const tiltCards = document.querySelectorAll('.course-card-panel');
    tiltCards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            const rotateX = (y / rect.height) * -10;
            const rotateY = (x / rect.width) * 10;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
        });
    });

    // Carregamento Dinâmico de Aulas
    const mainContent = document.querySelector('.main-content');
    const lessonLinks = document.querySelectorAll('.lesson-item a');

    lessonLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();

            // Destaque da aula ativa
            lessonLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            const url = this.getAttribute('href');
            const type = this.getAttribute('data-type').toLowerCase();

            // Transição de fade
            mainContent.style.opacity = 0;
            setTimeout(() => {
                mainContent.innerHTML = ''; // Limpa o conteúdo principal

                if (type === 'pdf') {
                    const pdfViewer = document.createElement('iframe');
                    pdfViewer.src = url;
                    mainContent.appendChild(pdfViewer);
                } else if (['mp4', 'webm', 'ogg'].includes(type)) {
                    const videoPlayer = document.createElement('video');
                    videoPlayer.src = url;
                    videoPlayer.controls = true;
                    videoPlayer.autoplay = true;
                    mainContent.appendChild(videoPlayer);
                } else {
                    const downloadContainer = document.createElement('div');
                    downloadContainer.className = 'download-container';
                    downloadContainer.innerHTML = `<p>Este archivo no se puede previsualizar.</p><a href="${url}" class="course-card-btn" download>Descargar archivo</a>`;
                    mainContent.appendChild(downloadContainer);
                }
                mainContent.style.opacity = 1;
            }, 300);
        });
    });
});
