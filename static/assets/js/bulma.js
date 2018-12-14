document.addEventListener('DOMContentLoaded', function () {

    $(document).ready(function () {

        // Check for click events on the navbar burger icon
        $(".navbar-burger").click(function () {

            // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
            $(".navbar-burger").toggleClass("is-active");
            $(".navbar-menu").toggleClass("is-active");

        });
    });

    $(document).on('click', '.notification > button.delete', function () {
        $(this).parent().addClass('is-hidden');
        return false;
    });


    let rootEl = document.documentElement;
    let $modals = getAll('.modal');
    let $modalButtons = getAll('.modal-button');
    let $modalCloses = getAll('.modal-background, .modal-close, .modal-card-head .delete, .modal-card-foot .button');

    if ($modalButtons.length > 0) {
        $modalButtons.forEach(function ($el) {
            $el.addEventListener('click', function () {
                var target = $el.dataset.target;
                openModal(target);
            });
        });
    }

    if ($modalCloses.length > 0) {
        $modalCloses.forEach(function ($el) {
            $el.addEventListener('click', function () {
                closeModals();
            });
        });
    }

    function openModal(target) {
        var $target = document.getElementById(target);
        rootEl.classList.add('is-clipped');
        $target.classList.add('is-active');
    }

    function closeModals() {
        rootEl.classList.remove('is-clipped');
        $modals.forEach(function ($el) {
            $el.classList.remove('is-active');
        });
    }

    function getAll(selector) {
        return Array.prototype.slice.call(document.querySelectorAll(selector), 0);
    }


    const curLine = document.location.hash;
    if (curLine.startsWith('#L')) {
        const hashlist = curLine.substring(2).split(',');
        if (hashlist.length > 0 && hashlist[0] !== '') {
            hashlist.forEach(function (el) {
                const line = document.getElementById(`l${el}`);
                if (line) {
                    line.classList.add('marked');
                }
            });
        }
    }

    const lines = document.querySelectorAll('.snippet-code li');
    lines.forEach(function (el) {
        el.onclick = function () {
            el.classList.toggle('marked');
            let hash = 'L';
            const marked = document.querySelectorAll('.snippet-code li.marked');
            marked.forEach(function (line) {
                if (hash !== 'L') {
                    hash += ',';
                }
                hash += line.getAttribute('id').substring(1);
            });
            window.location.hash = hash;
        };
    });

    const wordwrapCheckbox = document.getElementById('wordwrap');
    const snippetDiv = document.querySelectorAll('.snippet-code');

    function toggleWordwrap() {
        if (wordwrapCheckbox.checked) {
            snippetDiv.forEach(function (i) {
                i.classList.add('wordwrap') 
                i.style="padding-right: 5px"
            });
        } else {
            snippetDiv.forEach(function (i) {
                i.classList.remove('wordwrap') 
                i.style="padding-right: 0px"
            });
        }
    }

    if (wordwrapCheckbox && snippetDiv) {
        toggleWordwrap();
        wordwrapCheckbox.onchange = toggleWordwrap;
    }

    const af = document.querySelector('.autofocus textarea');
    if (af !== null) {
        af.focus();
    }

    let navbarEl = document.getElementById('navbar');
    let specialShadow = document.getElementById('specialShadow');
    let NAVBAR_HEIGHT = 52;
    let THRESHOLD = 160;
    let horizon = NAVBAR_HEIGHT;
    let whereYouStoppedScrolling = 0;
    let scrollFactor = 0;
    let currentTranslate = 0;

    function upOrDown(lastY, currentY) {
        if (currentY >= lastY) {
            return goingDown(currentY);
        }
        return goingUp(currentY);
    }

    function goingDown(currentY) {
        let trigger = NAVBAR_HEIGHT;
        whereYouStoppedScrolling = currentY;

        if (currentY > horizon) {
            horizon = currentY;
        }

        translateHeader(currentY, false);
    }

    function goingUp(currentY) {
        let trigger = 0;

        if (currentY < whereYouStoppedScrolling - NAVBAR_HEIGHT) {
            horizon = currentY + NAVBAR_HEIGHT;
        }

        translateHeader(currentY, true);
    }

    function constrainDelta(delta) {
        return Math.max(0, Math.min(delta, NAVBAR_HEIGHT));
    }

    function translateHeader(currentY, upwards) {
        // let topTranslateValue;
        let translateValue = void 0;

        if (upwards && currentTranslate === 0) {
            translateValue = 0;
        } else if (currentY <= NAVBAR_HEIGHT) {
            translateValue = currentY * -1;
        } else {
            let delta = constrainDelta(Math.abs(currentY - horizon));
            translateValue = delta - NAVBAR_HEIGHT;
        }

        if (translateValue !== currentTranslate) {
            let navbarStyle = '\n        transform: translateY(' + translateValue + 'px);\n      ';
            currentTranslate = translateValue;
            navbarEl.setAttribute('style', navbarStyle);
        }

        if (currentY > THRESHOLD * 2) {
            scrollFactor = 1;
        } else if (currentY > THRESHOLD) {
            scrollFactor = (currentY - THRESHOLD) / THRESHOLD;
        } else {
            scrollFactor = 0;
        }

        var translateFactor = 1 + translateValue / NAVBAR_HEIGHT;
        specialShadow.style.opacity = scrollFactor;
        specialShadow.style.transform = 'scaleY(' + translateFactor + ')';
    }

    translateHeader(window.scrollY, false);

    let ticking = false;
    let lastY = 0;

    window.addEventListener('scroll', function () {
        let currentY = window.scrollY;

        if (!ticking) {
            window.requestAnimationFrame(function () {
                upOrDown(lastY, currentY);
                ticking = false;
                lastY = currentY;
            });
        }

        ticking = true;
    });
});
