// Небольшое клиентское поведение проекта TheaterProps (ПР6).

// Текущий год в подвале страницы: год не прописан в HTML,
// его устанавливает этот скрипт.
const yearElement = document.getElementById("current-year");

if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
}

// Подсветка активного пункта навигации: сравниваем адрес
// текущей страницы со ссылками меню.
const navLinks = document.querySelectorAll(".nav-link");

navLinks.forEach((link) => {
    if (link.getAttribute("href") === window.location.pathname) {
        link.classList.add("active");
    }
});
