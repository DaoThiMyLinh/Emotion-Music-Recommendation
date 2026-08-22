# 📚 KỊCH BẢN BÁO CÁO DỰ ÁN KLTN: HỆ THỐNG GỢI Ý NHẠC DỰA TRÊN CẢM XÚC KHUÔN MẶT (Emotion-Music-Recommendation)

## 1. TỔNG QUAN DỰ ÁN (Mục tiêu)
- **Vấn đề giải quyết:** Âm nhạc có ảnh hưởng lớn đến tâm lý con người. Thay vì người dùng phải tự tìm kiếm bài hát theo tâm trạng một cách thủ công, hệ thống này ra đời để **tự động hóa hoàn toàn** trải nghiệm đó.
- **Sản phẩm:** Một Web Application có khả năng thu nhận hình ảnh từ Webcam, dùng Trí tuệ nhân tạo (AI) để phân tích cảm xúc khuôn mặt theo thời gian thực (Real-time), từ đó tự động gợi ý và phát trực tiếp các bản nhạc phù hợp với tâm trạng đó.

## 2. CÔNG NGHỆ SỬ DỤNG (Tech Stack)
Dự án được chia làm 3 mảng chính:
- **Backend (Máy chủ xử lý):** Sử dụng **Python (Flask)**. Flask đóng vai trò làm Server để quản lý routing, nhận luồng video và trả về dữ liệu web.
- **AI / Computer Vision:** 
  - **OpenCV:** Nhận diện khuôn mặt (Face Detection) bằng thuật toán Haar Cascade.
  - **TensorFlow & Keras:** Xây dựng mạng nơ-ron tích chập (CNN - Convolutional Neural Network) để phân loại 7 cảm xúc cơ bản: *Angry, Disgusted, Fearful, Happy, Neutral, Sad, Surprised*.
- **Frontend (Giao diện người dùng):** 
  - Sử dụng **HTML5, CSS3, Vanilla JavaScript**.
  - Tích hợp các thư viện bên thứ 3: `Chart.js` (vẽ biểu đồ cảm xúc), `html2pdf.js` (xuất báo cáo), `canvas-confetti` (hiệu ứng hình ảnh).

## 3. LUỒNG HOẠT ĐỘNG CHÍNH (Workflow)
Khi người dùng mở trang web, quá trình sẽ diễn ra theo 4 bước tuần hoàn:
1. **Thu thập dữ liệu:** Trình duyệt gửi luồng video từ Webcam người dùng về Server thông qua đường dẫn `/video_feed`.
2. **Tiền xử lý & Nhận diện (`camera.py`):** 
   - OpenCV cắt (crop) khuôn mặt ra khỏi khung hình và chuyển về ảnh xám (Grayscale).
   - Mô hình Keras (`model.keras` hoặc `model.h5`) sẽ dự đoán xem khuôn mặt đó đang ở cảm xúc nào.
3. **Gợi ý Âm nhạc:** Dựa trên cảm xúc nhận được, hệ thống sẽ ánh xạ (map) vào bộ dữ liệu bài hát (V-Pop, US-UK, Lofi) để lấy ra một danh sách (playlist) tương ứng.
4. **Phản hồi giao diện (`index.html`):** 
   - Server gửi JSON chứa danh sách bài hát và cảm xúc hiện tại qua API `/t`.
   - Frontend thay đổi màu nền, hiển thị biểu đồ, phát hiệu ứng (Mưa, Pháo hoa,...) và tự động cập nhật danh sách bài hát lên màn hình để người dùng có thể bấm phát nhạc trực tiếp (Mini Player).

## 4. CÁC ĐIỂM SÁNG / TÍNH NĂNG NỔI BẬT (Dùng để "Ghi điểm" với Hội đồng)
Khi báo cáo, bạn hãy đặc biệt nhấn mạnh vào 4 tính năng tân tiến này vì nó làm đồ án khác biệt so với các bài tập lớn thông thường:

- 🎵 **Trình phát nhạc tích hợp (Mini Player):** Không cần mở tab mới hay Spotify. Hệ thống tự động truy xuất ID YouTube ngầm (thông qua `urllib` và regex) và phát trực tiếp bài hát ngay góc màn hình bằng Iframe của YouTube.
- 🗣️ **Trợ lý ảo AI & Ra lệnh giọng nói (Voice Command):** 
  - **Text-to-Speech:** Ứng dụng tự động cất tiếng nói chào hỏi khi nhận diện được khuôn mặt quen thuộc, hoặc đưa ra lời khuyên tâm lý khi người dùng buồn.
  - **Speech-to-Text:** Tích hợp `SpeechRecognition API` cho phép người dùng bấm nút Micro và nói *"Đổi sang nhạc Lofi"*, *"Khóa màn hình"*, *"Dừng"*,... để điều khiển hệ thống mà không cần chạm chuột.
- 📊 **Phân tích Tâm lý & Xuất Báo cáo PDF (Insight Report):** Hệ thống không chỉ gợi ý nhạc mà còn lưu lại toàn bộ lịch sử cảm xúc trong phiên sử dụng (Emotion Diary). Người dùng có thể xuất file Báo cáo PDF. Trong file đó sẽ có một mục **AI Insight** tự động tính toán % căng thẳng/vui vẻ để đưa ra lời khuyên (ví dụ: Khuyên dùng Pomodoro nếu stress quá 30%).
- ✨ **Giao diện tương tác Động (Dynamic UI):** Giao diện liên tục thay đổi màu sắc theo cảm xúc (Dark/Glassmorphism). Cùng với đó là các hiệu ứng thị giác (Mưa rơi khi buồn, Pháo hoa khi vui, Chớp đỏ khi giận dữ) mang lại trải nghiệm tương tác liền mạch và ấn tượng.

## 5. TÓM TẮT CHỨC NĂNG CỦA CÁC FILE CHÍNH
- `app.py`: File khởi chạy Server Flask, chứa các Endpoints/API (như `/video_feed`, `/api/get_youtube_id`, `/toggle_freeze`).
- `camera.py`: Trái tim của AI. File này load Model CNN, đọc camera, nhận diện khuôn mặt, trả về khung hình đã vẽ bounding box và xử lý logic gán nhạc cho từng cảm xúc.
- `index.html`: Giao diện chính của toàn bộ ứng dụng, nơi chứa HTML layout, logic UI, Voice Command, biểu đồ Chart.js và giao tiếp với Backend qua kĩ thuật Polling liên tục (hàm `tick()`).
- `style.css`: File định hình phong cách thiết kế, quản lý màu sắc động và các keyframe animation (Mưa, Rung lắc, Hiệu ứng chớp đỏ,...).

---
**💡 Mẹo khi báo cáo:**
Hội đồng thường sẽ xoáy vào câu hỏi về **độ chính xác của mô hình** và **cách AI liên kết với bài hát**. Bạn hãy tự tin trình bày:
> *"Mô hình CNN của tụi em được huấn luyện trên bộ dữ liệu chuẩn (như FER2013) để trích xuất xác suất cảm xúc. Tuy nhiên, điểm mạnh và tâm huyết nhất của đồ án này là việc vận dụng và tối ưu hóa **Trải nghiệm người dùng (UX)** ở mảng Frontend. Nhóm đã biến kết quả thô của AI thành các tính năng hữu ích thực tế và trực quan như điều khiển bằng giọng nói, tự động xuất báo cáo tâm lý và thay đổi không gian âm nhạc theo thời gian thực."*
