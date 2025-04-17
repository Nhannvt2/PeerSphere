document.addEventListener("DOMContentLoaded", function() {
    let currentQuestion = 0;
    let answers = {};
    let questions = [];
  
    // Lấy dữ liệu câu hỏi từ API
    async function loadQuestions() {
      try {
        const response = await fetch("/api/questions");
        if (!response.ok) throw new Error("Không thể tải câu hỏi từ server");
        let data = await response.json();
        
        // Nếu data trả về dạng object, chuyển đổi thành mảng
        if (!Array.isArray(data)) {
          data = Object.keys(data)
                       .sort((a, b) => a - b)
                       .map(key => data[key]);
        }
        questions = data;
        showQuestion();
      } catch (error) {
        document.getElementById("quiz-container").innerHTML = `<p class="error">Lỗi: ${error.message}</p>`;
      }
    }
  
    // Hàm hiển thị câu hỏi hiện tại
    function showQuestion() {
      // Nếu hết câu hỏi, hiển thị nút nộp bài
      if (currentQuestion >= questions.length) {
        document.getElementById("quiz-container").innerHTML = `
          <h2>Hoàn thành!</h2>
          <button class="btn-submit" onclick="submitQuiz()">Nộp bài</button>
        `;
        return;
      }
  
      const q = questions[currentQuestion];
      // Dùng q.id nếu có, nếu không dùng currentQuestion
      const questionId = q.id || currentQuestion;
      const optionsHTML = Object.entries(q.options).map(([key, value]) => {
        const isChecked = answers[questionId] === key ? 'checked' : '';
        return `
          <label class="option-label">
            <input type="radio" name="answer" value="${key}" ${isChecked}>
            ${key}: ${value}
          </label><br>
        `;
      }).join('');
  
      const questionHTML = `
        <h3 class="question-title">Câu ${currentQuestion + 1}: ${q.question}</h3>
        <div class="options-container">
          ${optionsHTML}
        </div>
        <div class="nav-buttons">
          ${currentQuestion > 0 ? '<button class="btn-nav" onclick="prevQuestion()">Trước</button>' : ''}
          <button class="btn-nav" onclick="nextQuestion()">${currentQuestion === questions.length - 1 ? "Nộp bài" : "Tiếp theo"}</button>
        </div>
      `;
      document.getElementById("quiz-container").innerHTML = questionHTML;
    }
  
    // Chuyển sang câu hỏi trước
    window.prevQuestion = function() {
      if (currentQuestion > 0) {
        currentQuestion--;
        showQuestion();
      }
    };
  
    // Xử lý khi chuyển câu hỏi
    window.nextQuestion = function() {
      const selected = document.querySelector("input[name='answer']:checked");
      if (!selected) {
        alert("Vui lòng chọn câu trả lời!");
        return;
      }
      const questionId = questions[currentQuestion].id || currentQuestion;
      answers[questionId] = selected.value;
      currentQuestion++;
      showQuestion();
    };
  
    // Hàm gửi bài làm đến endpoint submit
    window.submitQuiz = async function() {
      try {
        const payload = {
          answers: Object.entries(answers).map(([id, answer]) => ({
            question_id: parseInt(id),
            answer: answer
          }))
        };
        const response = await fetch("/api/submit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error("Nộp bài không thành công");
        const result = await response.json();
        window.location.href = `/result?score=${result.total_score}&assessment=${encodeURIComponent(result.assessment)}`;
      } catch (error) {
        alert("Lỗi khi nộp bài: " + error.message);
      }
    };
  
    loadQuestions();
  });
  