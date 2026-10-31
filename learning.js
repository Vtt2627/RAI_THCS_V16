const STORAGE_KEY = "aiResponsibleResult";
const AGENT_API_URL = "/api/get-learning-content";

// Lưu trữ các câu hỏi đã bốc cho từng bài học để tránh bốc trùng nếu trả lời sai
let currentActiveQuizzes = {};

async function initLearningPage() {
    const results = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    const latest = results.length > 0 ? results[results.length - 1] : { studentCode: "HS_DEFAULT", behaviorResults: {} };
    const needAttention = Object.keys(latest.behaviorResults || {}).filter(k => latest.behaviorResults[k] === 0);

    try {
        const response = await fetch(AGENT_API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                studentCode: latest.studentCode,
                needAttention: needAttention
            })
        });

        const data = await response.json();
        document.getElementById("learningMessage").textContent = data.message;
        renderLessonsWithGate(data.content);

    } catch (error) {
        console.error("Lỗi kết nối Agent:", error);
        document.getElementById("learningMessage").innerHTML = "<span style='color: #ef4444;'>Không thể kết nối tới Server Python Backend. Hãy đảm bảo bạn đã chạy file main.py!</span>";
    }
}

function renderLessonsWithGate(contentData) {
    const container = document.getElementById("lessonContainer");
    container.innerHTML = "";

    const lessons = Array.isArray(contentData) ? contentData : Object.values(contentData);

    lessons.forEach((lesson, index) => {
        const card = document.createElement("div");
        card.className = "lesson-card";
        
        let htmlContent = `<h3>Bài học ${index + 1}: ${lesson.title}</h3>`;

        // Video nhúng YouTube
        if (lesson.video_url) {
            htmlContent += `
                <div class="video-wrapper">
                    <iframe src="${lesson.video_url}" allowfullscreen></iframe>
                </div>
            `;
        }

        // Bài đọc lý thuyết
        if (lesson.reading_content) {
            htmlContent += `<div class="reading-box">${lesson.reading_content}</div>`;
        }

        // Nút bấm "Tôi đã đọc và hiểu nội dung này"
        htmlContent += `
            <div style="text-align: center; margin: 20px 0;">
                <button class="understood-btn" id="understoodBtn_${index}" data-index="${index}">✓ Tôi đã đọc và hiểu nội dung này</button>
            </div>
        `;

        // Khung chứa câu hỏi kiểm tra (Bắt đầu bị ẩn)
        if (lesson.check_questions && lesson.check_questions.length > 0) {
            htmlContent += `<div id="quizContainer_${index}" class="check-quiz-box" style="display: none;"></div>`;
        }

        card.innerHTML = htmlContent;
        container.appendChild(card);

        // Lưu danh sách câu hỏi của bài học này vào bộ nhớ tạm
        currentActiveQuizzes[index] = {
            allQuestions: lesson.check_questions || [],
            lastQuestionId: null
        };
    });

    // SỰ KIỆN: Bấm nút "Tôi đã hiểu nội dung" -> Bốc ngẫu nhiên câu hỏi
    document.querySelectorAll(".understood-btn").forEach(btn => {
        btn.addEventListener("click", function() {
            const idx = this.getAttribute("data-index");
            const quizInfo = currentActiveQuizzes[idx];

            if (!quizInfo || quizInfo.allQuestions.length === 0) return;

            // Bốc 1 câu hỏi ngẫu nhiên khác với câu vừa trả lời sai (nếu có)
            let availableQuestions = quizInfo.allQuestions.filter(q => q.id !== quizInfo.lastQuestionId);
            if (availableQuestions.length === 0) availableQuestions = quizInfo.allQuestions;

            const selectedQuiz = availableQuestions[Math.floor(Math.random() * availableQuestions.length)];
            quizInfo.lastQuestionId = selectedQuiz.id;

            // Render câu hỏi vào khung
            const quizContainer = document.getElementById(`quizContainer_${idx}`);
            quizContainer.innerHTML = `
                <p><strong>📝 Câu hỏi kiểm tra [Mã: ${selectedQuiz.id || 'Q'}]:</strong> ${selectedQuiz.question}</p>
                <div id="options_${idx}">
                    ${selectedQuiz.options.map((opt, optIdx) => `
                        <label style="display:block; margin: 8px 0; cursor:pointer;">
                            <input type="radio" name="check_q_${idx}" value="${optIdx}"> ${opt}
                        </label>
                    `).join('')}
                </div>
                <button class="submit-check-btn" data-index="${idx}" data-correct="${selectedQuiz.answer}" style="margin-top: 10px;">Nộp câu trả lời</button>
                <p id="quizFeedback_${idx}" style="margin-top: 8px; font-weight: 600;"></p>
            `;

            quizContainer.style.display = "block";
            this.disabled = true;
            this.style.opacity = "0.5";
            this.textContent = "Đang làm câu hỏi kiểm tra bên dưới...";
            
            quizContainer.scrollIntoView({ behavior: 'smooth' });

            // Gán lại sự kiện Nộp bài cho nút vừa tạo
            attachSubmitEvent(idx);
        });
    });
}

// SỰ KIỆN: Nộp câu trả lời kiểm tra
function attachSubmitEvent(idx) {
    const submitBtn = document.querySelector(`.submit-check-btn[data-index="${idx}"]`);
    if (!submitBtn) return;

    submitBtn.addEventListener("click", function() {
        const correctAnswer = Number(this.getAttribute("data-correct"));
        const selected = document.querySelector(`input[name="check_q_${idx}"]:checked`);
        const feedback = document.getElementById(`quizFeedback_${idx}`);
        const understoodBtn = document.getElementById(`understoodBtn_${idx}`);
        const quizContainer = document.getElementById(`quizContainer_${idx}`);

        if (!selected) {
            alert("Vui lòng chọn một đáp án!");
            return;
        }

        const chosenAnswer = Number(selected.value);

        if (chosenAnswer === correctAnswer) {
            // TRẢ LỜI ĐÚNG: Đạt yêu cầu bài học
            feedback.style.color = "#4ade80";
            feedback.textContent = "Chính xác! Bạn đã hoàn thành xuất sắc bài học này.";
            submitBtn.disabled = true;
            submitBtn.style.opacity = "0.5";
            understoodBtn.textContent = "✓ Đã hoàn thành bài học này";
        } else {
            // TRẢ LỜI SAI: Yêu cầu học lại
            feedback.style.color = "#ef4444";
            feedback.textContent = "✕ Chưa chính xác! Bạn cần đọc/xem lại nội dung phía trên. Hãy bấm lại nút 'Tôi đã đọc và hiểu' để thử lại câu hỏi khác.";
            
            // Tự động ẩn câu hỏi sau 2.5 giây để học sinh đọc lại bài
            setTimeout(() => {
                quizContainer.style.display = "none";
                understoodBtn.disabled = false;
                understoodBtn.style.opacity = "1";
                understoodBtn.textContent = "Tôi đã đọc lại và hiểu nội dung (Thử lại)";
                understoodBtn.scrollIntoView({ behavior: 'smooth' });
            }, 2500);
        }
    });
}

// Khung Chat trực tiếp với Agent ở phía dưới trang học tập
document.getElementById("sendQueryBtn").addEventListener("click", async function() {
    const input = document.getElementById("userQuery");
    const text = input.value.trim();
    if (!text) return;

    addChatMessage("Bạn", text);
    input.value = "";

    try {
        const results = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
        const studentCode = results.length > 0 ? results[results.length - 1].studentCode : "HS_001";

        const res = await fetch('/api/chat', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ studentCode: studentCode, message: text })
        });
        const data = await res.json();
        addChatMessage("Agent", data.reply);
    } catch (err) {
        addChatMessage("Hệ thống", "Không thể phản hồi lúc này.");
    }
});

function addChatMessage(sender, text) {
    const chatBox = document.getElementById("chatBox");
    const msgDiv = document.createElement("div");
    msgDiv.style.marginBottom = "8px";
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

initLearningPage();