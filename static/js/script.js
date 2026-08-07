// ================================
// AI Nano Counter
// script.js
// ================================

console.log("🤖 AI Nano Counter Loaded Successfully");

// ----------------------------
// Smooth Page Fade-In
// ----------------------------

document.addEventListener("DOMContentLoaded", () => {

    document.body.style.opacity = "0";

    setTimeout(() => {

        document.body.style.transition = "opacity 0.8s ease";

        document.body.style.opacity = "1";

    }, 100);

});

// ----------------------------
// Dashboard Card Animation
// ----------------------------

const cards = document.querySelectorAll(".dash-card");

cards.forEach((card) => {

    card.addEventListener("mouseenter", () => {

        card.style.transform = "translateY(-10px) scale(1.03)";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform = "translateY(0px) scale(1)";

    });

});

// ----------------------------
// Feature Card Animation
// ----------------------------

const featureCards = document.querySelectorAll(".feature-card");

featureCards.forEach((card) => {

    card.addEventListener("mouseenter", () => {

        card.style.transform = "translateY(-10px)";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform = "translateY(0px)";

    });

});

// ----------------------------
// Upload File Name Preview
// ----------------------------

const fileInput = document.querySelector('input[type="file"]');

if (fileInput) {

    fileInput.addEventListener("change", function () {

        if (this.files.length > 0) {

            alert("Selected Image : " + this.files[0].name);

        }

    });

}

// ----------------------------
// Loading Effect on Detect Button
// ----------------------------

const detectButton = document.querySelector(".btn");

if (detectButton) {

    detectButton.addEventListener("click", () => {

        if (fileInput && fileInput.files.length > 0) {

            detectButton.innerHTML =
                '<i class="fa-solid fa-spinner fa-spin"></i> Detecting...';

        }

    });

}

// ----------------------------
// Welcome Message
// ----------------------------

setTimeout(() => {

    console.log("🚀 YOLO11L AI Model Ready");

}, 1000);

// Animated Counter

const counters = document.querySelectorAll(".counter");

counters.forEach(counter=>{

    const update=()=>{

        const target=+counter.getAttribute("data-target");

        const count=+counter.innerText;

        const speed=80;

        const inc=target/speed;

        if(count<target){

            counter.innerText=Math.ceil(count+inc);

            setTimeout(update,20);

        }

        else{

            counter.innerText=target.toLocaleString();

        }

    };

    update();

});