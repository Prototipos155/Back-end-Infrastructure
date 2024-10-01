const nav = document.querySelector(".nav"),
  searchIcon = document.querySelector("#searchIcon"),
  navOpenBtn = document.querySelector(".navOpenBtn"),
  navCloseBtn = document.querySelector(".navCloseBtn");
<<<<<<< HEAD
searchIcon.addEventListener("click", () => {
  nav.classList.toggle("openSearch");
  nav.classList.remove("openNav");
  if (nav.classList.contains("openSearch")) {
    return searchIcon.classList.replace("bx-search", "bx-chevron-left");
=======
  searchIcon.addEventListener("click", () => {
    nav.classList.toggle("openSearch");
    nav.classList.remove("openNav");
    if (nav.classList.contains("openSearch")) {
      return searchIcon.classList.replace("bx-search", "bx-chevron-left");
>>>>>>> 6e587cac256e69ce4344690ab43e1efcf57e77e9
  }
  searchIcon.classList.replace("bx-chevron-left", "bx-search");
});
navOpenBtn.addEventListener("click", () => {
  nav.classList.add("openNav");
  nav.classList.remove("openSearch");
  searchIcon.classList.replace("bx-chevron-left", "bx-search");
});
navCloseBtn.addEventListener("click", () => {
  nav.classList.remove("openNav");
});