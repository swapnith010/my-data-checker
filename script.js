// This "Smart Link" automatically detects if you are on your laptop or on Render
const API = window.location.origin.includes("localhost") 
            ? "http://127.0.0.1:5000" 
            : window.location.origin;

let reportData = null;

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
    })
    .catch(() => alert("Access Denied: Please Register first or check your password."));
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
    .then(res => res.ok ? showLogin() : alert("Username exists"));
}

function handleUpload(e) {
    e.preventDefault();
    const file = document.getElementById("file").files[0];
    if(!file) return alert("Upload file first");

    document.getElementById("loader").style.display = "flex";
    const formData = new FormData();
    formData.append("file", file);

    fetch(`${API}/upload`, { method: "POST", body: formData })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert("Analysis Error: " + data.error);
            return;
        }

        reportData = data;
        document.getElementById("rows").innerText = data.rows;
        document.getElementById("cols").innerText = data.cols;
        document.getElementById("errors").innerText = data.errors;
        
        // Update Quality Badge
        const q = data.quality;
        const qElement = document.getElementById("quality");
        qElement.innerText = q + "%";
        qElement.className = q > 80 ? "score-high" : (q > 50 ? "score-mid" : "score-low");

        document.getElementById("file-meta").innerText = `Last Scan: ${file.name} | ${new Date().toLocaleTimeString()}`;
        
        // --- FIXED INSPECTION LOG ---
        const list = document.getElementById("error-list");
        list.innerHTML = ""; // Completely clear previous messages
        
        if (data.error_list && data.error_list.length > 0) {
            data.error_list.forEach(err => {
                const d = document.createElement("div"); 
                d.className = "error-item"; 
                d.style.color = "white"; // Ensure text is visible
                d.style.padding = "10px";
                d.style.marginBottom = "5px";
                d.style.borderLeft = "4px solid #ff4d4d";
                d.style.background = "rgba(255, 77, 77, 0.1)";
                d.innerText = err;
                list.appendChild(d);
            });
        } else {
            list.innerHTML = '<div style="color: #4ade80; padding: 10px;">✅ No data quality issues detected!</div>';
        }
        
        document.getElementById("dl-btn").style.display = "block";
    })
    .catch(err => alert("Upload failed. The file might be too large or the server timed out."))
    .finally(() => document.getElementById("loader").style.display = "none");
}

function handleDownload(e) {
    e.preventDefault();
    if(!reportData) return alert("No data to download");

    fetch(`${API}/report`, { 
        method: "POST", 
        headers: {"Content-Type": "application/json"}, 
        body: JSON.stringify(reportData) 
    })
    .then(res => res.blob())
    .then(blob => {
        const a = document.createElement("a"); 
        a.href = URL.createObjectURL(blob); 
        a.download = "DQC_Pro_Report.pdf"; 
        a.click();
    })
    .catch(() => alert("Could not generate report."));
}

function showRegister() { 
    document.getElementById("login-box").style.display="none"; 
    document.getElementById("register-box").style.display="block"; 
}

function showLogin() { 
    document.getElementById("login-box").style.display="block"; 
    document.getElementById("register-box").style.display="none"; 
}