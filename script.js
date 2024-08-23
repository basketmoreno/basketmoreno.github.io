// Abrir y cerrar la barra lateral en móviles
document.querySelector('.mobile-menu-icon').addEventListener('click', function() {
    document.querySelector('.mobile-sidebar').style.width = '250px';
});

document.querySelector('.mobile-sidebar .close-btn').addEventListener('click', function() {
    document.querySelector('.mobile-sidebar').style.width = '0';
});
