document.addEventListener('DOMContentLoaded', function() {
    const contenidoTrigger = document.getElementById('contenido-trigger');
    const simuladosTrigger = document.getElementById('simulados-trigger');
    const modulesContainer = document.getElementById('modules-regular');
    const simuladosContainer = document.getElementById('modules-simulados');
    const sidebarNav = document.querySelector('.sidebar-nav');
    const moduleHeaders = document.querySelectorAll('.module-header');

    function setupAccordion(trigger, container) {
        if (trigger) {
            trigger.addEventListener('click', function() {
                this.classList.toggle('open');
                container.classList.toggle('open');
                
                if (container.classList.contains('open')) {
                    const navHeight = sidebarNav.offsetHeight;
                    const triggerHeight = trigger.offsetHeight;
                    const otherTriggerHeight = (trigger === contenidoTrigger ? simuladosTrigger.offsetHeight : contenidoTrigger.offsetHeight);
                    const availableHeight = navHeight - triggerHeight - otherTriggerHeight - 100;
                    container.style.maxHeight = availableHeight + 'px';
                } else {
                    container.style.maxHeight = '0px';
                }
            });
        }
    }

    setupAccordion(contenidoTrigger, modulesContainer);
    setupAccordion(simuladosTrigger, simuladosContainer);

    window.addEventListener('resize', () => {
        // Recalculate heights on resize if needed
        if(modulesContainer.classList.contains('open')) {
            const navHeight = sidebarNav.offsetHeight;
            const triggerHeight = contenidoTrigger.offsetHeight;
            const otherTriggerHeight = simuladosTrigger.offsetHeight;
            const availableHeight = navHeight - triggerHeight - otherTriggerHeight - 100;
            modulesContainer.style.maxHeight = availableHeight + 'px';
        }
        if(simuladosContainer.classList.contains('open')) {
            const navHeight = sidebarNav.offsetHeight;
            const triggerHeight = simuladosTrigger.offsetHeight;
            const otherTriggerHeight = contenidoTrigger.offsetHeight;
            const availableHeight = navHeight - triggerHeight - otherTriggerHeight - 100;
            simuladosContainer.style.maxHeight = availableHeight + 'px';
        }
    });

    moduleHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const moduleItem = this.parentElement;
            const wasActive = moduleItem.classList.contains('active');
            
            moduleHeaders.forEach(h => {
                if (h !== this) {
                    h.parentElement.classList.remove('active');
                    h.nextElementSibling.style.maxHeight = null;
                }
            });

            if (!wasActive) {
                moduleItem.classList.add('active');
                const lessonList = this.nextElementSibling;
                lessonList.style.maxHeight = lessonList.scrollHeight + "px";
            } else {
                moduleItem.classList.remove('active');
                this.nextElementSibling.style.maxHeight = null;
            }
        });
    });

    const navItems = document.querySelectorAll('.sidebar-nav .nav-item:not(.has-submenu)');
    const contentSections = document.querySelectorAll('.dashboard-content');
    const lessonLinks = document.querySelectorAll('.lesson-link');
    const contentViewer = document.getElementById('content-viewer');
    const lessonToolbar = document.getElementById('lesson-toolbar');
    const currentLessonTitle = document.getElementById('current-lesson-title');
    const downloadBtn = document.getElementById('download-btn');
    const pdfControls = document.getElementById('pdf-controls');
    const pdfViewerContainer = document.getElementById('pdf-viewer-container');
    const initialMessage = document.getElementById('initial-message');

    navItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.dataset.target;
            navItems.forEach(nav => nav.classList.remove('active'));
            this.classList.add('active');
            contentSections.forEach(section => section.classList.remove('active'));
            document.getElementById(targetId).classList.add('active');
        });
    });

    let pdfDoc = null,
        pageNum = 1,
        pageRendering = false,
        pageNumPending = null,
        scale = 1.5;

    const canvas = document.getElementById('pdf-canvas'),
          ctx = canvas.getContext('2d');

    function renderPage(num) {
        pageRendering = true;
        pdfDoc.getPage(num).then(function(page) {
            const viewport = page.getViewport({scale: scale});
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            const renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };
            const renderTask = page.render(renderContext);

            renderTask.promise.then(function() {
                pageRendering = false;
                if (pageNumPending !== null) {
                    renderPage(pageNumPending);
                    pageNumPending = null;
                }
            });
        });
        document.getElementById('page-num').textContent = num;
    }

    function queueRenderPage(num) {
        if (pageRendering) {
            pageNumPending = num;
        } else {
            renderPage(num);
        }
    }

    document.getElementById('prev-page').addEventListener('click', function() {
        if (pageNum <= 1) return;
        pageNum--;
        queueRenderPage(pageNum);
    });

    document.getElementById('next-page').addEventListener('click', function() {
        if (pageNum >= pdfDoc.numPages) return;
        pageNum++;
        queueRenderPage(pageNum);
    });

    document.getElementById('zoom-in').addEventListener('click', function() {
        scale += 0.2;
        renderPage(pageNum);
    });

    document.getElementById('zoom-out').addEventListener('click', function() {
        if (scale <= 0.8) return;
        scale -= 0.2;
        renderPage(pageNum);
    });

    lessonLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            navItems.forEach(nav => nav.classList.remove('active'));
            contentSections.forEach(section => section.classList.remove('active'));
            document.getElementById('course-content-area').classList.add('active');
            
            lessonLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');

            const lessonType = this.dataset.lessonType;
            const fileUrl = this.dataset.fileUrl;
            const videoUrl = this.dataset.videoUrl;
            const lessonTitle = this.dataset.title;

            lessonToolbar.style.display = 'flex';
            currentLessonTitle.textContent = lessonTitle;
            contentViewer.innerHTML = ''; // Clear previous content
            initialMessage.style.display = 'none';
            pdfViewerContainer.style.display = 'none';
            pdfControls.style.display = 'none';
            downloadBtn.style.display = 'none';

            if (lessonType === 'pdf') {
                pdfViewerContainer.style.display = 'block';
                pdfControls.style.display = 'flex';
                downloadBtn.href = fileUrl;
                downloadBtn.style.display = 'inline-flex';

                pdfjsLib.getDocument(fileUrl).promise.then(function(pdfDoc_) {
                    pdfDoc = pdfDoc_;
                    document.getElementById('page-count').textContent = pdfDoc.numPages;
                    pageNum = 1;
                    renderPage(pageNum);
                });

            } else if (lessonType === 'video') {
                const videoPlayer = document.createElement('video');
                videoPlayer.src = videoUrl || fileUrl;
                videoPlayer.controls = true;
                videoPlayer.setAttribute('controlsList', 'nodownload');
                videoPlayer.oncontextmenu = () => false;
                contentViewer.appendChild(videoPlayer);
                downloadBtn.style.display = 'none';

            } else {
                // Handle other file types or show a generic message
                contentViewer.innerHTML = `<div style="text-align:center; color: #fff; padding: 50px;"><p>Contenido no soportado para visualización directa.</p></div>`;
                if(fileUrl) {
                    downloadBtn.href = fileUrl;
                    downloadBtn.style.display = 'inline-flex';
                }
            }
        });
    });
});
