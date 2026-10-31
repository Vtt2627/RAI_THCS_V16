function loadResearchResults(){
    return JSON.parse(localStorage.getItem("aiResponsibleResult")) || [];
}

function displayResearchDashboard(){
    const results = loadResearchResults();
    const total = document.getElementById("researchTotalResults");
    const average = document.getElementById("researchAverageScore");
    if (results.length === 0){
        total.textContent = "Chưa có dữ liệu làm bài.";
        average.textContent = "";
        return;
    }
    const latest = results[results.length-1];
    total.textContent = "Mã học sinh gần nhất: " + latest.studentCode;
    average.textContent = "Điểm đạt được: " + latest.score + "/" + (latest.totalQuestions || 9);
}

function displayResearchBehaviorAnalysis(){
    const results = loadResearchResults();
    const container = document.getElementById("researchBehaviorAnalysis");
    container.innerHTML="";
    if(results.length === 0){
        container.textContent = "Chưa có dữ liệu.";
        return;
    }
    const latest = results[results.length-1];
    for(const behavior in behaviors){
        const p = document.createElement("p");
        const isPassed = latest.behaviorResults[behavior] === 1;
        p.textContent = `${behavior} (${behaviors[behavior]}): ${isPassed ? '✓ Đã đạt' : '⚠ Cần chú ý'}`;
        p.style.color = isPassed ? '#4ade80' : '#f87171';
        container.appendChild(p);
    }
}

document.getElementById("researchNextBtn").addEventListener("click", function(){
    const results = loadResearchResults();
    if(results.length === 0){
        alert("Chưa có kết quả để phân tích.");
        return;
    }

    const overlay = document.getElementById("loadingOverlay");
    overlay.style.display = "flex";

    const loadingSteps = [
        "Đang trích xuất dữ liệu từ LocalStorage...",
        "Agent đang rà soát các hành vi chưa đạt...",
        "Đang phân bổ Kho dữ liệu Bù đắp & Nâng cao...",
        "Đã hoàn tất! Đang chuyển hướng..."
    ];

    let step = 0;
    const textEl = document.getElementById("loadingText");
    
    const interval = setInterval(() => {
        step++;
        if(step < loadingSteps.length) {
            textEl.textContent = loadingSteps[step];
        } else {
            clearInterval(interval);
            window.location.href = "learning.html";
        }
    }, 700);
});

displayResearchDashboard();
displayResearchBehaviorAnalysis();