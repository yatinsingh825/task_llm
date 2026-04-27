const API = "https://YOUR-BACKEND-URL.onrender.com";
let spellTimeout = null;

// Live spell check as user types
document.getElementById("searchInput").addEventListener("input", (e) => {
    clearTimeout(spellTimeout);
    const text = e.target.value;
    
    if (text.length < 3) {
        hideSuggestions();
        return;
    }
    
    spellTimeout = setTimeout(() => checkSpelling(text), 400);
});

// Press Enter to search
document.getElementById("searchInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") doSearch();
});

async function checkSpelling(text) {
    try {
        const res = await fetch(`${API}/spell-check`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });
        const data = await res.json();
        
        if (data.has_errors) {
            showSuggestions(data);
        } else {
            hideSuggestions();
        }
    } catch (e) {
        console.error("Spell check error:", e);
    }
}

function showSuggestions(spellData) {
    const box = document.getElementById("spellSuggestions");
    box.innerHTML = "";
    
    for (const [wrong, info] of Object.entries(spellData.suggestions)) {
        const div = document.createElement("div");
        div.className = "suggestion-item";
        div.textContent = `Did you mean: "${info.best}"?`;
        div.onclick = () => {
            document.getElementById("searchInput").value = spellData.corrected;
            hideSuggestions();
        };
        box.appendChild(div);
    }
    
    box.classList.remove("hidden");
}

function hideSuggestions() {
    document.getElementById("spellSuggestions").classList.add("hidden");
}

async function doSearch() {
    const query = document.getElementById("searchInput").value.trim();
    if (!query) return;
    
    hideSuggestions();
    
    // Show loading
    document.getElementById("aiResponse").className = "ai-response";
    document.getElementById("aiResponse").innerHTML = "⏳ Planning your perfect wedding...";
    document.getElementById("imageGrid").innerHTML = '<div class="loading">🔍 Finding beautiful images...</div>';
    document.getElementById("videoGrid").innerHTML = "";
    
    try {
        const res = await fetch(`${API}/search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, use_local_model: false })
        });
        
        const data = await res.json();
        
        // Show AI response
        document.getElementById("aiResponse").innerHTML = `
            <strong>💡 AI Suggestion:</strong><br><br>${data.ai_response}
        `;
        
        // Show images
        const imageGrid = document.getElementById("imageGrid");
        imageGrid.innerHTML = "";
        
        if (data.images.length > 0) {
            data.images.forEach(img => {
                const el = document.createElement("img");
                el.src = img.thumbnail || img.url;
                el.alt = "Wedding inspiration";
                el.onclick = () => window.open(img.url, "_blank");
                imageGrid.appendChild(el);
            });
        } else {
            imageGrid.innerHTML = "<p>No images found for this search.</p>";
        }
        
        // Show videos
        const videoGrid = document.getElementById("videoGrid");
        videoGrid.innerHTML = "";
        
        if (data.videos.length > 0) {
            data.videos.forEach(vid => {
                const el = document.createElement("video");
                el.src = vid.url;
                el.controls = true;
                el.muted = true;
                videoGrid.appendChild(el);
            });
        }
        
    } catch (e) {
        document.getElementById("aiResponse").innerHTML = "❌ Error connecting to backend. Is it running?";
        console.error(e);
    }
}