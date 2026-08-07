// ==========================================
// AI Nano Counter Dashboard JS
// ==========================================

// Counter Animation
const counters = document.querySelectorAll(".card h2");

counters.forEach(counter => {

    const target = counter.innerText.replace("%","").replace("s","");

    let count = 0;

    const speed = target / 60;

    function update(){

        if(count < target){

            count += speed;

            if(counter.innerText.includes("%")){

                counter.innerHTML = count.toFixed(1) + "%";

            }
            else if(counter.innerText.includes("s")){

                counter.innerHTML = count.toFixed(2) + "s";

            }
            else{

                counter.innerHTML = Math.floor(count);

            }

            requestAnimationFrame(update);

        }

    }

    update();

});

// ==========================================
// Line Chart
// ==========================================

const lineCtx = document.getElementById("lineChart");

if(lineCtx){

new Chart(lineCtx,{

type:"line",

data:{

labels:["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],

datasets:[{

label:"Objects Detected",

data:[120,190,160,280,320,290,410],

borderColor:"#5B8CFF",

backgroundColor:"rgba(91,140,255,.15)",

fill:true,

tension:.4,

borderWidth:3,

pointRadius:5,

pointBackgroundColor:"#8B5CF6"

}]

},

options:{

responsive:true,

plugins:{

legend:{

labels:{

color:"#fff"

}

}

},

scales:{

x:{

ticks:{color:"#ddd"},

grid:{color:"rgba(255,255,255,.05)"}

},

y:{

ticks:{color:"#ddd"},

grid:{color:"rgba(255,255,255,.05)"}

}

}

}

});

}

// ==========================================
// Doughnut Chart
// ==========================================

const pieCtx = document.getElementById("pieChart");

if(pieCtx){

new Chart(pieCtx,{

type:"doughnut",

data:{

labels:[

"Person",

"Car",

"Bottle",

"Chair",

"Other"

],

datasets:[{

data:[42,28,15,9,6],

backgroundColor:[

"#5B8CFF",

"#8B5CF6",

"#22C55E",

"#F59E0B",

"#EF4444"

],

borderWidth:0

}]

},

options:{

responsive:true,

plugins:{

legend:{

labels:{

color:"#fff"

}

}

}

}

});

}

// ==========================================
// Welcome Animation
// ==========================================

window.addEventListener("load",()=>{

document.querySelector(".dashboard").style.opacity="1";

});

// ==========================================
// Card Hover Glow
// ==========================================

document.querySelectorAll(".card").forEach(card=>{

card.addEventListener("mouseenter",()=>{

card.classList.add("glow");

});

card.addEventListener("mouseleave",()=>{

card.classList.remove("glow");

});

});

// ==========================================
// Live Time
// ==========================================

const topbar = document.querySelector(".topbar p");

if(topbar){

setInterval(()=>{

const now=new Date();

topbar.innerHTML="AI Powered Dashboard • "+now.toLocaleTimeString();

},1000);

}