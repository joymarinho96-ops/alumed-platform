// Scroll suave personalizado
document.querySelectorAll("a[href^='#']").forEach(link => {
    link.addEventListener("click", function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute("href"));

        window.scrollTo({
            top: target.offsetTop - 70,
            behavior: "smooth"
        });
    });
});

// Fade-in nas seções
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("fade-visible");
        }
    });
}, { threshold: 0.2 });

document.querySelectorAll(".fade-section").forEach(sec => {
    observer.observe(sec);
});

// Parallax com profundidade
document.addEventListener("mousemove", (e) => {
    document.querySelectorAll(".bg-figure, .bg-figure2, .parallax-mouse").forEach(el => {
        let speed = el.classList.contains('parallax-mouse') ? 0.02 : 0.060;
        let x = (window.innerWidth / 2 - e.pageX) * speed;
        let y = (window.innerHeight / 2 - e.pageY) * speed;

        if (el.classList.contains('parallax-mouse')) {
            el.style.transform = `translate(${x}px, ${y}px)`;
        } else {
            el.style.transform = `translate(${x}px, ${y}px) translateZ(-200px) scale(2)`;
        }
    });
});
/* =======================================
   5) MENU INDICADOR ATIVO
======================================= */

const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-center .nav-link");

const navObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {

            navLinks.forEach(link => link.classList.remove("active"));

            const active = document.querySelector(`.nav-center a[href="#${entry.target.id}"]`);
            if (active) active.classList.add("active");
        }
    });
}, { threshold: 0.5 });

sections.forEach(sec => navObserver.observe(sec));


/* Movimento do texto da HOME seguindo o mouse */
const homeText = document.querySelector(".home-animate");

document.addEventListener("mousemove", (e) => {
    if (!homeText) return;

    const moveX = (e.clientX - window.innerWidth / 2) * 0.01;
    const moveY = (e.clientY - window.innerHeight / 2) * 0.01;

    homeText.style.transform = `translate(${moveX}px, ${moveY}px)`;
});

/* ===========================================================
   1) Scroll suave interno
=========================================================== */
document.querySelectorAll("a[href^='#']").forEach(link => {
    link.addEventListener("click", function (e) {
        const href = this.getAttribute("href");
        if (!href || href === "#") return;

        const target = document.querySelector(href);
        if (!target) return;

        e.preventDefault();
        window.scrollTo({
            top: target.offsetTop - 70,
            behavior: "smooth"
        });
    });
});


/* ===========================================================
   2) Fade simples nas seções (fade-section → fade-visible)
=========================================================== */
const fadeObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("fade-visible");
            fadeObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.20 });

document.querySelectorAll(".fade-section").forEach(sec => {
    fadeObserver.observe(sec);
});


/* ===========================================================
   3) Parallax com profundidade
=========================================================== */
(() => {
    const elements = document.querySelectorAll(".bg-figure, .bg-figure2");
    if (!elements.length) return;

    let mouseX = 0, mouseY = 0;
    let raf = null;

    window.addEventListener("mousemove", e => {
        mouseX = e.clientX;
        mouseY = e.clientY;

        if (!raf) raf = requestAnimationFrame(() => animateParallax());
    });

    function animateParallax() {
        const cx = window.innerWidth / 2;
        const cy = window.innerHeight / 2;

        elements.forEach((el, index) => {
            const speed = 0.02 + index * 0.01;
            const x = (cx - mouseX) * speed;
            const y = (cy - mouseY) * speed;
            el.style.transform = `translate(${x}px, ${y}px)`;
        });

        raf = null;
    }
})();


/* ===========================================================
   4) Menu ativo conforme seção visível
=========================================================== */
(() => {
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll(".nav-center .nav-link");

    if (sections.length === 0) return;

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {

                navLinks.forEach(a => a.classList.remove("active"));

                const link = document.querySelector(`.nav-center a[href="#${entry.target.id}"]`);
                if (link) link.classList.add("active");
            }
        });
    }, { threshold: 0.5 });

    sections.forEach(sec => observer.observe(sec));
})();


/* ===========================================================
   5) Movimento leve do texto da home seguindo o mouse
=========================================================== */
(() => {
    const homeText = document.querySelector(".home-text-container");
    if (!homeText) return;

    let posX = 0, posY = 0, raf = null;

    window.addEventListener("mousemove", e => {
        posX = (e.clientX - window.innerWidth / 2) * 0.01;
        posY = (e.clientY - window.innerHeight / 2) * 0.01;

        if (!raf) raf = requestAnimationFrame(() => moveText());
    });


    function moveText() {
        homeText.style.transform = `translate(${posX}px, ${posY}px)`;
        raf = null;
    }
})();


/* ===========================================================
   6) Scroll Reveal lateral (esquerda / direita aleatório)
=========================================================== */

// elementos que vão receber o efeito
const revealSelectors = `
    h1, h2, h3,
    p, li,
    .section-content,
    .home-title,
    .home-desc
`;

const revealTargets = [...document.querySelectorAll(revealSelectors)];

// adiciona classes reveal + direção aleatória
revealTargets.forEach(el => {
    el.classList.add("reveal");

    if (Math.random() > 0.5) {
        el.classList.add("reveal-left");
    } else {
        el.classList.add("reveal-right");
    }
});

// observer para ativar animação
const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            revealObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.15 });

revealTargets.forEach(el => revealObserver.observe(el));


/* ============================================================
   1) SCROLL REVEAL CINEMÁTICO • APPLE STYLE
============================================================ */

(function() {

    const elements = document.querySelectorAll(".reveal");

    if (elements.length === 0) return;

    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });

    elements.forEach(el => {

        // direção aleatória
        const dir = Math.random() > 0.5 ? "reveal-left" : "reveal-right";
        el.classList.add(dir);

        revealObserver.observe(el);
    });

})();


/* ============================================================
   2) PARALLAX PROFUNDO • 3D REALISTA
============================================================ */

(function() {

    const imgs = document.querySelectorAll(".bg-figure, .bg-figure2");
    if (imgs.length === 0) return;

    let mx = 0, my = 0;
    let rAF = null;

    window.addEventListener("mousemove", (e) => {
        mx = (e.clientX - window.innerWidth / 2);
        my = (e.clientY - window.innerHeight / 2);

        if (!rAF) rAF = requestAnimationFrame(updateParallax);
    });

    function updateParallax() {
        imgs.forEach((el, i) => {
            const depth = 0.015 + (i % 3) * 0.008;  // profundidade diferente
            const x = -mx * depth;
            const y = -my * depth;

            el.style.transform = `translate3d(${x}px, ${y}px, 0) scale(1.5)`;
        });

        rAF = null;
    }

})();


/* ============================================================
   3) SMOOTH SCROLL DOS LINKS
============================================================ */

document.querySelectorAll("a[href^='#']").forEach(link => {
    link.addEventListener("click", function (e) {

        const href = this.getAttribute("href");
        if (!href || href === "#") return;

        const target = document.querySelector(href);
        if (!target) return;

        e.preventDefault();

        window.scrollTo({
            top: target.offsetTop - 70,
            behavior: "smooth"
        });

    });
});


/* ============================================================
   4) MENU ATIVO POR SEÇÃO
============================================================ */

(function() {
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll(".nav-center .nav-link");

    if (sections.length === 0) return;

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {

                navLinks.forEach(a => a.classList.remove("active"));

                const link = document.querySelector(`.nav-center a[href="#${entry.target.id}"]`);
                if (link) link.classList.add("active");
            }
        });
    }, { threshold: 0.5 });

    sections.forEach(sec => observer.observe(sec));
})();

/* ============================================================
   7) EFEITO PARALLAX DO MOUSE NA IMAGEM DE FUNDO DA HOME
============================================================ */

(function() {
    const homeBgImage = document.querySelector(".home-bg-image");
    if (!homeBgImage) return;

    let mouseX = 0;
    let mouseY = 0;
    let rAF = null;

    document.addEventListener("mousemove", (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;

        if (!rAF) {
            rAF = requestAnimationFrame(updateImagePosition);
        }
    });

    function updateImagePosition() {
        const x = (window.innerWidth / 2 - mouseX) * 0.02;
        const y = (window.innerHeight / 2 - mouseY) * 0.02;

        homeBgImage.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`;
        rAF = null;
    }
})();

/* ============================================================
   MODAL DE DETALHES DA CONTA
============================================================ */
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById("account-modal");
    const link = document.getElementById("account-details-link");
    const closeButton = document.querySelector(".close-button");

    if (link) {
        link.onclick = function(e) {
            e.preventDefault();
            modal.style.display = "block";
        }
    }

    if (closeButton) {
        closeButton.onclick = function() {
            modal.style.display = "none";
        }
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
});

/* ============================================================
   ANIMAÇÃO DO MENU DROPDOWN
============================================================ */
document.addEventListener('DOMContentLoaded', function() {
    const userMenu = document.querySelector('.user-menu');
    if (userMenu) {
        const userMenuContent = userMenu.querySelector('.user-menu-content');
        let timeout;

        userMenu.addEventListener('mouseenter', function() {
            clearTimeout(timeout);
            userMenuContent.classList.add('visible');
        });

        userMenu.addEventListener('mouseleave', function() {
            timeout = setTimeout(() => {
                userMenuContent.classList.remove('visible');
            }, 200);
        });
    }
});
