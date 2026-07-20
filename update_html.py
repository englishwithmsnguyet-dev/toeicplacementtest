import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the test-container structure
new_test_container = """
        <div class="test-container">
            <!-- Left Content Area (PDF Viewer) -->
            <main class="main-content glass-panel split-left">
                <!-- Home Section -->
                <div id="home-section" class="content-section active">
                    <div class="home-content">
                        <h2>Hướng Dẫn Thi Thử TOEIC</h2>
                        <div class="instructions-card" style="padding-bottom: 10px;">
                            <h3 style="font-size: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; margin-bottom: 15px;">Cấu trúc bài thi TOEIC</h3>
                            <p style="margin-bottom: 20px;">Bài thi TOEIC Placement Test mô phỏng kì thi thực tế, gồm 2 kỹ năng chính với tổng cộng 200 câu hỏi, thời gian làm bài 120 phút.</p>
                            
                            <div class="skill-detail" style="margin-bottom: 25px;">
                                <h4 style="color: #3b82f6; margin-bottom: 12px; font-size: 17px;">1. LISTENING TEST (Nghe hiểu) - 100 câu / 45 phút</h4>
                                <ul style="list-style-type: none; margin-left: 0;">
                                    <li style="margin-bottom: 8px;"><strong>Part 1: Photographs (Mô tả tranh) - 6 câu:</strong> Bạn sẽ xem 6 bức tranh, nghe 4 câu mô tả (A,B,C,D) và chọn câu mô tả chính xác nhất.</li>
                                    <li style="margin-bottom: 8px;"><strong>Part 2: Question-Response (Hỏi & Đáp) - 25 câu:</strong> Bạn sẽ nghe một câu hỏi, theo sau là 3 câu trả lời (A,B,C). Chọn câu trả lời phù hợp nhất.</li>
                                    <li style="margin-bottom: 8px;"><strong>Part 3: Conversations (Đoạn hội thoại) - 39 câu:</strong> Bạn sẽ nghe các đoạn hội thoại ngắn giữa 2-3 người. Mỗi đoạn có 3 câu hỏi đi kèm.</li>
                                    <li style="margin-bottom: 8px;"><strong>Part 4: Talks (Bài nói ngắn) - 30 câu:</strong> Bạn sẽ nghe các bài nói chuyện ngắn độc thoại (thông báo, tin tức...). Mỗi bài nói có 3 câu hỏi đi kèm.</li>
                                </ul>
                            </div>

                            <div class="skill-detail" style="margin-bottom: 10px;">
                                <h4 style="color: #8b5cf6; margin-bottom: 12px; font-size: 17px;">2. READING TEST (Đọc hiểu) - 100 câu / 75 phút</h4>
                                <ul style="list-style-type: none; margin-left: 0;">
                                    <li style="margin-bottom: 8px;"><strong>Part 5: Incomplete Sentences (Hoàn câu) - 30 câu:</strong> Chọn từ/cụm từ (A,B,C,D) phù hợp.</li>
                                    <li style="margin-bottom: 8px;"><strong>Part 6: Text Completion (Điền đoạn văn) - 16 câu:</strong> Điền từ/câu vào đoạn văn.</li>
                                    <li style="margin-bottom: 8px;"><strong>Part 7: Reading Comprehension (Đọc hiểu) - 54 câu:</strong> Đọc đoạn đơn, đoạn kép, đoạn ba.</li>
                                </ul>
                            </div>
                        </div>
                        <button class="btn btn-primary" onclick="startTest()">Vào Làm Bài</button>
                    </div>
                </div>

                <!-- PDF Viewer Section -->
                <div id="pdf-section" class="content-section">
                    <object data="data/pdf/test_01_full.pdf#toolbar=0&navpanes=0&scrollbar=1" type="application/pdf" width="100%" height="100%">
                        <p>Trình duyệt của bạn không hỗ trợ xem PDF trực tiếp. <a href="data/pdf/test_01_full.pdf">Tải xuống PDF</a>.</p>
                    </object>
                </div>
            </main>

            <!-- Right Answer Sheet Sidebar (Bubble Sheet) -->
            <aside class="right-sidebar glass-panel split-right">
                <div class="sidebar-header">
                    <h3>Phiếu Trả Lời</h3>
                </div>
                
                <div id="audio-container" class="audio-panel">
                    <div class="audio-controls">
                        <audio id="main-audio" controls controlsList="nodownload">
                            <!-- Try exact filename or just placeholder -->
                            <source src="Audio/Final%20Thay%20Dinh%20Van%20LISTENING%20ETS%202026%20.mp3" type="audio/mpeg">
                            <source src="media/LISTENING TEST 01.mp3" type="audio/mpeg">
                        </audio>
                        <div id="audio-overlay" class="audio-overlay hidden">
                            <p>Audio đã kết thúc.</p>
                        </div>
                    </div>
                </div>

                <div class="bubble-sheet-container" id="bubble-sheet">
                    <!-- Bubbles injected here -->
                </div>
            </aside>
        </div>"""

pattern = r'<div class="test-container">.*?</div>\s*<!-- Result Modal -->'
# Note: we need a careful regex or string replacement.
start_idx = html.find('<div class="test-container">')
end_idx = html.find('<!-- Result Modal -->')

new_html = html[:start_idx] + new_test_container + '\n\n    ' + html[end_idx:]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
