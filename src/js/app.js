document.addEventListener("DOMContentLoaded", () => {
  // Intersection Observer for Reveal on Scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll(".fade-in").forEach((el) => observer.observe(el));

  // Analytics Stub for WhatsApp Click
  const waBtns = document.querySelectorAll('a[href*="wa.me"]');
  waBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      console.log("WhatsApp Click Tracked for: " + document.title);
      // Here you would fire GA or Pixel event
    });
  });

  // Smooth Scroll for Anchors
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth" });
      }
    });
  });
});
