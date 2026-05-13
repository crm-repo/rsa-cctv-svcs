const mobileMenuButton = document.getElementById("mobileMenuButton");
const mobileMenu = document.getElementById("mobileMenu");

mobileMenuButton.addEventListener("click", () => {
  mobileMenu.classList.toggle("hidden");
  mobileMenu.classList.toggle("flex");

  if (mobileMenu.classList.contains("hidden")) {
    mobileMenuButton.innerHTML = "☰";
  } else {
    mobileMenuButton.innerHTML = "×";
  }
});

const mobileMenuLinks = mobileMenu.querySelectorAll("a");

mobileMenuLinks.forEach((link) => {
  link.addEventListener("click", () => {
    mobileMenu.classList.add("hidden");
    mobileMenu.classList.remove("flex");
    mobileMenuButton.innerHTML = "☰";
  });
});