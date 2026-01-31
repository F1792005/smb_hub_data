// --- CẤU HÌNH API ---
const API_BASE_URL = "http://localhost:8000"; // Địa chỉ của Backend FastAPI

// --- CÁC HÀM TƯƠNG TÁC ---

// 1. Hàm lấy thống kê Dashboard
async function fetchStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        const data = await response.json();
        
        // Cập nhật giao diện
        document.getElementById('total-files').textContent = data.total_files;
        document.getElementById('clean-rate').textContent = data.clean_rate + "%";
    } catch (error) {
        console.error("Lỗi lấy stats:", error);
        alert("Không kết nối được với Backend API!");
    }
}

// 2. Hàm upload file
async function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const statusText = document.getElementById('upload-status');
    
    if (fileInput.files.length === 0) {
        alert("Vui lòng chọn file trước!");
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);
    
    statusText.textContent = "⏳ Đang upload...";
    statusText.style.color = "blue";
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: "POST",
            body: formData
        });
        const result = await response.json();
        
        statusText.textContent = "✅ " + result.status;
        statusText.style.color = "green";
        fileInput.value = ""; // Xóa input
    } catch (error) {
        console.error("Lỗi upload:", error);
        statusText.textContent = "❌ Upload thất bại!";
        statusText.style.color = "red";
    }
}

// 3. Hàm Chat với AI
async function sendMessage() {
    const inputField = document.getElementById('user-input');
    const question = inputField.value.trim();
    if (!question) return;
    
    // Hiển thị câu hỏi của User
    addMessageToChat(question, 'user');
    inputField.value = "";
    
    // Hiển thị trạng thái "Đang nhập..." của Bot
    const loadingId = addMessageToChat("...", 'bot', true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: question })
        });
        const data = await response.json();
        
        // Xóa trạng thái loading và hiện câu trả lời thật
        document.getElementById(loadingId).remove();
        addMessageToChat(data.answer, 'bot');
        
    } catch (error) {
        document.getElementById(loadingId).remove();
        addMessageToChat("❌ Lỗi kết nối với AI.", 'bot');
    }
}

// Hàm phụ trợ: Thêm tin nhắn vào khung chat
function addMessageToChat(text, sender, isLoading=false) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;
    if (isLoading) msgDiv.id = "loading-msg";
    
    const icon = sender === 'bot' ? 'fa-robot' : 'fa-user';
    
    msgDiv.innerHTML = `
        <div class="avatar"><i class="fas ${icon}"></i></div>
        <div class="content">${text.replace(/\n/g, '<br>')}</div>
    `;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Tự cuộn xuống cuối
    return msgDiv.id;
}

// --- SỰ KIỆN KHI TRANG LOAD XONG ---
document.addEventListener('DOMContentLoaded', () => {
    // Gọi thống kê lần đầu
    fetchStats();
    
    // Gắn sự kiện cho các nút
    document.getElementById('refresh-btn').addEventListener('click', fetchStats);
    document.getElementById('upload-btn').addEventListener('click', uploadFile);
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    document.getElementById('user-input').addEventListener('keypress', (e) => {
        if(e.key === 'Enter') sendMessage();
    });
});