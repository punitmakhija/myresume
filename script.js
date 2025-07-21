
        function showTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }

        function scrollToTop() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }

        function downloadResume() {
            alert('PDF download would be implemented with server-side functionality. For now, you can print this page as PDF using Ctrl+P or Cmd+P');
        }

        // Add smooth scrolling animation on load
        window.addEventListener('load', function() {
            document.body.style.animation = 'fadeIn 1s ease-in';
        });

        // Add click effects to skill tags
        document.querySelectorAll('.skill-tag').forEach(tag => {
            tag.addEventListener('click', function() {
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'scale(1.05)';
                }, 100);
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 200);
            });
        });

        // Parallax effect for header
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            const header = document.querySelector('.header');
            if (header) {
                header.style.transform = `translateY(${rate}px)`;
            }
        });

        // Add typing effect to name (optional enhancement)
        function typeWriter() {
            const nameElement = document.querySelector('.name');
            const text = nameElement.textContent;
            nameElement.textContent = '';
            let i = 0;
            
            function type() {
                if (i < text.length) {
                    nameElement.textContent += text.charAt(i);
                    i++;
                    setTimeout(type, 100);
                }
            }
            type();
        }

        // Uncomment the line below if you want the typing effect
        // setTimeout(typeWriter, 500);
    