// DOM Elements
const header = document.querySelector('header');
const navLinks = document.querySelector('.nav-links');
const hamburger = document.querySelector('.hamburger');
const navLinksItems = document.querySelectorAll('.nav-links li');
const themeToggle = document.querySelector('.theme-toggle');
const moonIcon = document.querySelector('.fa-moon');
const sunIcon = document.querySelector('.fa-sun');
const contactForm = document.getElementById('contact-form');

// Header scroll effect
if (header) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('header-scroll');
        } else {
            header.classList.remove('header-scroll');
        }
    });
}

// Mobile Navigation
if (hamburger && navLinks) {
    const setNavigationOpen = (isOpen) => {
        navLinks.classList.toggle('nav-active', isOpen);
        hamburger.classList.toggle('active', isOpen);
        hamburger.setAttribute('aria-expanded', String(isOpen));
        hamburger.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
        document.body.classList.toggle('no-scroll', isOpen);
    };

    hamburger.addEventListener('click', () => {
        setNavigationOpen(!navLinks.classList.contains('nav-active'));
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && navLinks.classList.contains('nav-active')) {
            setNavigationOpen(false);
            hamburger.focus();
        }
    });
}

// Close mobile menu when clicking on a link
navLinksItems.forEach(item => {
    item.addEventListener('click', () => {
        if (navLinks && navLinks.classList.contains('nav-active')) {
            navLinks.classList.remove('nav-active');
            if (hamburger) {
                hamburger.classList.remove('active');
                hamburger.setAttribute('aria-expanded', 'false');
                hamburger.setAttribute('aria-label', 'Open navigation');
            }
            document.body.classList.remove('no-scroll');
        }
    });
});

// Theme toggle functionality
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');

        if (document.body.classList.contains('light-theme')) {
            if (moonIcon) moonIcon.style.display = 'none';
            if (sunIcon) sunIcon.style.display = 'block';
        } else {
            if (moonIcon) moonIcon.style.display = 'block';
            if (sunIcon) sunIcon.style.display = 'none';
        }

        const theme = document.body.classList.contains('light-theme') ? 'light' : 'dark';
        localStorage.setItem('theme', theme);
    });
}

// Load saved theme preference
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');

    if (savedTheme === 'light') {
        document.body.classList.add('light-theme');
        if (moonIcon) moonIcon.style.display = 'none';
        if (sunIcon) sunIcon.style.display = 'block';
    }

    const animateElements = () => {
        const sections = document.querySelectorAll('section');

        sections.forEach(section => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('section-animate');
                    }
                });
            }, { threshold: 0.1 });

            observer.observe(section);
        });
    };

    animateElements();
});

// Handle contact form submission
if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const subject = document.getElementById('subject').value.trim();
        const message = document.getElementById('message').value.trim();

        // Simple form validation
        if (!name || !email || !subject || !message) {
            alert('Please fill out all fields');
            return;
        }

        const recipient = 'mumbipaul2026@gmail.com';
        const emailBody = `Name: ${name}\nEmail: ${email}\n\n${message}`;
        const mailtoUrl = `mailto:${recipient}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(emailBody)}`;

        window.location.href = mailtoUrl;
    });
}

// Add smooth scrolling to all links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        const targetId = this.getAttribute('href');
        if (targetId === '#') return; // Skip if href is just "#"

        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 80, // Adjust for header height
                behavior: 'smooth'
            });
        }
    });
});

// Add typing effect to the binary in hero section
const binaryElement = document.querySelector('.binary');
if (binaryElement) {
    const originalText = binaryElement.innerText;
    binaryElement.innerText = '';

    let i = 0;
    const typeWriter = () => {
        if (i < originalText.length) {
            binaryElement.innerText += originalText.charAt(i);
            i++;
            setTimeout(typeWriter, 50);
        }
    };

    // Start typing effect when page loads
    setTimeout(typeWriter, 1000);
}
