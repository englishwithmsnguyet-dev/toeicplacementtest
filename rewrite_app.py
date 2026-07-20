import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# We need to preserve calculateScore, showResults, reviewTest.
# They are generally at the end.
# Let's extract them.
score_idx = js.find('function calculateScore()')
if score_idx == -1:
    print("Could not find calculateScore")
    
preserved_logic = js[score_idx:]

new_js = """
// State Management
const state = {
    studentName: '',
    answers: {},
    timeLeft: 120 * 60, // 120 minutes in seconds
    timerInterval: null,
    testData: null,
    isReviewMode: false
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
    if (audio) {
        audio.addEventListener('ended', () => {
            audio.style.display = 'none';
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
    }
}

window.startTest = function() {
    document.getElementById('home-section').classList.remove('active');
    document.getElementById('pdf-section').classList.add('active');
    
    renderBubbleSheet();
    startTimer();
    
    // Play audio when test starts
    if (audio) {
        audio.play().catch(e => console.log("Auto-play blocked by browser, user needs to click play"));
    }
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

function renderBubbleSheet() {
    const container = document.getElementById('bubble-sheet');
    if (!state.testData || !state.testData.questions) return;
    
    let html = '';
    
    const parts = [
        {name: "Part 1 (Nghe)", start: 1, end: 6},
        {name: "Part 2 (Nghe)", start: 7, end: 31, options: ['A','B','C']},
        {name: "Part 3 (Nghe)", start: 32, end: 70},
        {name: "Part 4 (Nghe)", start: 71, end: 100},
        {name: "Part 5 (Đọc)", start: 101, end: 130},
        {name: "Part 6 (Đọc)", start: 131, end: 146},
        {name: "Part 7 (Đọc)", start: 147, end: 200}
    ];
    
    parts.forEach(part => {
        html += `<div class="bubble-group">
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
}

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
    btnSubmit.innerText = `Nộp Bài (${answered}/200)`;
};

function submitTest() {
    clearInterval(state.timerInterval);
    const results = calculateScore();
    showResults(results);
}
"""

new_js += "\n" + preserved_logic

# Fix reviewTest function because it used to navigate to the question in the left panel.
# Now review mode should just highlight the correct answers in the bubble sheet green, and wrong answers red.
review_override = """
function reviewTest() {
    state.isReviewMode = true;
    resultModal.classList.remove('active');
    btnSubmit.style.display = 'none';
    
    const questions = state.testData.questions;
    questions.forEach(q => {
        const userAns = state.answers[q.id];
        const correctAns = q.answer;
        
        // Highlight bubbles
        const opts = ['A','B','C','D'];
        opts.forEach(opt => {
            const el = document.getElementById(`bubble-${q.id}-${opt}`);
            if (el) {
                if (opt === correctAns) {
                    el.style.backgroundColor = '#10b981'; // Green for correct
                    el.style.color = '#fff';
                    el.style.borderColor = '#10b981';
                } else if (opt === userAns && userAns !== correctAns) {
                    el.style.backgroundColor = '#ef4444'; // Red for wrong
                    el.style.color = '#fff';
                    el.style.borderColor = '#ef4444';
                }
            }
        });
    });
}
"""

# Replace the old reviewTest
new_js = re.sub(r'function reviewTest\(\) \{[\s\S]*?(?=\n// Initialize)', review_override + '\n', new_js)

new_js += "\n// Initialize the app\ninit();\n"

with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(new_js)

print("Updated app.js successfully!")
