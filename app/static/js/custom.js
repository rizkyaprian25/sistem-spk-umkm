document.addEventListener('DOMContentLoaded', function () {
    // === 1. Label Dinamis File Upload (Bootstrap Custom File Input) ===
    if (typeof $ !== 'undefined') {
        $('.custom-file-input').on('change', function () {
            const fileNames = Array.from(this.files).map(file => file.name).join(', ') || 'Pilih file...';
            $(this).next('.custom-file-label').text(fileNames);
        });
    } else {
        console.warn('jQuery belum dimuat. Label file upload mungkin tidak berfungsi.');
    }

    // === 2. Footer Transparan saat Scroll ===
    const footer = document.querySelector('.footer');
    if (footer) {
        const scrollThresholdFooter = 50;
        window.addEventListener('scroll', () => {
            footer.classList.toggle('footer-scrolled', window.scrollY > scrollThresholdFooter);
        });
    }

    // === 3. Tombol Scroll to Top ===
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (scrollToTopBtn) {
        const scrollThresholdBtn = 200;
        window.addEventListener('scroll', () => {
            scrollToTopBtn.classList.toggle('show', window.scrollY > scrollThresholdBtn);
        });
        scrollToTopBtn.addEventListener('click', function (e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // === 4. Animasi Elemen Masuk Viewport (IntersectionObserver) ===
    const animatedElements = document.querySelectorAll('.animated-card');
    if (animatedElements.length > 0) {
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries, obs) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        obs.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.1 });
            animatedElements.forEach(el => observer.observe(el));
        } else {
            animatedElements.forEach(el => el.classList.add('is-visible'));
        }
    }
});
