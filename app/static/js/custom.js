document.addEventListener('DOMContentLoaded', function() {

    // 1. Script untuk menangani label file input Bootstrap
    // Membutuhkan jQuery untuk dimuat sebelum skrip ini jika menggunakan '$'
    if (typeof $ !== 'undefined') { // Cek apakah jQuery sudah dimuat
        $('.custom-file-input').on('change', function(event) {
            var inputFile = event.target;
            if (inputFile.files.length > 0) { // Pastikan ada file yang dipilih
                var fileName = inputFile.files[0].name;
                $(inputFile).next('.custom-file-label').html(fileName);
            } else {
                // Reset label jika tidak ada file dipilih atau pilihan dibatalkan
                $(inputFile).next('.custom-file-label').html('Pilih file...');
            }
        });
    } else {
        console.warn('jQuery not loaded, Bootstrap file input label script might not work as expected if an error occurs elsewhere.');
    }

    // 2. Script untuk footer transparan
    const footer = document.querySelector('.footer');
    if (footer) { // Pastikan elemen footer ada
        const scrollThresholdFooter = 50; // Jarak scroll (dalam pixel) sebelum footer menjadi transparan

        window.addEventListener('scroll', function() {
            if (window.scrollY > scrollThresholdFooter) {
                footer.classList.add('footer-scrolled');
            } else {
                footer.classList.remove('footer-scrolled');
            }
        });
    } else {
        // console.warn('Footer element not found for transparent scroll effect.');
    }

    // 3. Script untuk tombol Scroll to Top
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (scrollToTopBtn) { // Pastikan elemen tombol ada
        const scrollThresholdBtn = 200; // Jarak scroll sebelum tombol muncul

        window.addEventListener('scroll', function() {
            if (window.scrollY > scrollThresholdBtn) {
                scrollToTopBtn.classList.add('show');
            } else {
                scrollToTopBtn.classList.remove('show');
            }
        });

        scrollToTopBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Mencegah perilaku default link #
            window.scrollTo({
                top: 0,
                behavior: 'smooth' // Efek scroll halus
            });
        });
    } else {
        // console.warn('Scroll to top button element not found.');
    }

    // 4. Script untuk Animasi Sederhana pada Elemen (Intersection Observer)
    const animatedElements = document.querySelectorAll('.animated-card'); // Atau kelas lain yang ingin dianimasi
    if (animatedElements.length > 0) {
        if ("IntersectionObserver" in window) {
            let observer = new IntersectionObserver((entries, observerInstance) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observerInstance.unobserve(entry.target); // Agar animasi hanya dijalankan sekali per elemen
                    }
                });
            }, { threshold: 0.1 }); // Muncul saat 10% elemen terlihat di viewport

            animatedElements.forEach(el => {
                observer.observe(el);
            });
        } else {
            // Fallback untuk browser lama yang tidak mendukung IntersectionObserver:
            // Langsung tampilkan semua elemen tanpa animasi scroll
            animatedElements.forEach(el => {
                el.classList.add('is-visible');
            });
            // console.warn('IntersectionObserver not supported, animations on scroll might not work as expected.');
        }
    }

});