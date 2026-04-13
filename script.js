const API = window.location.origin.includes("localhost") 
            ? "http://127.0.0.1:5000" 
            : window.location.origin;

let reportData = null;

function showRegister() {
    document.getElementById('login-box').style.display = 'none';
    document.getElementById('register-box').style.display = 'block';
}

function showLogin() {
    document.getElementById('login-box').style.display = 'block';
    document.getElementById('register-box').style.display = 'none';
}

function handleRegister(e) {
    e.preventDefault();
    const u = document.getElementById("register-username").value;
    const p = document.getElementById("register-password").value;
    
    fetch(`${API}/register`, { 
        method: "POST", 
        headers: {"Content-Type": "application/json"}, 
        body: JSON.stringify({username: u, password: p}) 
    })
    .then(res => {
        if(res.ok) {
            alert("Registration successful! Please login.");
            showLogin();
        } else {
            alert("Username already taken.");
        }
    });
}

function handleLogin(e) {
    e.preventDefault();
    const u = document.getElementById("login-username").value;
    const p = document.getElementById("login-password").value;
    
    fetch(`${API}/login`, { 
        method: "POST", 
        headers: {"Content-Type": "application/json"}, 
        body: JSON.stringify({username: u, password: p}) 
    })
    .then(res => res.ok ? res.json() : Promise.reject())
    .then(() => {
        document.getElementById("auth-box").style.display = "none";
        document.getElementById("main").style.display = "flex";
        document.getElementById("user-display").innerText = u;
        document.body.style.background = "#0f172a"; 
    })
    .catch(() => alert("Login failed. Check credentials or register first."));
}

function handleUpload(e) {
    e.preventDefault();
    const file = document.getElementById("file").files[0];
    if(!file) return alert("Please select a file.");

    document.getElementById("loader").style.display = "block";
    const formData = new FormData();
    formData.append("file", file);

    fetch(`${API}/upload`, { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
        reportData = data;
        document.getElementById("rows").innerText = data.rows;
        document.getElementById("cols").innerText = data.cols;
        document.getElementById("errors").innerText = data.errors;
        document.getElementById("quality").innerText = data.quality + "%";
        
        const list = document.getElementById("error-list");
        list.innerHTML = "";
        data.error_list.forEach(err => {
            const d = document.createElement("div");
            d.style.color = "#ff4d4d";
            d.style.padding = "5px 0";
            d.style.borderBottom = "1px solid #334155";
            d.innerText = "🚨 " + err;
            list.appendChild(d);
        });
        document.getElementById("dl-btn").style.display = "block";
    })
    .finally(() => document.getElementById("loader").style.display = "none");
}

function handleDownload(e) {
    e.preventDefault();
    fetch(`${API}/report`, { 
        method: "POST", 
        headers: {"Content-Type": "application/json"}, 
        body: JSON.stringify(reportData) 
    })
    .then(res => res.blob())
    .then(blob => {
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "DQC_Report.pdf";
        a.click();
    });
}