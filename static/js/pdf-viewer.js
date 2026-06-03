(function () {
    "use strict";

    var container = document.getElementById("viewer-container");
    if (!container) return;

    var pdfUrl = container.dataset.pdfUrl;
    var pageCount = parseInt(container.dataset.pageCount, 10) || 0;
    var journalTitle = container.dataset.journalTitle;
    var journalNumber = container.dataset.journalNumber;

    var flipbookEl = document.getElementById("flipbook");
    var loadingEl = document.getElementById("viewer-loading");
    var errorEl = document.getElementById("viewer-error");
    var btnPrev = document.getElementById("btn-prev");
    var btnNext = document.getElementById("btn-next");
    var btnFullscreen = document.getElementById("btn-fullscreen");
    var pageCurrentEl = document.getElementById("page-current");
    var pageTotalEl = document.getElementById("page-total");
    var announcer = document.getElementById("viewer-announcer");

    var pageFlip = null;
    var totalPages = 0;
    var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var zoomLevel = 1.0;
    var ZOOM_MIN = 0.5;
    var ZOOM_MAX = 3.0;
    var ZOOM_STEP = 0.25;
    var isMuted = false;

    var btnZoomIn = document.getElementById("btn-zoom-in");
    var btnZoomOut = document.getElementById("btn-zoom-out");
    var btnZoomReset = document.getElementById("btn-zoom-reset");
    var zoomLabel = document.getElementById("zoom-level");
    var btnSound = document.getElementById("btn-sound");
    var iconSoundOn = document.getElementById("icon-sound-on");
    var iconSoundOff = document.getElementById("icon-sound-off");
    var soundSelect = document.getElementById("sound-select");
    var soundType = "paper";

    function waitForLibraries(callback) {
        var attempts = 0;
        var maxAttempts = 50;
        var interval = setInterval(function () {
            attempts++;
            var pdfReady = typeof pdfjsLib !== "undefined";
            var flipReady = typeof window.St !== "undefined" && typeof window.St.PageFlip !== "undefined";

            if (pdfReady && flipReady) {
                clearInterval(interval);
                callback();
            } else if (pdfReady && attempts >= maxAttempts) {
                clearInterval(interval);
                callback();
            } else if (attempts >= maxAttempts) {
                clearInterval(interval);
                showError();
            }
        }, 100);
    }

    function announce(message) {
        if (announcer) {
            announcer.textContent = "";
            setTimeout(function () {
                announcer.textContent = message;
            }, 100);
        }
    }

    function showError() {
        if (loadingEl) loadingEl.hidden = true;
        if (errorEl) errorEl.hidden = false;
    }

    function hideLoading() {
        if (loadingEl) loadingEl.hidden = true;
    }

    function updatePageInfo(currentPage) {
        var displayPage = currentPage + 1;
        if (pageCurrentEl) pageCurrentEl.textContent = displayPage;
        if (btnPrev) btnPrev.disabled = currentPage <= 0;
        if (btnNext) btnNext.disabled = currentPage >= totalPages - 1;
    }

    function goToPage(pageIndex) {
        if (pageFlip && pageIndex >= 0 && pageIndex < totalPages) {
            pageFlip.flip(pageIndex);
        }
    }

    function goNext() {
        if (pageFlip) {
            var current = pageFlip.getCurrentPageIndex();
            if (current < totalPages - 1) {
                pageFlip.flipNext();
            }
        }
    }

    function goPrev() {
        if (pageFlip) {
            var current = pageFlip.getCurrentPageIndex();
            if (current > 0) {
                pageFlip.flipPrev();
            }
        }
    }

    function toggleFullscreen() {
        var section = document.querySelector(".viewer-section");
        if (!section) return;

        if (!document.fullscreenElement) {
            section.requestFullscreen().then(function () {
                if (btnFullscreen) {
                    btnFullscreen.setAttribute("aria-label", "Quitter le mode plein écran");
                    var label = btnFullscreen.querySelector(".viewer-btn-label");
                    if (label) label.textContent = "Quitter";
                }
                announce("Mode plein écran activé");
            }).catch(function () {});
        } else {
            document.exitFullscreen().then(function () {
                if (btnFullscreen) {
                    btnFullscreen.setAttribute("aria-label", "Activer le mode plein écran");
                    var label = btnFullscreen.querySelector(".viewer-btn-label");
                    if (label) label.textContent = "Plein écran";
                }
                announce("Mode plein écran désactivé");
            }).catch(function () {});
        }
    }

    function playPageFlipSound() {
        if (isMuted || prefersReducedMotion) return;
        try {
            var AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) return;
            var audioCtx = new AudioContext();
            var noise = audioCtx.createBufferSource();
            var duration, freq, vol, q;

            switch (soundType) {
                case "book":
                    duration = 0.18;
                    freq = 900;
                    vol = 0.14;
                    q = 0.8;
                    break;
                case "magazine":
                    duration = 0.10;
                    freq = 3200;
                    vol = 0.10;
                    q = 0.3;
                    break;
                default: // paper
                    duration = 0.12;
                    freq = 1800;
                    vol = 0.12;
                    q = 0.5;
            }

            var sampleRate = audioCtx.sampleRate;
            var bufferSize = Math.floor(sampleRate * duration);
            var buffer = audioCtx.createBuffer(1, bufferSize, sampleRate);
            var data = buffer.getChannelData(0);
            for (var i = 0; i < bufferSize; i++) {
                data[i] = Math.random() * 2 - 1;
            }
            noise.buffer = buffer;

            var filter = audioCtx.createBiquadFilter();
            filter.type = "lowpass";
            filter.frequency.value = freq;
            filter.Q.value = q;

            var gain = audioCtx.createGain();
            gain.gain.setValueAtTime(vol, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);

            noise.connect(filter);
            filter.connect(gain);
            gain.connect(audioCtx.destination);
            noise.start();
            noise.stop(audioCtx.currentTime + duration);
        } catch (e) {}
    }

    function applyZoom() {
        var parent = document.querySelector(".stf__parent");
        if (parent) {
            parent.style.transform = "scale(" + zoomLevel + ")";
            parent.style.transformOrigin = "center center";
            parent.style.transition = "transform 0.25s ease";
        }
        if (zoomLabel) {
            zoomLabel.textContent = Math.round(zoomLevel * 100) + " %";
        }
    }

    function zoomIn() {
        if (zoomLevel < ZOOM_MAX) {
            zoomLevel = Math.min(ZOOM_MAX, parseFloat((zoomLevel + ZOOM_STEP).toFixed(2)));
            applyZoom();
        }
    }

    function zoomOut() {
        if (zoomLevel > ZOOM_MIN) {
            zoomLevel = Math.max(ZOOM_MIN, parseFloat((zoomLevel - ZOOM_STEP).toFixed(2)));
            applyZoom();
        }
    }

    function zoomReset() {
        zoomLevel = 1.0;
        applyZoom();
    }

    function toggleSound() {
        isMuted = !isMuted;
        if (btnSound) {
            btnSound.setAttribute("aria-label", isMuted ? "Activer le son" : "Désactiver le son");
            btnSound.setAttribute("aria-pressed", isMuted ? "true" : "false");
            var label = btnSound.querySelector(".viewer-sound-label");
            if (label) label.textContent = isMuted ? "Muet" : "Son";
        }
        if (iconSoundOn) iconSoundOn.hidden = isMuted;
        if (iconSoundOff) iconSoundOff.hidden = !isMuted;
        announce(isMuted ? "Son désactivé" : "Son activé");
    }

    function getViewerDimensions() {
        var vw = window.innerWidth;
        var vh = window.innerHeight;
        var isMobile = vw < 768;
        var renderWidth = isMobile ? 600 : 900;
        var renderHeight = Math.round(renderWidth * 1.414);

        return {
            width: renderWidth,
            height: renderHeight,
            isMobile: isMobile
        };
    }

    function renderPDF(url) {
        if (typeof pdfjsLib === "undefined") {
            showError();
            return;
        }

        pdfjsLib.GlobalWorkerOptions.workerSrc =
            "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

        var loadingTask = pdfjsLib.getDocument(url);
        loadingTask.promise.then(function (pdf) {
            totalPages = pdf.numPages;
            if (pageTotalEl) pageTotalEl.textContent = totalPages;

            var dims = getViewerDimensions();

            var renderPromises = [];
            for (var i = 1; i <= totalPages; i++) {
                renderPromises.push(renderPage(pdf, i, dims));
            }

            Promise.all(renderPromises).then(function (canvases) {
                canvases.forEach(function (canvas) {
                    var pageDiv = document.createElement("div");
                    pageDiv.className = "flipbook-page";
                    pageDiv.appendChild(canvas);
                    flipbookEl.appendChild(pageDiv);
                });

                initFlipbook(dims);
                hideLoading();
                announce(
                    journalTitle + " numéro " + journalNumber +
                    " chargé, " + totalPages + " pages. " +
                    "Utilisez les flèches gauche et droite pour naviguer."
                );
            });
        }).catch(function (err) {
            console.error("Erreur chargement PDF:", err);
            showError();
        });
    }

    function renderPage(pdf, pageNum, dims) {
        return pdf.getPage(pageNum).then(function (page) {
            var viewport = page.getViewport({ scale: 1 });
            var scale = dims.width / viewport.width;
            var scaledViewport = page.getViewport({ scale: scale });

            var canvas = document.createElement("canvas");
            canvas.width = scaledViewport.width;
            canvas.height = scaledViewport.height;
            canvas.setAttribute("role", "img");
            canvas.setAttribute("aria-label", "Page " + pageNum + " du journal");

            var ctx = canvas.getContext("2d", { willReadFrequently: true });
            return page.render({
                canvasContext: ctx,
                viewport: scaledViewport
            }).promise.then(function () {
                return canvas;
            });
        });
    }

    function initFlipbook(dims) {
        var PageFlipClass = window.St && window.St.PageFlip ? window.St.PageFlip : null;

        if (!PageFlipClass) {
            flipbookEl.style.display = "flex";
            flipbookEl.style.flexWrap = "wrap";
            flipbookEl.style.justifyContent = "center";
            flipbookEl.style.gap = "8px";
            flipbookEl.removeAttribute("aria-hidden");

            var pages = flipbookEl.querySelectorAll(".flipbook-page");
            pages.forEach(function (p, i) {
                p.style.width = dims.width + "px";
                p.style.height = dims.height + "px";
                p.setAttribute("role", "img");
                p.setAttribute("aria-label", "Page " + (i + 1));
            });

            updatePageInfo(0);
            if (btnPrev) btnPrev.disabled = true;
            if (btnNext) btnNext.disabled = false;

            var currentIndex = 0;
            if (btnNext) {
                btnNext.addEventListener("click", function () {
                    if (currentIndex < totalPages - 1) {
                        currentIndex++;
                        var pages2 = flipbookEl.querySelectorAll(".flipbook-page");
                        pages2.forEach(function (p, idx) {
                            p.style.display = idx === currentIndex ? "block" : "none";
                        });
                        updatePageInfoSimple(currentIndex);
                        announce("Page " + (currentIndex + 1) + " sur " + totalPages);
                    }
                });
            }
            if (btnPrev) {
                btnPrev.addEventListener("click", function () {
                    if (currentIndex > 0) {
                        currentIndex--;
                        var pages2 = flipbookEl.querySelectorAll(".flipbook-page");
                        pages2.forEach(function (p, idx) {
                            p.style.display = idx === currentIndex ? "block" : "none";
                        });
                        updatePageInfoSimple(currentIndex);
                        announce("Page " + (currentIndex + 1) + " sur " + totalPages);
                    }
                });
            }

            function updatePageInfoSimple(idx) {
                if (pageCurrentEl) pageCurrentEl.textContent = idx + 1;
                if (btnPrev) btnPrev.disabled = idx <= 0;
                if (btnNext) btnNext.disabled = idx >= totalPages - 1;
            }

            hideLoading();
            return;
        }

        var flipConfig = {
            width: 400,
            height: 565,
            size: "stretch",
            minWidth: 200,
            maxWidth: 750,
            minHeight: 280,
            maxHeight: 1100,
            showCover: true,
            mobileScrollSupport: true,
            flippingTime: prefersReducedMotion ? 0 : 800,
            useMouseEvents: true,
            swipeDistance: 30,
            clickEventForward: true,
            usePortrait: dims.isMobile,
            startZIndex: 0,
            autoSize: true,
            maxShadowOpacity: 0.5,
            drawShadow: !prefersReducedMotion
        };

        pageFlip = new PageFlipClass(flipbookEl, flipConfig);

        var pageElements = flipbookEl.querySelectorAll(".flipbook-page");
        pageFlip.loadFromHTML(pageElements);

        pageFlip.on("flip", function (e) {
            var currentPage = e.data;
            updatePageInfo(currentPage);
            playPageFlipSound();
            announce("Page " + (currentPage + 1) + " sur " + totalPages);
        });

        updatePageInfo(0);
    }

    function handleKeyboard(e) {
        var activeEl = document.activeElement;
        var isInFormField = activeEl && ["INPUT", "SELECT", "TEXTAREA"].indexOf(activeEl.tagName) !== -1;

        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case "+":
                case "=":
                    e.preventDefault();
                    zoomIn();
                    return;
                case "-":
                    e.preventDefault();
                    zoomOut();
                    return;
                case "0":
                    e.preventDefault();
                    zoomReset();
                    return;
            }
        }

        if (isInFormField) {
            if (e.key === "Escape") {
                e.preventDefault();
                activeEl.blur();
            }
            return;
        }

        switch (e.key) {
            case "ArrowLeft":
                e.preventDefault();
                goPrev();
                break;
            case "ArrowRight":
                e.preventDefault();
                goNext();
                break;
            case "Home":
                e.preventDefault();
                goToPage(0);
                break;
            case "End":
                e.preventDefault();
                goToPage(totalPages - 1);
                break;
            case "Escape":
                if (document.fullscreenElement) {
                    document.exitFullscreen();
                } else {
                    window.location.href = document.querySelector(".viewer-btn--back").href;
                }
                break;
        }
    }

    function handleResize() {
        if (!pageFlip) return;
        pageFlip.update();
    }

    var resizeTimeout;
    window.addEventListener("resize", function () {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(handleResize, 250);
    });

    document.addEventListener("keydown", handleKeyboard);

    if (btnPrev) btnPrev.addEventListener("click", goPrev);
    if (btnNext) btnNext.addEventListener("click", goNext);
    if (btnFullscreen) btnFullscreen.addEventListener("click", toggleFullscreen);

    document.addEventListener("fullscreenchange", function () {
        if (!document.fullscreenElement && btnFullscreen) {
            btnFullscreen.setAttribute("aria-label", "Activer le mode plein écran");
            var label = btnFullscreen.querySelector(".viewer-btn-label");
            if (label) label.textContent = "Plein écran";
        }
    });

    if (btnZoomIn) btnZoomIn.addEventListener("click", zoomIn);
    if (btnZoomOut) btnZoomOut.addEventListener("click", zoomOut);
    if (btnZoomReset) btnZoomReset.addEventListener("click", zoomReset);
    if (btnSound) btnSound.addEventListener("click", toggleSound);
    if (soundSelect) {
        soundSelect.addEventListener("change", function () {
            soundType = soundSelect.value;
            announce("Son changé : " + soundSelect.options[soundSelect.selectedIndex].text);
        });
    }

    waitForLibraries(function () {
        renderPDF(pdfUrl);
    });
})();
