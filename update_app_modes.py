import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Add testMode to state
if 'testMode: null' not in js:
    js = js.replace('isReviewMode: false', 'isReviewMode: false,\n    testMode: null // "listening", "reading", or "full"')

# Replace startTest
new_startTest = """
window.startTest = function(mode) {
    state.testMode = mode;
    document.getElementById('home-section').classList.remove('active');
    document.getElementById('pdf-section').classList.add('active');
    
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
    
    // Play audio when test starts (if listening is involved)
    if (audio && (mode === 'full' || mode === 'listening')) {
        audio.play().catch(e => console.log("Auto-play blocked by browser, user needs to click play"));
    }
};
"""
js = re.sub(r'window\.startTest = function\(\) \{[\s\S]*?(?=function startTimer)', new_startTest, js)

# Replace renderBubbleSheet
new_renderBubbleSheet = """
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
"""
js = re.sub(r'function renderBubbleSheet\(\) \{[\s\S]*?(?=window\.switchSection = function)', new_renderBubbleSheet, js)

# Replace selectBubble update text
js = re.sub(r'btnSubmit\.innerText = `Nộp Bài \(\$\{answered\}/200\)`;', 'const totalQ = state.testMode === "full" ? 200 : 100;\n    btnSubmit.innerText = `Nộp Bài (${answered}/${totalQ})`;', js)

# Replace calculateScore and showResults
new_score_logic = """
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
"""
js = re.sub(r'function calculateScore\(\) \{[\s\S]*?(?=document\.getElementById\(\'btn-review-test\'\))', new_score_logic, js)


with open('js/app.js', 'w', encoding='utf-8') as f:
    f.write(js)
