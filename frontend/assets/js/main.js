const mobileMenuButton = document.getElementById("mobileMenuButton");
const mobileMenu = document.getElementById("mobileMenu");
const mobileMenuOverlay = document.getElementById("mobileMenuOverlay");

mobileMenuButton.addEventListener("click", () => {
  mobileMenu.classList.toggle("hidden");
  mobileMenu.classList.toggle("flex");

  mobileMenuOverlay.classList.toggle("hidden");

  if (mobileMenu.classList.contains("hidden")) {
    mobileMenuButton.innerHTML = "☰";
  } else {
    mobileMenuButton.innerHTML = "×";
  }
});

mobileMenuOverlay.addEventListener("click", () => {
  mobileMenu.classList.add("hidden");
  mobileMenu.classList.remove("flex");

  mobileMenuOverlay.classList.add("hidden");

  mobileMenuButton.innerHTML = "☰";
});

const mobileMenuLinks = mobileMenu.querySelectorAll("a");

mobileMenuLinks.forEach((link) => {
  link.addEventListener("click", () => {
    mobileMenu.classList.add("hidden");
    mobileMenu.classList.remove("flex");

    mobileMenuOverlay.classList.add("hidden");

    mobileMenuButton.innerHTML = "☰";
  });
});