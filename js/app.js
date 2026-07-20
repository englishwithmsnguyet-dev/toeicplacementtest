
// State Management
const state = {
    studentName: '',
    answers: {},
    timeLeft: 120 * 60, // 120 minutes in seconds
    timerInterval: null,
    testData: null,
    isReviewMode: false,
    testMode: null // "listening", "reading", or "full"
};

// DOM Elements
const loginScreen = document.getElementById('login-screen');
const testScreen = document.getElementById('test-screen');
const loginForm = document.getElementById('login-form');
const displayName = document.getElementById('display-name');
const timerDisplay = document.getElementById('timer');
const btnSubmit = document.getElementById('btn-submit-test');
const resultModal = document.getElementById('result-modal');

const audio = document.getElementById('main-audio');
const audioOverlay = document.getElementById('audio-overlay');

// Initialize Application
function init() {
    if (window.TEST_DATA) {
        state.testData = window.TEST_DATA;
        console.log('Test data loaded:', state.testData);
    } else {
        alert("Error loading test data. Please check data/test01.js");
    }

    // Event Listeners
    loginForm.addEventListener('submit', handleLogin);
    
    btnSubmit.addEventListener('click', () => {
        if (!state.isReviewMode && confirm('Bạn có chắc chắn muốn nộp bài?')) {
            submitTest();
        }
    });

    // Audio setup
    const btnPlayAudio = document.getElementById('btn-play-audio');
    if (audio && btnPlayAudio) {
        btnPlayAudio.addEventListener('click', () => {
            audio.play().then(() => {
                btnPlayAudio.style.backgroundColor = '#10b981';
                btnPlayAudio.innerText = '🔊 Đang phát Audio...';
                btnPlayAudio.style.pointerEvents = 'none'; // Disable clicking again
            }).catch(e => {
                console.error("Audio playback failed:", e);
                alert("Không thể phát Audio. Vui lòng kiểm tra lại file âm thanh.");
            });
        });
        
        audio.addEventListener('ended', () => {
            btnPlayAudio.style.display = 'none';
            audioOverlay.classList.remove('hidden');
        });
    }
}

function handleLogin(e) {
    e.preventDefault();
    const nameInput = document.getElementById('fullName').value.trim();
    if (nameInput) {
        state.studentName = nameInput;
        displayName.textContent = state.studentName;
        loginScreen.classList.remove('active');
        testScreen.classList.add('active');
        
        // Ghi nhận giờ đăng nhập
        sendToGoogleForm(state.studentName, 'Bắt đầu truy cập');
    }
}


window.startTest = function(mode) {
    state.testMode = mode;
    document.getElementById('home-section').classList.remove('active');
    document.getElementById('pdf-section').classList.add('active');
    document.querySelector('.split-right').style.display = 'flex'; // Hiển thị phiếu trả lời
    document.getElementById('header-timer').style.display = 'block'; // Hiển thị đồng hồ
    document.getElementById('header-submit').style.display = 'block'; // Hiển thị nút nộp bài
    
    // Hide tabs if not full test
    const tabs = document.querySelector('.test-tabs');
    if (mode === 'full') {
        tabs.style.display = 'flex';
        state.timeLeft = 120 * 60;
    } else if (mode === 'listening') {
        tabs.style.display = 'none';
        state.timeLeft = 45 * 60;
    } else if (mode === 'reading') {
        tabs.style.display = 'none';
        state.timeLeft = 75 * 60;
    }
    
    renderBubbleSheet(mode);
    startTimer();
    
    // Audio is no longer auto-played here. User must click the button.
};
function startTimer() {
    state.timerInterval = setInterval(() => {
        state.timeLeft--;
        
        if (state.timeLeft <= 0) {
            clearInterval(state.timerInterval);
            timerDisplay.textContent = "00:00:00";
            alert("Đã hết thời gian làm bài. Hệ thống sẽ tự động nộp bài.");
            submitTest();
            return;
        }

        const hours = Math.floor(state.timeLeft / 3600);
        const minutes = Math.floor((state.timeLeft % 3600) / 60);
        const seconds = state.timeLeft % 60;

        timerDisplay.textContent = 
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
        if (state.timeLeft <= 300) { // 5 minutes warning
            timerDisplay.classList.add('warning');
        }
    }, 1000);
}


function renderBubbleSheet(mode) {
    const container = document.getElementById('bubble-sheet');
    if (!state.testData || !state.testData.questions) return;
    
    let html = '';
    
    const parts = [
        {name: "Part 1 (Nghe)", start: 1, end: 6, type: "listening"},
        {name: "Part 2 (Nghe)", start: 7, end: 31, options: ['A','B','C'], type: "listening"},
        {name: "Part 3 (Nghe)", start: 32, end: 70, type: "listening"},
        {name: "Part 4 (Nghe)", start: 71, end: 100, type: "listening"},
        {name: "Part 5 (Đọc)", start: 101, end: 130, type: "reading"},
        {name: "Part 6 (Đọc)", start: 131, end: 146, type: "reading"},
        {name: "Part 7 (Đọc)", start: 147, end: 200, type: "reading"}
    ];
    
    parts.forEach(part => {
        // If mode is specific, only render that mode's parts
        if (mode !== 'full' && part.type !== mode) return;
        
        html += `<div class="bubble-group ${part.type}-group">
                    <div class="bubble-group-title">${part.name}</div>`;
                    
        for (let i = part.start; i <= part.end; i++) {
            const opts = part.options || ['A','B','C','D'];
            html += `<div class="bubble-row">
                        <div class="bubble-qnum">${i}.</div>
                        <div class="bubble-options">`;
            opts.forEach(opt => {
                const isSelected = state.answers[i] === opt;
                html += `<div class="bubble-circle ${isSelected ? 'selected' : ''}" 
                              id="bubble-${i}-${opt}"
                              onclick="selectBubble(${i}, '${opt}')">${opt}</div>`;
            });
            html += `   </div>
                     </div>`;
        }
        html += `</div>`;
    });
    
    container.innerHTML = html;
    
    // Set initial section
    if (mode === 'full' || mode === 'listening') {
        switchSection('listening');
    } else {
        switchSection('reading');
    }
}
window.switchSection = function(type) {
    // 1. Update Tabs
    document.getElementById('tab-listening').classList.remove('active');
    document.getElementById('tab-reading').classList.remove('active');
    document.getElementById(`tab-${type}`).classList.add('active');
    
    // 2. Update PDF Object (recreate to force browser reload after display:none)
    // Use setTimeout to ensure the DOM has applied display: flex before injecting <object>
    setTimeout(() => {
        const pdfContainer = document.getElementById('pdf-viewer-container');
        if (pdfContainer) {
            pdfContainer.innerHTML = `
                <object id="pdf-object" data="data/pdf/${type}_test_01.pdf#toolbar=0&navpanes=0&scrollbar=1" type="application/pdf" width="100%" height="100%">
                    <p>Trình duyệt của bạn không hỗ trợ xem PDF trực tiếp. <a href="data/pdf/${type}_test_01.pdf">Tải xuống PDF</a>.</p>
                </object>
            `;
        }
    }, 50);

    // 3. Show/Hide Bubble Groups
    const lGroups = document.querySelectorAll('.listening-group');
    const rGroups = document.querySelectorAll('.reading-group');
    const audioPanel = document.getElementById('audio-container');
    
    if (type === 'listening') {
        lGroups.forEach(g => g.classList.remove('hidden'));
        rGroups.forEach(g => g.classList.add('hidden'));
        if (audioPanel) audioPanel.style.display = 'block';
    } else {
        lGroups.forEach(g => g.classList.add('hidden'));
        rGroups.forEach(g => g.classList.remove('hidden'));
        if (audioPanel) audioPanel.style.display = 'none';
    }
};

window.selectBubble = function(qId, option) {
    if (state.isReviewMode) return; 
    state.answers[qId] = option;
    
    const opts = ['A','B','C','D'];
    opts.forEach(opt => {
        const el = document.getElementById(`bubble-${qId}-${opt}`);
        if (el) {
            if (opt === option) el.classList.add('selected');
            else el.classList.remove('selected');
        }
    });
    
    const answered = Object.keys(state.answers).length;
    const totalQ = state.testMode === "full" ? 200 : 100;
    btnSubmit.innerText = `Nộp Bài (${answered}/${totalQ})`;
};

function submitTest() {
    clearInterval(state.timerInterval);
    const results = calculateScore();
    
    // Ghi nhận giờ thoát và nộp bài
    const scoreStr = `L: ${results.listeningScore}, R: ${results.readingScore}, T: ${results.totalScore}`;
    sendToGoogleForm(state.studentName, `Nộp bài thi (${state.testMode}) - Điểm: ${scoreStr}`);
    
    showResults(results);
}

// Google Form Tracking
function sendToGoogleForm(name, actionStr) {
    const formUrl = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSfXI3rXcFfqeFEVAARVM2mphJchll9KEcN4CiFTFzHhZQUmPw/formResponse";
    const formData = new FormData();
    const timeStr = new Date().toLocaleTimeString('vi-VN');
    formData.append("entry.388968236", `${name} - ${actionStr} [${timeStr}]`);
    
    fetch(formUrl, {
        method: "POST",
        mode: "no-cors",
        body: formData
    }).catch(e => console.error("Lỗi gửi dữ liệu Google Form:", e));
}



// Initialize the app
init();


function calculateScore() {
    let listeningCorrect = 0;
    let readingCorrect = 0;
    const questions = state.testData.questions;

    questions.forEach(q => {
        // Only count if answer exists
        if (state.answers[q.id] && state.answers[q.id] === q.answer) {
            if (q.id <= 100) listeningCorrect++;
            else readingCorrect++;
        }
    });

    const lScore = state.testMode === 'reading' ? 0 : convertListeningScore(listeningCorrect);
    const rScore = state.testMode === 'listening' ? 0 : convertReadingScore(readingCorrect);
    
    return {
        listeningCorrect, readingCorrect,
        listeningScore: lScore, readingScore: rScore,
        totalScore: lScore + rScore
    };
}

function convertListeningScore(correct) {
    if (correct <= 6) return 5;
    if (correct >= 93) return 495;
    return Math.floor(correct * 495 / 100 / 5) * 5; // Simplified conversion
}

function convertReadingScore(correct) {
    if (correct <= 9) return 5;
    if (correct >= 97) return 495;
    return Math.floor(correct * 495 / 100 / 5) * 5; // Simplified conversion
}

function showResults(results) {
    document.getElementById('res-student-name').textContent = state.studentName;
    
    const lBox = document.getElementById('res-l-correct').parentElement.parentElement;
    const rBox = document.getElementById('res-r-correct').parentElement.parentElement;
    const totalBox = document.getElementById('res-total').parentElement;
    
    if (state.testMode === 'listening') {
        lBox.style.display = 'block';
        rBox.style.display = 'none';
        totalBox.style.display = 'none';
    } else if (state.testMode === 'reading') {
        lBox.style.display = 'none';
        rBox.style.display = 'block';
        totalBox.style.display = 'none';
    } else {
        lBox.style.display = 'block';
        rBox.style.display = 'block';
        totalBox.style.display = 'block';
    }

    document.getElementById('res-l-correct').textContent = `${results.listeningCorrect}/100`;
    document.getElementById('res-l-score').textContent = results.listeningScore;
    document.getElementById('res-r-correct').textContent = `${results.readingCorrect}/100`;
    document.getElementById('res-r-score').textContent = results.readingScore;
    document.getElementById('res-total').textContent = results.totalScore;
    
    resultModal.classList.add('active');
}
document.getElementById('btn-review-test').addEventListener('click', reviewTest);
document.getElementById('btn-restart').addEventListener('click', () => location.reload()); // Thi lại thì tải lại trang là hợp lý để reset triệt để
document.getElementById('btn-go-home').addEventListener('click', goHome);

function goHome() {
    // 1. Hide Result Modal
    resultModal.classList.remove('active');
    
    // 2. Reset State
    state.answers = {};
    state.isReviewMode = false;
    state.testMode = null;
    clearInterval(state.timerInterval);
    
    // 3. Reset Audio
    if (audio) {
        audio.pause();
        audio.currentTime = 0;
        audio.load();
        const btnPlayAudio = document.getElementById('btn-play-audio');
        if (btnPlayAudio) {
            btnPlayAudio.style.display = 'inline-block';
            btnPlayAudio.style.backgroundColor = '#3b82f6';
            btnPlayAudio.innerText = '▶ BẤM ĐỂ NGHE AUDIO';
            btnPlayAudio.style.pointerEvents = 'auto';
        }
        audioOverlay.classList.add('hidden');
    }
    
    // 4. Reset UI visibility
    document.querySelector('.split-right').style.display = 'none';
    document.getElementById('header-timer').style.display = 'none';
    document.getElementById('header-submit').style.display = 'none';
    document.getElementById('pdf-section').classList.remove('active');
    document.getElementById('home-section').classList.add('active');
    
    // Clear the PDF container to ensure it unloads properly
    const pdfContainer = document.getElementById('pdf-viewer-container');
    if (pdfContainer) pdfContainer.innerHTML = '';
    
    // 5. Reset Bubble Sheet text
    btnSubmit.innerText = 'Nộp Bài';
    btnSubmit.style.display = 'block';
}

function reviewTest() {
    state.isReviewMode = true;
    resultModal.classList.remove('active');
    btnSubmit.style.display = 'none';
    
    const questions = state.testData.questions;
    questions.forEach(q => {
        const userAns = state.answers[q.id];
        const correctAns = q.answer;
        
        const opts = ['A','B','C','D'];
        opts.forEach(opt => {
            const el = document.getElementById(`bubble-${q.id}-${opt}`);
            if (el) {
                if (opt === correctAns) {
                    el.style.backgroundColor = '#10b981'; // Green
                    el.style.color = '#fff';
                    el.style.borderColor = '#10b981';
                } else if (opt === userAns && userAns !== correctAns) {
                    el.style.backgroundColor = '#ef4444'; // Red
                    el.style.color = '#fff';
                    el.style.borderColor = '#ef4444';
                }
            }
        });
    });
}

