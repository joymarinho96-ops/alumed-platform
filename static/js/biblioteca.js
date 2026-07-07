document.addEventListener("DOMContentLoaded", () => {
    const payloadNode = document.getElementById("library-catalog-data");
    if (!payloadNode) return;

    const payload = JSON.parse(payloadNode.textContent);
    const staticBase = window.ALUMED_LIBRARY_STATIC_BASE || "/static/";
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const dom = {
        page: document.getElementById("alLibraryPage"),
        yearRail: document.getElementById("libraryYearRail"),
        yearSummary: document.getElementById("libraryYearSummary"),
        subjectGrid: document.getElementById("librarySubjectGrid"),
        roomHead: document.getElementById("libraryRoomHead"),
        continueCard: document.getElementById("libraryContinueCard"),
        roomStats: document.getElementById("libraryRoomStats"),
        sectionNav: document.getElementById("librarySectionNav"),
        roomSections: document.getElementById("libraryRoomSections"),
        roomEmpty: document.getElementById("libraryRoomEmpty"),
        inventoryBody: document.getElementById("libraryInventoryBody"),
        searchInput: document.getElementById("librarySearchInput"),
    };

    const years = payload.years || [];
    const rooms = payload.rooms || {};
    const inventory = payload.inventory || [];
    const defaultYear = years.find((year) => year.isDefault) || years[0] || null;

    const state = {
        activeYearId: defaultYear ? defaultYear.id : null,
        activeSubjectId: defaultYear && defaultYear.subjects[0] ? defaultYear.subjects[0].id : null,
        activeSectionId: "apuntes_alumed",
        query: "",
    };

    const revealObserver = !reducedMotion && "IntersectionObserver" in window
        ? new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    entry.target.classList.add("is-visible");
                    revealObserver.unobserve(entry.target);
                });
            },
            { threshold: 0.12 }
        )
        : null;

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function normalize(value) {
        return String(value ?? "").toLowerCase();
    }

    function resolveAsset(url) {
        if (!url) return "";
        if (/^(https?:)?\/\//.test(url) || url.startsWith("/")) return url;
        return `${staticBase}${url}`;
    }

    function getYear(yearId) {
        return years.find((year) => year.id === yearId) || null;
    }

    function getRoom(subjectId) {
        return subjectId ? rooms[subjectId] || null : null;
    }

    function ensureActiveState() {
        const activeYear = getYear(state.activeYearId) || defaultYear;
        if (!activeYear) return;
        state.activeYearId = activeYear.id;

        const subjectIds = activeYear.subjects.map((subject) => subject.id);
        if (!subjectIds.includes(state.activeSubjectId)) {
            state.activeSubjectId = subjectIds[0] || null;
        }
    }

    function matchesQuery(item) {
        if (!state.query) return true;
        const haystack = normalize(
            [
                item.title,
                item.description,
                item.category,
                item.author,
                item.badge,
                item.metaLine,
                item.tags ? item.tags.join(" ") : "",
            ].join(" ")
        );
        return haystack.includes(state.query);
    }

    function iconForGroup(groupId) {
        const group = (payload.rooms[state.activeSubjectId] || { resourceGroups: [] }).resourceGroups || [];
        const match = group.find((entry) => entry.id === groupId);
        return match ? match.icon : "fa-book-medical";
    }

    function iconForItem(item) {
        if (item.groupId === "simulacros_examenes") return "fa-file-signature";
        if (item.groupId === "metodo_profe_joy") return "fa-brain";
        if (item.groupId === "microscopio_virtual") return "fa-microscope";
        if (item.groupId === "flashcards") return "fa-clone";
        if (item.groupId === "podcasts") return "fa-headphones";
        if (item.groupId === "ia_profe_joy") return "fa-robot";

        const room = getRoom(item.subjectKey);
        return room ? room.icon : "fa-book-medical";
    }

    function renderYearTabs() {
        dom.yearRail.innerHTML = years
            .map((year) => {
                const isActive = year.id === state.activeYearId;
                return `
                    <button
                        type="button"
                        class="al-library-year-tab ${isActive ? "is-active" : ""}"
                        data-year-id="${escapeHtml(year.id)}"
                        role="tab"
                        aria-selected="${isActive ? "true" : "false"}"
                    >
                        ${escapeHtml(year.label)}
                        <small>${escapeHtml(year.headline)}</small>
                    </button>
                `;
            })
            .join("");

        dom.yearRail.querySelectorAll("[data-year-id]").forEach((button) => {
            button.addEventListener("click", () => {
                state.activeYearId = button.dataset.yearId;
                state.activeSectionId = "apuntes_alumed";
                ensureActiveState();
                renderAll();
            });
        });
    }

    function renderYearSummary() {
        const activeYear = getYear(state.activeYearId);
        if (!activeYear) {
            dom.yearSummary.innerHTML = "";
            return;
        }

        dom.yearSummary.innerHTML = `
            <div>
                <p class="al-library-eyebrow">Ano seleccionado</p>
                <h3>${escapeHtml(activeYear.label)}</h3>
                <p>${escapeHtml(activeYear.copy)}</p>
            </div>
            <div class="al-library-year-meta">
                <div class="al-library-year-stat">
                    <span>Materias</span>
                    <strong>${activeYear.subjects.length}</strong>
                </div>
                <div class="al-library-year-stat">
                    <span>Recursos</span>
                    <strong>${activeYear.resourceCount}</strong>
                </div>
                <div class="al-library-year-stat">
                    <span>Disponibles</span>
                    <strong>${activeYear.availableCount}</strong>
                </div>
            </div>
        `;
    }

    function renderSubjectGrid() {
        const activeYear = getYear(state.activeYearId);
        if (!activeYear || !activeYear.subjects.length) {
            dom.subjectGrid.innerHTML = `
                <article class="al-library-empty-card">
                    <div>
                        <i class="fas fa-layer-group"></i>
                        <h4>Arquitectura preparada para este ano</h4>
                        <p>
                            Este nivel ya esta contemplado en la Biblioteca ALUMED. Cuando lleguen nuevos recursos,
                            la estructura de materias podra activarse sin rehacer la interfaz.
                        </p>
                    </div>
                    <span class="al-library-action-disabled">Proximamente</span>
                </article>
            `;
            return;
        }

        dom.subjectGrid.innerHTML = activeYear.subjects
            .map((subject) => {
                const isActive = subject.id === state.activeSubjectId;
                return `
                    <button
                        type="button"
                        class="al-library-subject-card js-hover-card ${isActive ? "is-active" : ""}"
                        data-subject-id="${escapeHtml(subject.id)}"
                    >
                        <div class="al-library-subject-card-head">
                            <div class="al-library-subject-icon">
                                <i class="fas ${escapeHtml(subject.icon)}"></i>
                            </div>
                            <span class="al-library-subject-badge">${escapeHtml(subject.badge)}</span>
                        </div>
                        <h3>${escapeHtml(subject.label)}</h3>
                        <p>${escapeHtml(subject.description)}</p>
                        <div class="al-library-subject-meta">
                            <span class="al-library-subject-pill">${subject.resourceCount} recursos</span>
                            <span class="al-library-subject-pill">${subject.officialCount} ALUMED</span>
                            <span class="al-library-subject-pill">${subject.availableCount} listos</span>
                        </div>
                    </button>
                `;
            })
            .join("");

        dom.subjectGrid.querySelectorAll("[data-subject-id]").forEach((button) => {
            button.addEventListener("click", () => {
                state.activeSubjectId = button.dataset.subjectId;
                state.activeSectionId = "apuntes_alumed";
                renderAll();
            });
        });
    }

    function renderRoomHead(room) {
        dom.roomHead.innerHTML = `
            <div class="al-library-room-head">
                <div>
                    <div class="al-library-breadcrumb">
                        <span>${escapeHtml(payload.career.label)}</span>
                        <i class="fas fa-chevron-right"></i>
                        <span>${escapeHtml(room.yearLabel)}</span>
                        <i class="fas fa-chevron-right"></i>
                        <span>${escapeHtml(room.label)}</span>
                    </div>
                    <h2 class="al-library-room-title">${escapeHtml(room.label)}</h2>
                    <p class="al-library-room-copy">${escapeHtml(room.description)}</p>
                </div>
                <div class="al-library-room-tags">
                    <span class="al-library-room-tag">${escapeHtml(room.focus)}</span>
                    <span class="al-library-room-tag">${room.stats.total} recursos</span>
                    <span class="al-library-room-tag">${room.stats.official} ALUMED</span>
                </div>
            </div>
        `;
    }

    function renderContinueCard(room) {
        const card = room.continueCard;
        const action = card.url
            ? `<a class="al-library-action" href="${escapeHtml(card.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(card.actionLabel)}</a>`
            : `<span class="al-library-action-disabled">${escapeHtml(card.actionLabel)}</span>`;

        dom.continueCard.innerHTML = `
            <article class="al-library-continue-card js-hover-card">
                <div class="al-library-continue-copy">
                    <p class="al-library-section-eyebrow">${escapeHtml(card.eyebrow)}</p>
                    <h3>${escapeHtml(card.title)}</h3>
                    <p>${escapeHtml(card.description)}</p>
                    <div class="al-library-continue-meta">
                        <span class="al-library-room-tag">${escapeHtml(card.badge)}</span>
                        <span class="al-library-room-tag">${escapeHtml(card.meta)}</span>
                    </div>
                </div>
                <div class="al-library-continue-actions">
                    <span class="al-library-status-pill" data-tone="${escapeHtml(card.statusTone)}">${escapeHtml(card.statusLabel)}</span>
                    ${action}
                </div>
            </article>
        `;
    }

    function renderRoomStats(room) {
        dom.roomStats.innerHTML = `
            <div class="al-library-stat">
                <span>Recursos visibles</span>
                <strong>${room.stats.total}</strong>
            </div>
            <div class="al-library-stat">
                <span>Links listos</span>
                <strong>${room.stats.available}</strong>
            </div>
            <div class="al-library-stat">
                <span>Material ALUMED</span>
                <strong>${room.stats.official}</strong>
            </div>
            <div class="al-library-stat">
                <span>Pendientes</span>
                <strong>${room.stats.pending}</strong>
            </div>
        `;
    }

    function renderSectionNav(room) {
        dom.sectionNav.innerHTML = room.resourceGroups
            .map((group) => `
                <button
                    type="button"
                    class="al-library-section-jump ${group.id === state.activeSectionId ? "is-active" : ""}"
                    data-section-jump="${escapeHtml(group.id)}"
                >
                    ${escapeHtml(group.label)}
                    <small>${group.counts.total} recursos</small>
                </button>
            `)
            .join("");

        dom.sectionNav.querySelectorAll("[data-section-jump]").forEach((button) => {
            button.addEventListener("click", () => {
                state.activeSectionId = button.dataset.sectionJump;
                const target = document.getElementById(`section-${button.dataset.sectionJump}`);
                if (target) {
                    target.scrollIntoView({
                        behavior: reducedMotion ? "auto" : "smooth",
                        block: "start",
                    });
                }
                renderSectionNav(room);
            });
        });
    }

    function renderResourceCard(item) {
        const cover = resolveAsset(item.cover);
        const action = item.primaryUrl
            ? `<a class="al-library-action" href="${escapeHtml(item.primaryUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.actionLabel)}</a>`
            : `<span class="al-library-action-disabled">${escapeHtml(item.actionLabel)}</span>`;
        const metaPills = [
            item.type || "Recurso",
            item.category || "General",
            item.pages ? `${item.pages} pags.` : item.metaLine,
        ]
            .filter(Boolean)
            .slice(0, 3)
            .map((value) => `<span>${escapeHtml(value)}</span>`)
            .join("");
        const infoPills = [
            item.author,
            item.yearLabel,
            item.origin === "inventory" ? "Migracion por validar" : "Ruta nativa ALUMED",
        ]
            .filter(Boolean)
            .map((value) => `<span class="al-library-resource-pill">${escapeHtml(value)}</span>`)
            .join("");

        return `
            <article class="al-library-resource-card js-hover-card al-reveal">
                <div class="al-library-resource-media">
                    <span class="al-library-resource-badge">${escapeHtml(item.badge)}</span>
                    ${cover ? `<img src="${escapeHtml(cover)}" alt="${escapeHtml(item.title)}" loading="lazy">` : ""}
                    <div class="al-library-resource-fallback">
                        <i class="fas ${escapeHtml(iconForItem(item))}"></i>
                        <small>${escapeHtml(item.category || item.type || "Recurso")}</small>
                        <strong>${escapeHtml(item.title)}</strong>
                    </div>
                </div>
                <div class="al-library-resource-body">
                    <div>
                        <div class="al-library-card-meta">${metaPills}</div>
                        <h4>${escapeHtml(item.title)}</h4>
                        <p>${escapeHtml(item.description)}</p>
                        <div class="al-library-resource-info">${infoPills}</div>
                    </div>
                    <div class="al-library-card-footer">
                        <span class="al-library-status-pill" data-tone="${escapeHtml(item.statusTone)}">${escapeHtml(item.statusLabel)}</span>
                        ${action}
                    </div>
                </div>
            </article>
        `;
    }

    function renderEmptyCard(group) {
        return `
            <article class="al-library-empty-card">
                <div>
                    <i class="fas ${escapeHtml(group.icon)}"></i>
                    <h4>${escapeHtml(group.emptyState.title)}</h4>
                    <p>${escapeHtml(group.emptyState.copy)}</p>
                </div>
                <div class="al-library-card-footer">
                    <span class="al-library-status-pill" data-tone="muted">${escapeHtml(group.emptyState.badge)}</span>
                    <span class="al-library-action-disabled">Proximamente</span>
                </div>
            </article>
        `;
    }

    function renderRoomSections(room) {
        const renderedSections = room.resourceGroups
            .map((group) => {
                const filteredItems = group.items.filter(matchesQuery);
                const countTotal = filteredItems.length;
                const countAvailable = filteredItems.filter((item) => item.isAvailable).length;
                const countOfficial = filteredItems.filter((item) => item.isOfficial).length;
                const cards = filteredItems.length
                    ? filteredItems.map(renderResourceCard).join("")
                    : renderEmptyCard(group);

                return `
                    <article class="al-library-section al-reveal" id="section-${escapeHtml(group.id)}">
                        <div class="al-library-section-head">
                            <div>
                                <p class="al-library-section-eyebrow">${escapeHtml(room.label)}</p>
                                <h3>${escapeHtml(group.label)}</h3>
                                <p>${escapeHtml(group.description)}</p>
                            </div>
                            <div class="al-library-section-counts">
                                <span class="al-library-room-tag">${countTotal} visibles</span>
                                <span class="al-library-room-tag">${countAvailable} listos</span>
                                <span class="al-library-room-tag">${countOfficial} ALUMED</span>
                            </div>
                        </div>
                        <div class="al-library-section-grid">
                            ${cards}
                        </div>
                    </article>
                `;
            })
            .join("");

        dom.roomSections.innerHTML = renderedSections;

        const visibleItems = room.resourceGroups.some((group) => group.items.filter(matchesQuery).length > 0);
        dom.roomEmpty.hidden = visibleItems;
        if (!visibleItems) {
            dom.roomSections.innerHTML = "";
        }
    }

    function renderInventory(room) {
        const roomInventory = inventory.filter((entry) => {
            if (entry.subjectKey !== room.id) return false;
            if (!state.query) return true;
            const haystack = normalize(
                [
                    entry.folder,
                    entry.subfolder,
                    entry.title,
                    entry.description,
                    entry.statusLabel,
                ].join(" ")
            );
            return haystack.includes(state.query);
        });

        if (!roomInventory.length) {
            dom.inventoryBody.innerHTML = `
                <tr>
                    <td colspan="8">
                        <span class="al-library-inline-status" data-tone="muted">Sin inventario visible para esta materia</span>
                    </td>
                </tr>
            `;
            return;
        }

        dom.inventoryBody.innerHTML = roomInventory
            .map((entry) => {
                const source = entry.sourceUrl
                    ? `<a class="al-library-table-link" href="${escapeHtml(entry.sourceUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(entry.sourceUrl)}</a>`
                    : "<small>Sin enlace cargado</small>";

                return `
                    <tr>
                        <td>${escapeHtml(entry.folder)}</td>
                        <td>${escapeHtml(entry.subfolder)}</td>
                        <td>
                            <strong>${escapeHtml(entry.title)}</strong><br>
                            <small>${escapeHtml(entry.description)}</small>
                        </td>
                        <td>${escapeHtml(entry.fileType || "PDF")}</td>
                        <td>${source}</td>
                        <td>${entry.views ?? "-"}</td>
                        <td>${escapeHtml(entry.updatedAt || "Sin fecha")}</td>
                        <td>
                            <span class="al-library-inline-status" data-tone="${escapeHtml(entry.statusTone)}">${escapeHtml(entry.statusLabel)}</span>
                        </td>
                    </tr>
                `;
            })
            .join("");
    }

    function renderYearPlaceholder(year) {
        dom.roomHead.innerHTML = `
            <div class="al-library-room-head">
                <div>
                    <div class="al-library-breadcrumb">
                        <span>${escapeHtml(payload.career.label)}</span>
                        <i class="fas fa-chevron-right"></i>
                        <span>${escapeHtml(year.label)}</span>
                    </div>
                    <h2 class="al-library-room-title">${escapeHtml(year.label)}</h2>
                    <p class="al-library-room-copy">${escapeHtml(year.copy)}</p>
                </div>
            </div>
        `;
        dom.continueCard.innerHTML = "";
        dom.roomStats.innerHTML = "";
        dom.sectionNav.innerHTML = "";
        dom.roomSections.innerHTML = `
            <article class="al-library-empty-card">
                <div>
                    <i class="fas fa-layer-group"></i>
                    <h4>Este nivel ya esta contemplado</h4>
                    <p>
                        La Biblioteca ALUMED deja preparada la arquitectura para futuras materias, dashboards,
                        recomendaciones y modulos clinicos sin volver a empezar desde cero.
                    </p>
                </div>
                <span class="al-library-action-disabled">Proximamente</span>
            </article>
        `;
        dom.roomEmpty.hidden = true;
        dom.inventoryBody.innerHTML = `
            <tr>
                <td colspan="8">
                    <span class="al-library-inline-status" data-tone="muted">Sin inventario asignado a este ano todavia</span>
                </td>
            </tr>
        `;
    }

    function renderRoom() {
        const activeYear = getYear(state.activeYearId);
        const room = getRoom(state.activeSubjectId);

        if (!activeYear) return;
        if (!room) {
            renderYearPlaceholder(activeYear);
            return;
        }

        renderRoomHead(room);
        renderContinueCard(room);
        renderRoomStats(room);
        renderSectionNav(room);
        renderRoomSections(room);
        renderInventory(room);
    }

    function bindSearch() {
        if (!dom.searchInput) return;
        dom.searchInput.addEventListener("input", (event) => {
            state.query = normalize(event.target.value.trim());
            renderRoom();
        });
    }

    function applyHoverCards(nodes) {
        if (reducedMotion) return;

        nodes.forEach((node) => {
            if (node.dataset.hoverBound === "true") return;
            node.dataset.hoverBound = "true";

            node.addEventListener("pointermove", (event) => {
                const rect = node.getBoundingClientRect();
                const x = event.clientX - rect.left;
                const y = event.clientY - rect.top;
                const rotateY = ((x / rect.width) - 0.5) * 7;
                const rotateX = ((y / rect.height) - 0.5) * -7;

                node.style.setProperty("--card-rotate-x", `${rotateX.toFixed(2)}deg`);
                node.style.setProperty("--card-rotate-y", `${rotateY.toFixed(2)}deg`);
                node.style.setProperty("--spot-x", `${x}px`);
                node.style.setProperty("--spot-y", `${y}px`);
            });

            node.addEventListener("pointerleave", () => {
                node.style.setProperty("--card-rotate-x", "0deg");
                node.style.setProperty("--card-rotate-y", "0deg");
                node.style.setProperty("--spot-x", "50%");
                node.style.setProperty("--spot-y", "50%");
            });

            node.addEventListener("pointerdown", () => {
                node.style.setProperty("--card-scale", "0.992");
            });

            node.addEventListener("pointerup", () => {
                node.style.setProperty("--card-scale", "1");
            });
        });
    }

    function observeReveals(scope = document) {
        const nodes = scope.querySelectorAll(".al-reveal");
        if (!revealObserver) {
            nodes.forEach((node) => node.classList.add("is-visible"));
            return;
        }
        nodes.forEach((node) => {
            if (node.dataset.revealBound === "true") return;
            node.dataset.revealBound = "true";
            revealObserver.observe(node);
        });
    }

    function animateCounters() {
        const counters = Array.from(document.querySelectorAll("[data-count-target]"));
        if (!counters.length) return;

        const runCounter = (counter) => {
            if (counter.dataset.animated === "true") return;
            counter.dataset.animated = "true";

            const target = Number(counter.dataset.countTarget || counter.textContent || "0");
            if (reducedMotion || Number.isNaN(target)) {
                counter.textContent = String(target);
                return;
            }

            counter.textContent = "0";
            const duration = 1200;
            const start = performance.now();

            const tick = (now) => {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3);
                counter.textContent = String(Math.round(target * eased));
                if (progress < 1) requestAnimationFrame(tick);
            };

            requestAnimationFrame(tick);
        };

        if (!("IntersectionObserver" in window) || reducedMotion) {
            counters.forEach(runCounter);
            return;
        }

        const counterObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (!entry.isIntersecting) return;
                    runCounter(entry.target);
                    counterObserver.unobserve(entry.target);
                });
            },
            { threshold: 0.35 }
        );

        counters.forEach((counter) => counterObserver.observe(counter));
    }

    function setupParallax() {
        if (reducedMotion || !dom.page || !window.matchMedia("(hover: hover)").matches) return;

        const nodes = Array.from(document.querySelectorAll(".js-parallax"));
        if (!nodes.length) return;

        let rafId = 0;
        let mouseX = 0;
        let mouseY = 0;

        const update = () => {
            nodes.forEach((node) => {
                const speed = Number(node.dataset.parallaxSpeed || 10);
                const offsetX = mouseX * (speed / 120);
                const offsetY = mouseY * (speed / 160);
                node.style.transform = `translate3d(${offsetX.toFixed(2)}px, ${offsetY.toFixed(2)}px, 0)`;
            });
            rafId = 0;
        };

        dom.page.addEventListener("pointermove", (event) => {
            const rect = dom.page.getBoundingClientRect();
            mouseX = ((event.clientX - rect.left) / rect.width - 0.5) * 12;
            mouseY = ((event.clientY - rect.top) / rect.height - 0.5) * 12;
            if (!rafId) rafId = requestAnimationFrame(update);
        });

        dom.page.addEventListener("pointerleave", () => {
            mouseX = 0;
            mouseY = 0;
            if (!rafId) {
                rafId = requestAnimationFrame(update);
            }
        });
    }

    function refreshInteractions() {
        applyHoverCards(document.querySelectorAll(".js-hover-card"));
        observeReveals(document);
    }

    function renderAll() {
        ensureActiveState();
        renderYearTabs();
        renderYearSummary();
        renderSubjectGrid();
        renderRoom();
        refreshInteractions();
    }

    bindSearch();
    renderAll();
    animateCounters();
    setupParallax();
});
