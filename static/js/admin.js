// ================================
// ADMIN MOBILE SIDEBAR
// ================================

function openAdminSidebar() {

    document
        .getElementById("adminSidebar")
        .classList.add("show");

    document
        .getElementById("sidebarOverlay")
        .classList.add("show");
}


// ================================
// CLOSE SIDEBAR
// ================================

function closeAdminSidebar() {

    document
        .getElementById("adminSidebar")
        .classList.remove("show");

    document
        .getElementById("sidebarOverlay")
        .classList.remove("show");
}


// ================================
// CLOSE SIDEBAR AFTER MENU CLICK
// ================================

document.querySelectorAll(".sidebar-nav a").forEach(function(link) {

    link.addEventListener("click", function() {

        if (window.innerWidth <= 991) {

            closeAdminSidebar();

        }

    });

});


// ================================
// CLOSE SIDEBAR ON WINDOW RESIZE
// ================================

window.addEventListener("resize", function() {

    if (window.innerWidth > 991) {

        closeAdminSidebar();

    }

});