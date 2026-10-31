async function initLearningPage() {
    loadYouTubeAPI();
    
    let needAttention = [];
    let studentCode = "HS_DEFAULT";

    const results = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    if (results.length > 0) {
        const latest = results[results.length - 1];
        studentCode = latest.studentCode || studentCode;
        
        // Lọc chính xác các mã hành vi có kết quả bằng 0 (làm sai)
        if (latest.behaviorResults) {
            needAttention = Object.keys(latest.behaviorResults).filter(k => latest.behaviorResults[k] === 0);
        }
    }

    // Gửi yêu cầu lên FastAPI Backend
    try {
        const response = await fetch(AGENT_API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                studentCode: studentCode,
                need_attention: needAttention // Truyền mảng câu sai đã gom
            })
        });

        const data = await response.json();
        
        // Hiển thị thông báo lộ trình
        const messageEl = document.getElementById("learningMessage");
        if (messageEl) {
            messageEl.textContent = data.message;
        }
        
        renderLessonsWithGate(data.content);

    } catch (error) {
        console.error("Lỗi kết nối Agent:", error);
    }
}
