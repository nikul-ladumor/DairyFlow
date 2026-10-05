// ================================
// CUSTOMER MOBILE SIDEBAR
// ================================

function openCustomerSidebar() {

    const sidebar = document.getElementById("customerSidebar");
    const overlay = document.getElementById("customerSidebarOverlay");

    sidebar.classList.add("show");
    overlay.classList.add("show");
}


function closeCustomerSidebar() {

    const sidebar = document.getElementById("customerSidebar");
    const overlay = document.getElementById("customerSidebarOverlay");

    sidebar.classList.remove("show");
    overlay.classList.remove("show");
}


// ================================
// MENU LINK CLICK
// ================================

document.querySelectorAll(".customer-menu a").forEach(function(link) {

    link.addEventListener("click", function() {

        if (window.innerWidth <= 991) {

            closeCustomerSidebar();

        }

    });

});


// ================================
// WINDOW RESIZE
// ================================

window.addEventListener("resize", function() {

    if (window.innerWidth > 991) {

        closeCustomerSidebar();

    }

});
function toggleSecurityMenu() {

    const submenu = document.getElementById("securitySubmenu");
    const arrow = document.getElementById("securityArrow");

    submenu.classList.toggle("show");
    arrow.classList.toggle("rotate");
}

// Close customer sidebar when page is scrolled
window.addEventListener("scroll", function () {
    if (window.innerWidth <= 991) {
        closeCustomerSidebar();
    }
});