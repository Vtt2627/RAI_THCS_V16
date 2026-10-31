const GAS_URL = "https://script.google.com/macros/s/AKfycbzAf8smk-nTrzTGmwtU7z6EHKh3qCcPjH-4BLkE5NIFwRCZrwtcIivY-HAzdLXVRAUV/exec";
const STORAGE_KEY = "aiResponsibleResult";

let currentQuestion = 0;
let answers = [];
let assignedCode = null;
let hasSubmitted = false;
let selectedQuestions = [];

const BEHAVIOR_ORDER = [
    "HV01", "HV02", "HV03", "HV04", "HV05", "HV06", "HV07", "HV08", "HV09"
];

const startButton = document.getElementById("startButton");
const quiz = document.getElementById("quiz");
const startSection = document.getElementById("startSection");
const nextButton = document.getElementById("nextButton");
const result = document.getElementById("result");
const scoreResult = document.getElementById("scoreResult");
const attentionResult = document.getElementById("attentionResult");
const recommendationResult = document.getElementById("recommendationResult");
const studentCodeDisplay = document.getElementById("studentCodeDisplay");

// Hàm lấy mã học sinh từ Google Apps Script có xử lý dự phòng
function requestStudentCode(retries = 3, delay = 2000) {
    if (!studentCodeDisplay) return;
    studentCodeDisplay.textContent = "Đang cấp mã học sinh...";
    if (startButton) startButton.disabled = true;

    function attempt(n) {
        fetch(GAS_URL + "?action=getCode", { method: "GET" })
            .then(res => res.json())
            .then(data => {
                if (!data || !data.code) throw new Error("Không nhận được mã hợp lệ");
                assignedCode = data.code;
                studentCodeDisplay.textContent = assignedCode;
                if (startButton) startButton.disabled = false;
            })
            .catch(err => {
                console.warn(`Thử cấp mã thất bại (Còn ${n - 1} lần thử):`, err);
                if (n > 1) {
                    setTimeout(() => attempt(n - 1), delay + Math.random() * 1000);
                } else {
                    // Tạo mã dự phòng dựa trên thời gian nếu GAS không phản hồi
                    assignedCode = "HS_" + Math.floor(100000 + Math.random() * 900000);
                    studentCodeDisplay.textContent = assignedCode + " (Tự động)";
                    if (startButton) startButton.disabled = false;
                }
            });
    }
    attempt(retries);
}

if (startButton) {
    startButton.addEventListener("click", function () {
        if (!assignedCode) {
            alert("Hệ thống chưa thể cấp được mã học sinh. Vui lòng tải lại trang.");
            return;
        }
        selectedQuestions = selectedOneQuestionPerBehavior();
        currentQuestion = 0;
        answers = [];
        hasSubmitted = false;

        quiz.style.display = "block";
        startSection.style.display = "none";
        if (window.RaiBackground) window.RaiBackground.setWarning(false);
        showQuestion();
    });
}

function selectedOneQuestionPerBehavior() {
    const selected = [];
    BEHAVIOR_ORDER.forEach(behavior => {
        const candidates = questions.filter(q => q.behavior === behavior);
        if (candidates.length > 0) {
            const randomIndex = Math.floor(Math.random() * candidates.length);
            selected.push(candidates[randomIndex]);
        }
    });
    return selected;
}

function showQuestion() {
    const q = selectedQuestions[currentQuestion];
    document.getElementById("questionNumber").textContent = "Câu " + (currentQuestion + 1) + "/" + selectedQuestions.length;
    document.getElementById("questionText").textContent = q.question;
    nextButton.textContent = (currentQuestion === selectedQuestions.length - 1) ? "Nộp bài" : "Tiếp tục";
    nextButton.style.display = "inline-block";
    const options = document.getElementById("options");
    options.innerHTML = "";
    q.options.forEach((option, index) => {
        options.innerHTML += `<label><input type="radio" name="answer" value="${index}">${option}</label><br><br>`;
    });
}

if (nextButton) {
    nextButton.addEventListener("click", function () {
        const selected = document.querySelector('input[name="answer"]:checked');
        if (!selected) {
            alert("Vui lòng chọn một phương án.");
            return;
        }
        answers[currentQuestion] = Number(selected.value);
        currentQuestion++;
        if (currentQuestion < selectedQuestions.length) {
            showQuestion();
        } else {
            finishQuiz();
        }
    });
}

function calculateScore() {
    let totalScore = 0;
    for (let i = 0; i < selectedQuestions.length; i++) {
        if (answers[i] === selectedQuestions[i].answer) totalScore++;
    }
    return totalScore;
}

function analyzeBehaviors() {
    let behaviorResults = {};
    for (let i = 0; i < selectedQuestions.length; i++) {
        const behavior = selectedQuestions[i].behavior;
        behaviorResults[behavior] = (answers[i] === selectedQuestions[i].answer) ? 1 : 0;
    }
    return behaviorResults;
}

function getNeedAttention(behaviorResults) {
    let needAttention = [];
    for (const behavior in behaviorResults) {
        if (behaviorResults[behavior] === 0) needAttention.push(behavior);
    }
    return needAttention;
}

function getRecommendations(needAttention) {
    let resultArr = [];
    needAttention.forEach(behavior => {
        if (typeof recommendations !== "undefined" && recommendations[behavior]) {
            resultArr.push({ behavior: behavior, recommendation: recommendations[behavior] });
        }
    });
    return resultArr;
}

function saveResult(studentCode, score, average, behaviorResults, needAttention, resultRecommendations) {
    const selectedQuestionInfo = selectedQuestions.map(q => ({ id: q.id, behavior: q.behavior }));
    const resultData = {
        studentCode: studentCode,
        attempt: new Date().toLocaleString(),
        version: "V16",
        score: score,
        totalQuestions: selectedQuestions.length,
        average: average,
        answers: answers,
        selectedQuestions: selectedQuestionInfo,
        behaviorResults: behaviorResults,
        recommendations: resultRecommendations
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify([resultData]));
}

function sendResultToSheet(studentCode, score, average, needAttention, resultRecommendations) {
    let attentionText = Array.isArray(needAttention) ? needAttention.join(", ") : "";
    let recommendationsText = Array.isArray(resultRecommendations) ? resultRecommendations.map(item => `${item.behavior}: ${item.recommendation}`).join("\n") : "";
    let selectedQuestionsText = selectedQuestions.map(q => `${q.behavior}:${q.id}`).join("|");

    fetch(GAS_URL, {
        method: "POST",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: JSON.stringify({
            code: studentCode,
            score: score + "/" + selectedQuestions.length,
            average: average,
            needAttention: attentionText,
            recommendations: recommendationsText,
            selectedQuestions: selectedQuestionsText,
            version: "V16"
        })
    })
    .then(res => res.json())
    .then(data => console.log("Google Sheet:", data))
    .catch(err => console.error("Lỗi Google Sheet:", err));
}

function showResult(score, needAttention, resultRecommendations) {
    quiz.style.display = "none";
    result.style.display = "block";
    scoreResult.textContent = "Điểm của bạn: " + score + "/" + selectedQuestions.length;
    attentionResult.innerHTML = "";
    recommendationResult.innerHTML = "";

    if (needAttention.length === 0) {
        attentionResult.innerHTML = "<p>Chưa có nội dung cần chú ý trong các tình huống đánh giá.</p>";
    } else {
        needAttention.forEach(behavior => {
            const behaviorTitle = (typeof behaviors !== "undefined" && behaviors[behavior]) ? behaviors[behavior] : behavior;
            attentionResult.innerHTML += `<p>• ${behavior} — ${behaviorTitle}</p>`;
        });
    }
    resultRecommendations.forEach(item => {
        recommendationResult.innerHTML += `<p>• ${item.behavior}: ${item.recommendation}</p>`;
    });
    if (window.RaiBackground) window.RaiBackground.setWarning(score < selectedQuestions.length / 2);
}

// Hàm hoàn thành bài trắc nghiệm và gửi mảng câu sai chính xác lên FastAPI
function finishQuiz() {
    if (hasSubmitted) return;
    hasSubmitted = true;
    const score = calculateScore();
    const behaviorResults = analyzeBehaviors();
    const needAttention = getNeedAttention(behaviorResults); // Mảng các mã hành vi sai (ví dụ: ["HV03", "HV04"])
    const resultRecommendations = getRecommendations(needAttention);
    const average = Number(((score / selectedQuestions.length) * 10).toFixed(2));

    saveResult(assignedCode, score, average, behaviorResults, needAttention, resultRecommendations);
    sendResultToSheet(assignedCode, score, average, needAttention, resultRecommendations);
    showResult(score, needAttention, resultRecommendations);

    // Gửi danh sách câu sai lên FastAPI Backend và lưu kết quả chuyển sang learning.html
    fetch('/api/get-learning-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            studentCode: assignedCode,
            need_attention: needAttention
        })
    })
    .then(res => res.json())
    .then(data => {
        localStorage.setItem("learningData", JSON.stringify(data));
    })
    .catch(err => console.error("Lỗi gọi API Backend:", err));
}

// Chuyển hướng sang trang lộ trình học tập cá nhân hóa
const goToAgentBtn = document.getElementById("goToAgentBtn");
if (goToAgentBtn) {
    goToAgentBtn.addEventListener("click", function () {
        window.location.href = "learning.html";
    });
}

// Khởi chạy lấy mã học sinh khi vừa tải trang
requestStudentCode();