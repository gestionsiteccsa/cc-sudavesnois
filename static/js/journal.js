(function () {
    "use strict";

    var hiddenByEscape = false;

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && !hiddenByEscape) {
            hiddenByEscape = true;
            document.querySelectorAll(".tooltip").forEach(function (tooltip) {
                tooltip.classList.add("tooltip--hidden");
            });
        }
    });

    document.querySelectorAll(".journal-btn").forEach(function (btn) {
        btn.addEventListener("mouseenter", function () {
            if (hiddenByEscape) {
                hiddenByEscape = false;
                document.querySelectorAll(".tooltip--hidden").forEach(function (tooltip) {
                    tooltip.classList.remove("tooltip--hidden");
                });
            }
        });
        btn.addEventListener("focus", function () {
            if (hiddenByEscape) {
                hiddenByEscape = false;
                document.querySelectorAll(".tooltip--hidden").forEach(function (tooltip) {
                    tooltip.classList.remove("tooltip--hidden");
                });
            }
        });
    });
})();
