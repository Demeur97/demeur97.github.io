document.addEventListener('DOMContentLoaded', function() {
    const initData = window.Telegram.WebApp.initData;
    const userID = initData.user.id;
    const userName = initData.user.first_name;

    document.getElementById('user-id').textContent = 'ID: ' + userID;
    document.getElementById('user-name').textContent = 'Имя: ' + userName;

    // Настройка кнопок и их обработчиков
    const buttons = document.querySelectorAll('.button');
    buttons.forEach(function(button, index) {
        button.addEventListener('click', function() {
            // Обработка нажатия на кнопку
            console.log('Кнопка ' + (index + 1) + ' нажата');
        });
    });

    // Инициализация Telegram WebApp
    window.Telegram.WebApp.ready();
});
