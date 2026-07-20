import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# We need to replace the navigation logic, startTest function, and renderQuestions function.

# 1. Provide startTest function and bubble sheet rendering
new_functions = """
// Expose startTest to global scope for the button
window.startTest = function() {
    document.getElementById('home-section').classList.remove('active');
    document.getElementById('pdf-section').classList.add('active');
    
    // Auto start audio if needed, or let user play it
    
    // Render Bubble Sheet
    renderBubbleSheet();
};

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
    if (state.isReviewMode) return; // Cannot change answers in review mode
    
    state.answers[qId] = option;
    
    // Update UI
    const opts = ['A','B','C','D'];
    opts.forEach(opt => {
        const el = document.getElementById(`bubble-${qId}-${opt}`);
        if (el) {
            if (opt === option) el.classList.add('selected');
            else el.classList.remove('selected');
        }
    });
    
    updateProgress();
};

function updateProgress() {
    const total = 200;
    const answered = Object.keys(state.answers).length;
    // We could show this somewhere, e.g. the submit button
    const btn = document.getElementById('btn-submit-test');
    if(btn) btn.innerText = `Nộp Bài (${answered}/${total})`;
}
"""

# Instead of complex regex replacing, let's just append the new functions at the end of the file
# and they will override the older navigation if they aren't used.
# But we need to make sure the old `renderQuestions` isn't called initially if it breaks things.
# Let's replace the whole file using a python script to ensure it's clean.

