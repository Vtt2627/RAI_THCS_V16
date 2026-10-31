const STORAGE_KEY = "aiResponsibleResult";
const AGENT_API_URL = "/api/get-learning-content";

let currentActiveQuizzes = {};
let ytPlayers = {};

function loadYouTubeAPI() {
    if (!window.YT) {
        const tag = document.createElement('script');
        tag.src = "https://www.youtube.com/iframe_api";
        const firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    }
}

async function initLearningPage() {
    loadYouTubeAPI();
    
    let needAttention = [];
    let studentCode = "HS_DEFAULT";

    // Đọc dữ liệu từ localStorage theo cấu trúc kết quả bài làm
    const results = JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    if (results.length > 0) {
        const latest = results[results.length - 1];
        studentCode = latest.studentCode || studentCode;
        
        // Lọc các mã hành vi có kết quả bằng 0 (làm sai)
        if (latest.behaviorResults) {
            needAttention = Object.keys(latest.behaviorResults).filter(k => latest.behaviorResults[k] === 0);
        }
        
        // Dự phòng nếu behaviorResults không tồn tại nhưng có recommendations
        if (needAttention.length === 0 && latest.recommendations) {
            needAttention = latest.recommendations.map(r => r.behavior);
        }
    }

    // Dự phòng kiểm tra kho lưu trữ trực tiếp learningData nếu aiResponsibleResult trống
    if (needAttention.length === 0) {
        const directLearningData = JSON.parse(localStorage.getItem("learningData"));
        if (directLearningData && directLearningData.need_attention) {
            needAttention = directLearningData.need_attention;
        }
    }

    try {
        const response = await fetch(AGENT_API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                studentCode: studentCode,
                need_attention: needAttention // Tên trường chính xác khớp với FastAPI backend
            })
        });

        const data = await response.json();
        
        // Hiển thị thông báo lộ trình ở đầu trang
        const messageEl = document.getElementById("learningMessage");
        if (messageEl) {
            messageEl.textContent = data.message || "Lộ trình học tập cá nhân hóa:";
        }
        
        // Render giao diện thẻ bài học
        renderLessonsWithGate(data.content);

    } catch (error) {
        console.error("Lỗi kết nối Agent:", error);
        const messageEl = document.getElementById("learningMessage");
        if (messageEl) {
            messageEl.innerHTML = "<span style='color: #ef4444;'>Không thể kết nối tới Server Python Backend. Hãy đảm bảo file main.py đang chạy!</span>";
        }
    }
}

function renderLessonsWithGate(contentData) {
    const container = document.getElementById("lessonContainer");
    if (!container) return;
    container.innerHTML = "";

    const lessons = Array.isArray(contentData) ? contentData : Object.values(contentData);

    lessons.forEach((lesson, index) => {
        const card = document.createElement("div");
        card.className = "lesson-card";
        
        let htmlContent = `<h3>Bài học ${index + 1}: ${lesson.title || "Nội dung khắc phục"}</h3>`;

        let hasVideo = false;
        const videoSrc = lesson.video_url || lesson.videoUrl;
        if (videoSrc) {
            hasVideo = true;
            const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
            const match = videoSrc.match(regExp);
            const videoId = (match && match[2].length === 11) ? match[2] : "UlXXRd3HGT0";

            htmlContent += `
                <div class="video-wrapper">
                    <div id="yt-player-${index}" data-videoid="${videoId}"></div>
                </div>
            `;
        }

        const readingText = lesson.reading_content || lesson.description || lesson.content;
        if (readingText) {
            htmlContent += `<div class="reading-box" style="margin: 15px 0; line-height: 1.6;">${readingText}</div>`;
        }

        const btnDisabledAttr = hasVideo ? "disabled style='opacity: 0.5; cursor: not-allowed;'" : "";
        const btnText = hasVideo ? "🔒 Vui lòng xem hết video để mở khóa nút này" : "✓ Tôi đã đọc và hiểu nội dung này";

        htmlContent += `
            <div style="text-align: center; margin: 20px 0;">
                <button class="understood-btn" id="understoodBtn_${index}" data-index="${index}" ${btnDisabledAttr}>${btnText}</button>
            </div>
        `;

        const questionsList = lesson.check_questions || lesson.questions;
        if (questionsList && questionsList.length > 0) {
            htmlContent += `<div id="quizContainer_${index}" class="check-quiz-box" style="display: none; background: #111b2b; padding: 15px; border-radius: 6px; margin-top: 15px;"></div>`;
        }

        card.innerHTML = htmlContent;
        container.appendChild(card);

        currentActiveQuizzes[index] = {
            allQuestions: questionsList || [],
            lastQuestionId: null
        };
    });

    setTimeout(() => {
        lessons.forEach((lesson, index) => {
            const videoSrc = lesson.video_url || lesson.videoUrl;
            if (videoSrc) {
                initYouTubePlayer(index);
            }
        });
    }, 500);

    document.querySelectorAll(".understood-btn").forEach(btn => {
        btn.addEventListener("click", function() {
            if (this.disabled) return;
            const idx = this.getAttribute("data-index");
            const quizInfo = currentActiveQuizzes[idx];

            if (!quizInfo || quizInfo.allQuestions.length === 0) return;

            let availableQuestions = quizInfo.allQuestions.filter(q => q.id !== quizInfo.lastQuestionId);
            if (availableQuestions.length === 0) availableQuestions = quizInfo.allQuestions;

            const selectedQuiz = availableQuestions[Math.floor(Math.random() * availableQuestions.length)];
            quizInfo.lastQuestionId = selectedQuiz.id;

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
                <button class="submit-check-btn" data-index="${idx}" data-correct="${selectedQuiz.answer}" style="margin-top: 10px; padding: 8px 16px; background: #2563eb; color: white; border: none; border-radius: 4px; cursor: pointer;">Nộp câu trả lời</button>
                <p id="quizFeedback_${idx}" style="margin-top: 8px; font-weight: 600;"></p>
            `;

            quizContainer.style.display = "block";
            this.disabled = true;
            this.style.opacity = "0.5";
            this.style.cursor = "not-allowed";
            this.textContent = "Đang làm câu hỏi kiểm tra bên dưới...";
            
            quizContainer.scrollIntoView({ behavior: 'smooth' });
            attachSubmitEvent(idx);
        });
    });
}

function initYouTubePlayer(index) {
    const playerElement = document.getElementById(`yt-player-${index}`);
    if (!playerElement) return;
    const videoId = playerElement.getAttribute("data-videoid");

    if (window.YT && window.YT.Player) {
        ytPlayers[index] = new YT.Player(`yt-player-${index}`, {
            height: '315',
            width: '100%',
            videoId: videoId,
            playerVars: { 'playsinline': 1 },
            events: {
                'onStateChange': (event) => onPlayerStateChange(event, index)
            }
        });
    } else {
        setTimeout(() => initYouTubePlayer(index), 500);
    }
}

function onPlayerStateChange(event, index) {
    if (event.data === YT.PlayerState.ENDED) {
        const btn = document.getElementById(`understoodBtn_${index}`);
        if (btn) {
            btn.disabled = false;
            btn.style.opacity = "1";
            btn.style.cursor = "pointer";
            btn.textContent = "✓ Tôi đã đọc và hiểu nội dung này";
        }
    }
}

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
            feedback.style.color = "#4ade80";
            feedback.textContent = "Chính xác! Bạn đã hoàn thành xuất sắc bài học này.";
            submitBtn.disabled = true;
            submitBtn.style.opacity = "0.5";
            understoodBtn.textContent = "✓ Đã hoàn thành bài học này";
        } else {
            feedback.style.color = "#ef4444";
            feedback.textContent = "✕ Chưa chính xác! Bạn cần xem lại video và nội dung phía trên. Nút xác nhận đã bị khóa lại.";
            
            setTimeout(() => {
                quizContainer.style.display = "none";
                understoodBtn.disabled = true;
                understoodBtn.style.opacity = "0.5";
                understoodBtn.style.cursor = "not-allowed";
                understoodBtn.textContent = "🔒 Xem lại hết video để mở khóa lại nút này";
                understoodBtn.scrollIntoView({ behavior: 'smooth' });
                
                if (ytPlayers[idx] && typeof ytPlayers[idx].seekTo === 'function') {
                    ytPlayers[idx].seekTo(0);
                    ytPlayers[idx].pauseVideo();
                }
            }, 3000);
        }
    });
}

const sendQueryBtn = document.getElementById("sendQueryBtn");
if (sendQueryBtn) {
    sendQueryBtn.addEventListener("click", async function() {
        const input = document.getElementById("userQuery");
        if (!input) return;
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
}

function addChatMessage(sender, text) {
    const chatBox = document.getElementById("chatBox");
    if (!chatBox) return;
    const msgDiv = document.createElement("div");
    msgDiv.style.marginBottom = "8px";
    msgDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

initLearningPage();
