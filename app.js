/**
 * EXECUTIVE LEARN - INTERACTIVE UI MOCK
 * Multi-Agent Assistant (Giảng viên, Bạn học, LMG)
 * Executive Design System Implementation
 */

// ============================================================================
// 1. MOCK DATA: SLIDES BÀI GIẢNG (Track C · Mini Hackathon AI)
// ============================================================================
const SLIDES_DATA = [
  {
    id: 1,
    category: "MODULE 1 · BÀI TOÁN & PERSONA",
    title: "1. Chuẩn bị đội ngũ & Khung Canvas bài toán",
    subtitle: "Xác định rõ người dùng mục tiêu, nỗi đau thật và phân chia nhiệm vụ trong 47,5 giờ.",
    statusText: "Đã hoàn thành",
    statusClass: "completed",
    content: `
      <div class="slide-grid-2col">
        <div class="feature-box">
          <div class="feature-box-icon">🎯</div>
          <div class="feature-box-title">Định vị Persona & Nỗi đau thật</div>
          <div class="feature-box-desc">Học viên thường xuyên bị quá tải khi tự học tài liệu dài, thiếu người đố kiến thức và khó tự kiểm tra mức độ hiểu sâu của từng slide.</div>
        </div>
        <div class="feature-box">
          <div class="feature-box-icon">⚖️</div>
          <div class="feature-box-title">Mục tiêu Checkpoint CP1 & CP2</div>
          <div class="feature-box-desc">Hoàn thành Canvas 4 ô, chốt repo công khai và xây dựng bản Mockup tương tác chứng minh toàn bộ luồng trải nghiệm người dùng trước 21:00.</div>
        </div>
      </div>
      <div class="slide-highlight-banner">
        <div>💡</div>
        <div class="slide-highlight-text">
          <strong>Trọng tâm đánh giá:</strong> Đừng vội viết code phức tạp khi luồng sản phẩm chưa thông suốt. Bản mock bấm được giúp nhóm phát hiện lỗ hổng UX chỉ trong 10 phút.
        </div>
      </div>
    `,
    summaryPoints: [
      "Xác định học viên bận rộn cần tương tác hai chiều khi đọc slide.",
      "Chốt cam kết ít nhất 2 willing users ngay từ CP1.",
      "Mục tiêu luồng: Chuyển giao mượt mà giữa các tác tử hỗ trợ học tập."
    ]
  },
  {
    id: 2,
    category: "MODULE 2 · DỮ LIỆU THẬT & GOLDEN SET",
    title: "2. Thu thập dữ liệu thực tế & Xây dựng Golden Set",
    subtitle: "Khai thác gói vlearn-pack và discord-pack để đúc kết 30 câu hỏi chuẩn bị cho việc đo lường CP3.",
    statusText: "Đã hoàn thành",
    statusClass: "completed",
    content: `
      <div class="slide-grid-2col">
        <div class="feature-box">
          <div class="feature-box-icon">📊</div>
          <div class="feature-box-title">Phân tích Chatlog VLearn</div>
          <div class="feature-box-desc">Phát hiện 68% câu hỏi của người học xoay quanh việc cần giảng giải lại các công thức toán hoặc đề nghị cho ví dụ minh họa bằng code thực tế.</div>
        </div>
        <div class="feature-box">
          <div class="feature-box-icon">🧪</div>
          <div class="feature-box-title">Xây dựng 30 Case Golden Set</div>
          <div class="feature-box-desc">Thiết lập bộ dữ liệu chuẩn (input câu hỏi + output kỳ vọng) để làm thước đo định lượng tự động cho mốc CP3 (tỉ lệ chính xác đạt > 85%).</div>
        </div>
      </div>
      <div class="slide-highlight-banner">
        <div>🔍</div>
        <div class="slide-highlight-text">
          <strong>Nguyên tắc Mom Test:</strong> Không hỏi người dùng "Tính năng này có hay không?", hãy hỏi "Lần gần nhất bạn gặp bế tắc khi xem slide này là khi nào?".
        </div>
      </div>
    `,
    summaryPoints: [
      "Bộ dữ liệu golden set phản ánh đúng nhu cầu học tập thực tế.",
      "Tách bạch giữa việc hỏi lý thuyết (Giảng viên) và luyện phản xạ (Bạn học).",
      "Định chuẩn số liệu đo lường sẵn sàng cho CP3."
    ]
  },
  {
    id: 3,
    category: "MODULE 3 · THIẾT KẾ TRẢI NGHIỆM MULTI-AGENT",
    title: "3. Thiết kế luồng trải nghiệm & Tương tác Multi-Agent",
    subtitle: "Xây dựng kiến trúc hỗ trợ người học theo 3 vai trò: Giảng viên, Bạn học và Bộ sinh tài liệu (LMG).",
    statusText: "Đang học",
    statusClass: "active",
    content: `
      <div class="slide-grid-2col">
        <div class="feature-box">
          <div class="feature-box-icon">👨‍🏫</div>
          <div class="feature-box-title">Teaching Agent (Giảng viên AI)</div>
          <div class="feature-box-desc">Cắt nghĩa cặn kẽ từng luận điểm, cung cấp bài giảng mẫu và chủ động hỏi người dùng câu hỏi mở sâu sắc để khơi gợi tư duy phản biện.</div>
        </div>
        <div class="feature-box">
          <div class="feature-box-icon">🧑‍🎓</div>
          <div class="feature-box-title">Study Agent (Bạn học AI)</div>
          <div class="feature-box-desc">Đóng vai bạn đồng môn tích cực: liên tục đặt câu hỏi ngắn, đố vui ôn tập, phản hồi đánh giá câu trả lời của học viên tạo tâm lý hào hứng.</div>
        </div>
      </div>
      <div class="slide-highlight-banner">
        <div>⚡</div>
        <div class="slide-highlight-text">
          <strong>LMG (Learning Material Generator):</strong> Bộ máy trích xuất nội dung slide tự động biến kiến thức thành Quiz trắc nghiệm, Flashcard lật 2 mặt và Bản đồ tư duy Mindmap tức thì.
        </div>
      </div>
    `,
    summaryPoints: [
      "Chia tách rõ ràng 3 tác tử: Giảng viên (sâu sắc), Bạn học (tương tác đố), LMG (công cụ sinh tài liệu).",
      "Ngữ cảnh slide hiện tại (Active Slide Context) tự động được ghim vào prompt của mọi Agent.",
      "Đoạn giới thiệu vai trò biến mất ngay khi người dùng bắt đầu gửi tin nhắn hoặc chọn công cụ."
    ]
  },
  {
    id: 4,
    category: "MODULE 4 · PROTOTYPE & ĐO LƯỜNG ĐỊNH LƯỢNG",
    title: "4. Xây dựng Prototype AI thật & Đo lường định lượng",
    subtitle: "Mốc CP3: Quay video thao tác 30s + đo lường tỉ lệ thành công trên tập kiểm thử golden set.",
    statusText: "Tiếp theo",
    statusClass: "upcoming",
    content: `
      <div class="slide-grid-2col">
        <div class="feature-box">
          <div class="feature-box-icon">⏱️</div>
          <div class="feature-box-title">Video thao tác 30 giây</div>
          <div class="feature-box-desc">Ghi hình màn hình thật: người dùng chuyển slide, đổi agent, nhận câu trả lời thực tế từ LLM và sinh bộ câu hỏi Quiz mà không cần biên tập video.</div>
        </div>
        <div class="feature-box">
          <div class="feature-box-icon">📈</div>
          <div class="feature-box-title">Báo cáo số đo thực nghiệm</div>
          <div class="feature-box-desc">Đo độ trễ phản hồi (Latency < 2.5s) và tỉ lệ câu trả lời bám sát ngữ cảnh slide (Relevance Rate) đạt trên 90% qua 30 mẫu thử nghiệm.</div>
        </div>
      </div>
      <div class="slide-highlight-banner">
        <div>⚙️</div>
        <div class="slide-highlight-text">
          <strong>Lưu ý kỹ thuật:</strong> Áp dụng streaming response để người dùng không phải chờ đợi lâu, tăng cảm giác phản hồi tức thì của trợ lý AI.
        </div>
      </div>
    `,
    summaryPoints: [
      "Quay video mộc chứng minh AI thật đang chạy.",
      "Bảng số đo thực nghiệm là minh chứng thuyết phục nhất trong bài pitch.",
      "Tối ưu độ trễ với LLM tốc độ cao (Gemini 1.5 / 2.0 Flash)."
    ]
  },
  {
    id: 5,
    category: "MODULE 5 · AI SPEC & CHUẨN ĐẠT",
    title: "5. Hoàn thiện tài liệu AI Spec & Khóa chuẩn Đạt",
    subtitle: "Xác định rõ ràng biên độ hành vi AI, kịch bản xử lý khi gặp lỗi và cam kết an toàn kiến thức.",
    statusText: "Chờ học",
    statusClass: "upcoming",
    content: `
      <div class="slide-grid-2col">
        <div class="feature-box">
          <div class="feature-box-icon">📋</div>
          <div class="feature-box-title">Đặc tả hành vi (AI Spec)</div>
          <div class="feature-box-desc">Quy định chặt chẽ: Giảng viên chỉ trả lời trong phạm vi bài học; nếu học viên hỏi lan man ngoài lề, khéo léo dẫn dắt quay lại chủ đề chính.</div>
        </div>
        <div class="feature-box">
          <div class="feature-box-icon">🛡️</div>
          <div class="feature-box-title">Cơ chế Guardrails & Fallback</div>
          <div class="feature-box-desc">Khi độ tin cậy của mô hình thấp (Confidence < 0.7), tự động gợi ý người học tham khảo slide tài liệu gốc thay vì tạo ra kiến thức ảo (Hallucination).</div>
        </div>
      </div>
      <div class="slide-highlight-banner">
        <div>🔒</div>
        <div class="slide-highlight-text">
          <strong>Mốc CP4:</strong> Khóa chuẩn "Đạt" trước 21:00 ngày 17/9. Tự khai trung thực các điểm chưa hoàn thiện để ghi điểm tính minh bạch.
        </div>
      </div>
    `,
    summaryPoints: [
      "Tài liệu Spec chuẩn hóa cách ứng xử của từng Agent.",
      "Ngăn chặn hoàn toàn ảo giác kiến thức (Anti-hallucination RAG).",
      "Khai báo rõ các ràng buộc kỹ thuật."
    ]
  },
  {
    id: 6,
    category: "MODULE 6 · XÁC THỰC NGƯỜI DÙNG & PITCHING",
    title: "6. Xác thực người dùng ngoài nhóm & Thuyết trình chung cuộc",
    subtitle: "Kiểm chứng thực tế với ít nhất 2 willing users và chuẩn bị sẵn sàng cho vòng thi LAB 18/9.",
    statusText: "Chờ học",
    statusClass: "upcoming",
    content: `
      <div class="slide-grid-2col">
        <div class="feature-box">
          <div class="feature-box-icon">👥</div>
          <div class="feature-box-title">Thử nghiệm với Willing Users</div>
          <div class="feature-box-desc">Cho 2 người dùng thật thao tác tự do: bấm chuyển giữa Giảng viên, Bạn học và bấm sinh Quiz. Ghi nhận phản ứng chân thật nhất.</div>
        </div>
        <div class="feature-box">
          <div class="feature-box-icon">🏆</div>
          <div class="feature-box-title">Kịch bản Demo & Slide Pitch</div>
          <div class="feature-box-desc">Slide thuyết trình gọn gàng, video demo dự phòng sẵn sàng trong máy và làm nổi bật giá trị cá nhân hóa lộ trình học tập của sản phẩm.</div>
        </div>
      </div>
      <div class="slide-highlight-banner">
        <div>🎤</div>
        <div class="slide-highlight-text">
          <strong>Thời khắc chung kết:</strong> Tự tin trình bày luồng giá trị sản phẩm từ nỗi đau có thật đến giải pháp tương tác đa tác tử đột phá!
        </div>
      </div>
    `,
    summaryPoints: [
      "Bằng chứng kiểm chứng thực tế từ người dùng khách quan.",
      "Video demo dự phòng sẵn sàng đề phòng rủi ro mạng chập chờn.",
      "Chiến thắng nhờ tư duy sản phẩm AI sắc sảo."
    ]
  }
];

// ============================================================================
// 2. AGENTS CONFIGURATION & SYSTEM PROMPTS
// ============================================================================
const AGENTS_CONFIG = {
  teacher: {
    roleId: "teacher",
    name: "Giảng viên AI",
    enName: "Teaching Agent",
    icon: "👨‍🏫",
    themeClass: "theme-teacher",
    placeholder: "Hỏi giảng viên về nội dung slide này...",
    title: "Chào bạn, tôi là Giảng viên AI!",
    desc: "Tôi đồng hành giải thích cặn kẽ từng khái niệm trong slide, phân tích các ca sử dụng thực tế và sẵn sàng đặt câu hỏi kiểm tra độ hiểu bài của bạn.",
    quickPrompts: [
      "Giải thích ngắn gọn luận điểm chính của slide này?",
      "Tại sao việc phân tách vai trò Multi-Agent lại tối ưu hơn 1 bot?",
      "Thầy hãy hỏi em một câu hỏi mở để kiểm tra độ hiểu bài!"
    ]
  },
  study: {
    roleId: "study",
    name: "Bạn học AI",
    enName: "Study Peer Agent",
    icon: "🧑‍🎓",
    themeClass: "theme-study",
    placeholder: "Cùng ôn bài hoặc trả lời câu đố của bạn học...",
    title: "Chào bạn! Mình là Bạn học AI cùng tiến!",
    desc: "Mình sẽ đóng vai người bạn học cùng nhóm, liên tục đố vui và đặt ra các tình huống bài tập liên quan đến slide để tụi mình cùng thảo luận và nhớ lâu hơn.",
    quickPrompts: [
      "Đố mình một câu hỏi nhanh về nội dung slide này đi!",
      "Mình trả lời: Multi-Agent giúp giảm tải và chuyên môn hóa tác vụ, đúng không?",
      "Nếu người dùng hỏi ngoài phạm vi bài học thì tụi mình nên xử lý thế nào?"
    ]
  },
  lmg: {
    roleId: "lmg",
    name: "LMG Studio",
    enName: "Learning Material Generator",
    icon: "⚡",
    themeClass: "theme-lmg",
    placeholder: "Yêu cầu LMG tạo tài liệu trắc nghiệm, flashcard hoặc mindmap...",
    title: "Chào bạn! Tôi là Bộ sinh tài liệu (LMG)",
    desc: "Tôi tự động phân tích slide hiện tại để sinh tài liệu ôn tập thông minh: Quiz trắc nghiệm, Flashcard lật 2 mặt, Bản đồ tư duy Mindmap và Tóm tắt trọng tâm. Bấm công cụ bên dưới để tạo ngay:",
    studioTools: [
      { id: "quiz", icon: "📝", name: "Tạo Quiz trắc nghiệm", hint: "Kiểm tra kiến thức tức thì" },
      { id: "flashcard", icon: "🗂", name: "Tạo Flashcard", hint: "Thẻ lật 2 mặt ghi nhớ" },
      { id: "mindmap", icon: "🧠", name: "Bản đồ tư duy", hint: "Sơ đồ cây phân nhánh" },
      { id: "summary", icon: "📄", name: "Tóm tắt cốt lõi", hint: "Các ý chính quan trọng" }
    ]
  }
};

// ============================================================================
// 3. APPLICATION STATE
// ============================================================================
let currentSlideIndex = 2; // Mặc định ở Slide 3 (id: 3)
let currentAgent = "teacher"; // 'teacher' | 'study' | 'lmg'
let isDrawerOpen = true;
let zoomPercent = 100;

// Chat histories per agent to maintain independent conversations
const chatHistories = {
  teacher: [],
  study: [],
  lmg: []
};

// Flags to know if the intro banner was hidden per agent
const introDismissed = {
  teacher: false,
  study: false,
  lmg: false
};

// ============================================================================
// 4. DOM ELEMENTS
// ============================================================================
const slideListContainer = document.getElementById("slideListContainer");
const presentationCardBody = document.getElementById("presentationCardBody");
const slideMainTitle = document.getElementById("slideMainTitle");
const slideMainSubtitle = document.getElementById("slideMainSubtitle");
const slideCategoryText = document.getElementById("slideCategoryText");
const slideHeaderIndex = document.getElementById("slideHeaderIndex");
const slideBreadcrumb = document.getElementById("slideBreadcrumb");
const slideCounterText = document.getElementById("slideCounterText");
const prevSlideBtn = document.getElementById("prevSlideBtn");
const nextSlideBtn = document.getElementById("nextSlideBtn");
const topbarProgressBar = document.getElementById("topbarProgressBar");
const topbarProgressLabel = document.getElementById("topbarProgressLabel");

// Drawer & Agents Elements
const assistantDrawer = document.getElementById("assistantDrawer");
const toggleAiDrawerBtn = document.getElementById("toggleAiDrawerBtn");
const closeDrawerBtn = document.getElementById("closeDrawerBtn");
const resetChatBtn = document.getElementById("resetChatBtn");
const agentTabs = document.querySelectorAll(".agent-tab");
const contextSlideLabel = document.getElementById("contextSlideLabel");
const agentIntroBanner = document.getElementById("agentIntroBanner");
const introBadgeRole = document.getElementById("introBadgeRole");
const introTitle = document.getElementById("introTitle");
const introDesc = document.getElementById("introDesc");
const introActionsArea = document.getElementById("introActionsArea");
const chatStreamContainer = document.getElementById("chatStreamContainer");
const lmgInteractiveArea = document.getElementById("lmgInteractiveArea");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");

// Zoom controls
const btnZoomIn = document.getElementById("btnZoomIn");
const btnZoomOut = document.getElementById("btnZoomOut");
const zoomLevelText = document.getElementById("zoomLevel");
const presentationCard = document.getElementById("presentationCard");
const btnFullscreen = document.getElementById("btnFullscreen");

// ============================================================================
// 5. INITIALIZATION & RENDERING FUNCTIONS
// ============================================================================
function initApp() {
  renderSlideList();
  renderCurrentSlide();
  renderAgentView();
  bindEvents();
}

/**
 * Render Left Sidebar: Slide Navigation Items
 */
function renderSlideList() {
  slideListContainer.innerHTML = "";
  SLIDES_DATA.forEach((slide, idx) => {
    const isActive = idx === currentSlideIndex;
    const item = document.createElement("div");
    item.className = `slide-item ${isActive ? "active" : ""}`;
    item.dataset.index = idx;
    
    item.innerHTML = `
      <div class="slide-num-badge">${slide.id}</div>
      <div class="slide-item-content">
        <div class="slide-item-title">${slide.title}</div>
        <div class="slide-item-status">
          <span style="font-size: 8px;">●</span>
          <span>${slide.statusText}</span>
        </div>
      </div>
    `;

    item.addEventListener("click", () => {
      selectSlide(idx);
    });

    slideListContainer.appendChild(item);
  });
}

/**
 * Render Middle Slide Presentation Card
 */
function renderCurrentSlide() {
  const slide = SLIDES_DATA[currentSlideIndex];
  if (!slide) return;

  slideMainTitle.textContent = slide.title;
  slideMainSubtitle.textContent = slide.subtitle;
  slideCategoryText.textContent = slide.category;
  slideHeaderIndex.textContent = `0${slide.id}/0${SLIDES_DATA.length}`;
  slideBreadcrumb.textContent = `Khung bài giảng · ${slide.title}`;
  slideCounterText.textContent = `Slide ${slide.id} / ${SLIDES_DATA.length}`;
  presentationCardBody.innerHTML = slide.content;

  // Update progress bar
  const progressVal = Math.round(((currentSlideIndex + 1) / SLIDES_DATA.length) * 100);
  topbarProgressBar.style.width = `${progressVal}%`;
  topbarProgressLabel.textContent = `Tiến độ: ${currentSlideIndex + 1}/${SLIDES_DATA.length} bài`;

  // Update dock buttons state
  prevSlideBtn.disabled = currentSlideIndex === 0;
  nextSlideBtn.disabled = currentSlideIndex === SLIDES_DATA.length - 1;

  // Synchronize AI Drawer Context Tag
  contextSlideLabel.textContent = `Slide ${slide.id} · ${slide.title.split(". ")[1] || slide.title}`;

  // Update active status on left list
  const allItems = slideListContainer.querySelectorAll(".slide-item");
  allItems.forEach((el, idx) => {
    el.classList.toggle("active", idx === currentSlideIndex);
  });
}

/**
 * Handle Slide Selection
 */
function selectSlide(index) {
  if (index < 0 || index >= SLIDES_DATA.length) return;
  currentSlideIndex = index;
  renderCurrentSlide();

  // If AI drawer is open, add context update pill message
  if (isDrawerOpen) {
    const currentSlide = SLIDES_DATA[currentSlideIndex];
    if (chatHistories[currentAgent].length > 0) {
      appendSystemContextNote(`Đã đồng bộ ngữ cảnh mới: Slide ${currentSlide.id} - "${currentSlide.title}"`);
    }
  }
}

/**
 * Render Right AI Drawer based on Current Agent
 */
function renderAgentView() {
  const config = AGENTS_CONFIG[currentAgent];
  if (!config) return;

  // Update Agent Switcher Tabs Active State
  agentTabs.forEach(tab => {
    const isThisAgent = tab.dataset.agent === currentAgent;
    tab.classList.toggle("active", isThisAgent);
  });

  // Update input placeholder
  chatInput.placeholder = config.placeholder;

  // Check if intro banner should be shown
  if (!introDismissed[currentAgent] && chatHistories[currentAgent].length === 0) {
    agentIntroBanner.style.display = "block";
    agentIntroBanner.className = `agent-intro-banner ${config.themeClass}`;
    introBadgeRole.innerHTML = `<span>${config.icon}</span><span>${config.enName}</span>`;
    introTitle.textContent = config.title;
    introDesc.textContent = config.desc;

    // Render Quick Prompts or Studio Tools
    if (currentAgent === "lmg") {
      introActionsArea.innerHTML = `
        <div class="quick-prompts-title">Công cụ sinh tài liệu thông minh:</div>
        <div class="lmg-studio-grid" id="studioToolsGrid">
          ${config.studioTools.map(tool => `
            <div class="studio-action-tile" data-tool="${tool.id}">
              <div class="studio-tile-icon">${tool.icon}</div>
              <div class="studio-tile-name">${tool.name}</div>
              <div class="studio-tile-hint">${tool.hint}</div>
            </div>
          `).join("")}
        </div>
      `;
      // Bind studio tile clicks
      introActionsArea.querySelectorAll(".studio-action-tile").forEach(tile => {
        tile.addEventListener("click", () => {
          handleStudioToolClick(tile.dataset.tool);
        });
      });
    } else {
      introActionsArea.innerHTML = `
        <div class="quick-prompts-title">Gợi ý tương tác nhanh:</div>
        <div class="quick-prompts-wrap">
          ${config.quickPrompts.map(prompt => `
            <button class="prompt-pill-btn" data-prompt="${prompt}">
              <span>${prompt}</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          `).join("")}
        </div>
      `;
      // Bind prompt chip clicks
      introActionsArea.querySelectorAll(".prompt-pill-btn").forEach(btn => {
        btn.addEventListener("click", () => {
          const text = btn.dataset.prompt;
          sendUserMessage(text);
        });
      });
    }
  } else {
    // Hide intro banner
    agentIntroBanner.style.display = "none";
  }

  // Render chat messages for this agent
  renderChatMessages();
}

/**
 * Render Chat Messages for active agent
 */
function renderChatMessages() {
  chatStreamContainer.innerHTML = "";
  const history = chatHistories[currentAgent];

  history.forEach(msg => {
    const msgEl = document.createElement("div");
    msgEl.className = `chat-message ${msg.sender}`;

    if (msg.sender === "ai") {
      const config = AGENTS_CONFIG[currentAgent];
      msgEl.innerHTML = `
        <div class="ai-author-tag">
          <span>${config.icon}</span>
          <span>${config.name}</span>
        </div>
        <div class="message-bubble">${msg.text}</div>
      `;
    } else if (msg.sender === "system") {
      msgEl.className = "chat-message system";
      msgEl.innerHTML = `
        <div style="font-size: 11px; text-align: center; color: var(--slate-400); margin: 6px 0;">
          ${msg.text}
        </div>
      `;
    } else {
      msgEl.innerHTML = `
        <div class="message-bubble">${msg.text}</div>
      `;
    }

    chatStreamContainer.appendChild(msgEl);
  });

  scrollDrawerToBottom();
}

/**
 * Append System Notification
 */
function appendSystemContextNote(text) {
  chatHistories[currentAgent].push({ sender: "system", text });
  renderChatMessages();
}

/**
 * User sends message
 * "Mỗi khi bấm 1 agent sẽ có 1 đoạn chữ giới thiệu về AI (mất khi mình chat)."
 */
function sendUserMessage(text) {
  if (!text || text.trim() === "") return;
  const cleanText = text.trim();

  // 1. DISMISS INTRO BANNER IMMEDIATELY AS REQUESTED BY USER
  introDismissed[currentAgent] = true;
  agentIntroBanner.style.display = "none";

  // 2. Append User Message
  chatHistories[currentAgent].push({
    sender: "user",
    text: cleanText
  });
  renderChatMessages();
  chatInput.value = "";

  // 3. Show Typing Indicator
  showTypingIndicator();

  // 4. Generate Realistic Simulated AI Response based on Agent and Slide
  setTimeout(() => {
    removeTypingIndicator();
    const aiResponseText = generateAgentResponse(currentAgent, cleanText, SLIDES_DATA[currentSlideIndex]);
    chatHistories[currentAgent].push({
      sender: "ai",
      text: aiResponseText
    });
    renderChatMessages();
  }, 900);
}

/**
 * Show Typing Indicator
 */
function showTypingIndicator() {
  const existing = document.getElementById("typingIndicator");
  if (existing) return;

  const indicator = document.createElement("div");
  indicator.id = "typingIndicator";
  indicator.className = "chat-message ai";
  indicator.innerHTML = `
    <div class="ai-author-tag">
      <span>${AGENTS_CONFIG[currentAgent].icon}</span>
      <span>${AGENTS_CONFIG[currentAgent].name} đang trả lời...</span>
    </div>
    <div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>
  `;
  chatStreamContainer.appendChild(indicator);
  scrollDrawerToBottom();
}

function removeTypingIndicator() {
  const existing = document.getElementById("typingIndicator");
  if (existing) existing.remove();
}

/**
 * Scroll drawer to bottom smoothly
 */
function scrollDrawerToBottom() {
  const drawerBody = document.getElementById("drawerBody");
  drawerBody.scrollTop = drawerBody.scrollHeight;
}

// ============================================================================
// 6. SIMULATED AI RESPONSE GENERATOR (Teaching, Study, LMG)
// ============================================================================
function generateAgentResponse(agent, userQuery, slide) {
  const lower = userQuery.toLowerCase();

  // 1. TEACHING AGENT (Giảng viên)
  if (agent === "teacher") {
    if (lower.includes("giải thích") || lower.includes("ý nghĩa") || lower.includes("tổng quan")) {
      return `Chào bạn! Về <strong>Slide ${slide.id}: ${slide.title}</strong>:<br><br>
      Trọng tâm cốt lõi là: <em>${slide.subtitle}</em>.<br><br>
      Trong kiến trúc Mini Hackathon AI, việc nắm chắc luận điểm này giúp nhóm tránh được cái bẫy "làm tính năng thừa mà không ai dùng". Thay vì chỉ tập trung vào mô hình AI, bạn cần chứng minh được giá trị thực tế mang lại cho học viên.<br><br>
      ❓ <strong>Câu hỏi gợi mở cho bạn:</strong> Bạn đã xác định rõ nhóm mình sẽ đo lường mức độ thành công của tính năng này bằng chỉ số định lượng nào chưa?`;
    }
    if (lower.includes("tại sao") || lower.includes("multi-agent") || lower.includes("tối ưu")) {
      return `Một câu hỏi rất hay về mặt kiến trúc hệ thống!<br><br>
      Việc tách thành 3 Agent chuyên biệt (<strong>Giảng viên, Bạn học, LMG</strong>) mang lại 3 ưu thế vượt trội:<br>
      1. <strong>Chuyên biệt hóa System Prompt:</strong> Giảng viên cần phong thái uyên bác, giải thích sâu; Bạn học cần tính tương tác đố vui; LMG cần tuân thủ cấu trúc dữ liệu JSON để sinh card.<br>
      2. <strong>Giảm thiểu Token Pollution:</strong> Mỗi agent duy trì context ngắn gọn, không bị loãng ngữ cảnh.<br>
      3. <strong>Trải nghiệm người học đa chiều:</strong> Vừa được giải đáp, vừa được thử thách, lại vừa có sẵn công cụ sinh tài liệu ôn thi.`;
    }
    if (lower.includes("câu hỏi") || lower.includes("kiểm tra") || lower.includes("đố")) {
      return `Được rồi, tôi có một câu hỏi kiểm tra tư duy dành riêng cho bạn về <strong>${slide.title}</strong>:<br><br>
      <em>"Nếu trong quá trình học, học viên đưa ra một câu trả lời sai hoàn toàn so với kiến thức trong slide, bạn sẽ thiết kế cho Giảng viên AI phản hồi như thế nào để vừa sửa lỗi sai vừa không làm giảm động lực học tập của bạn ấy?"</em><br><br>
      Hãy gõ câu trả lời của bạn vào đây nhé!`;
    }
    // Generic teaching response
    return `Tôi ghi nhận câu hỏi của bạn: "<em>${userQuery}</em>".<br><br>
    Đối chiếu với nội dung <strong>Slide ${slide.id}</strong>, giải pháp tốt nhất là bám sát dữ liệu thực tế và kịch bản người dùng. Nhóm cần đảm bảo mọi phản hồi đều gắn liền với bài giảng hiện tại để tránh ảo giác kiến thức (hallucination). Bạn có muốn tôi làm rõ thêm phần nào không?`;
  }

  // 2. STUDY AGENT (Bạn học)
  if (agent === "study") {
    if (lower.includes("đố") || lower.includes("câu hỏi")) {
      return `Haha, chuẩn bị tinh thần nhận câu đố của mình nhé! 🎯<br><br>
      <strong>Đố bạn:</strong> Ở <strong>Slide ${slide.id}</strong>, điều gì được xem là "chỗ ăn điểm nặng nhất" theo đánh giá của các giám khảo?<br><br>
      A. Code thật nhiều dòng và thuật toán phức tạp<br>
      B. Khảo sát nỗi đau thật từ người dùng và chứng minh được luồng hoạt động thông suốt<br>
      C. Giao diện có thật nhiều nút bấm phức tạp<br><br>
      👉 Bạn chọn A, B hay C? Trả lời mình xem bạn nắm bài đến đâu nào!`;
    }
    if (lower.includes("b") || lower.includes("khảo sát") || lower.includes("đúng không")) {
      return `🎉 <strong>Chính xác 100%! Giỏi quá bạn ơi!</strong><br><br>
      Đáp án B hoàn toàn chuẩn xác. Giám khảo chấm rất nặng ở tiêu chí "Nỗi đau thật & Tư duy sản phẩm AI" chứ không chấm điểm số lượng dòng code.<br><br>
      Cậu nắm bài chắc đấy! Giờ tụi mình cùng thảo luận thêm một ca khó nhé: Nhóm cậu đã tìm được ít nhất 2 willing users để test thử chưa?`;
    }
    // Generic study peer response
    return `Ý kiến của cậu rất thú vị đấy! Mình thấy tụi mình đang có chung hướng đi. Ở <strong>Slide ${slide.id}</strong> này, mình nghĩ điểm mấu chốt là phải làm sao cho người học cảm thấy có người đồng hành cùng ôn tập thay vì chỉ đọc slide một mình.<br><br>
    Cậu có muốn mình đố thêm một câu trắc nghiệm nhanh nữa không?`;
  }

  // 3. LMG (Learning Material Generator)
  return `Tôi đã nhận lệnh từ bạn: "<em>${userQuery}</em>".<br><br>
  Đang phân tích cấu trúc <strong>${slide.title}</strong>... Bạn có thể bấm vào các nút công cụ Studio bên dưới (hoặc dùng các nút tạo Quiz, Flashcard, Mindmap) để tôi kết xuất dữ liệu trực quan ngay lập tức!`;
}

// ============================================================================
// 7. LMG STUDIO TOOLS INTERACTIVE GENERATOR
// ============================================================================
function handleStudioToolClick(toolType) {
  // Dismiss intro banner immediately
  introDismissed.lmg = true;
  agentIntroBanner.style.display = "none";

  const slide = SLIDES_DATA[currentSlideIndex];
  showTypingIndicator();

  setTimeout(() => {
    removeTypingIndicator();
    let cardHtml = "";

    if (toolType === "quiz") {
      cardHtml = `
        <div class="lmg-output-card">
          <div class="lmg-card-header">
            <span class="lmg-badge-tag">📝 BÀI KIỂM TRA NHANH (QUIZ)</span>
            <span style="font-size: 11px; color: var(--slate-400);">Gắn với Slide ${slide.id}</span>
          </div>
          <div class="quiz-question-title">
            Câu hỏi: Mục tiêu trọng tâm của "${slide.title}" trong lộ trình Mini Hackathon là gì?
          </div>
          <button class="quiz-option-btn" onclick="handleQuizAnswer(this, false)">
            A. Hoàn thiện toàn bộ mã nguồn backend không có lỗi
          </button>
          <button class="quiz-option-btn" onclick="handleQuizAnswer(this, true)">
            B. ${slide.summaryPoints[0]}
          </button>
          <button class="quiz-option-btn" onclick="handleQuizAnswer(this, false)">
            C. Bỏ qua bước kiểm thử và tiến hành thuyết trình trực tiếp
          </button>
          <div class="quiz-explanation" id="quizExp">
            ✅ <strong>Giải thích chính xác:</strong> Bám sát đúng mục tiêu của slide: <em>${slide.subtitle}</em>. Việc tập trung đúng vào trọng tâm này giúp sản phẩm đạt chuẩn chất lượng mốc CP2 & CP3.
          </div>
        </div>
      `;
    } else if (toolType === "flashcard") {
      cardHtml = `
        <div class="lmg-output-card">
          <div class="lmg-card-header">
            <span class="lmg-badge-tag">🗂 THẺ GHI NHỚ (FLASHCARD)</span>
            <span style="font-size: 11px; color: var(--slate-400);">Nhấp để lật 2 mặt</span>
          </div>
          <div class="flashcard-3d-wrap" onclick="this.querySelector('.flashcard-inner').classList.toggle('flipped')">
            <div class="flashcard-inner">
              <div class="flashcard-front">
                <div style="font-size: 11px; font-weight: 700; color: var(--agent-teacher-accent); margin-bottom: 6px;">MẶT CÂU HỎI</div>
                <div style="font-size: 14px; font-weight: 700;">Khái niệm cốt lõi của Slide ${slide.id}?</div>
                <div class="flashcard-hint-pill">👉 Nhấp thẻ để xem đáp án</div>
              </div>
              <div class="flashcard-back">
                <div style="font-size: 11px; font-weight: 700; color: var(--agent-study-accent); margin-bottom: 6px;">MẶT ĐÁP ÁN</div>
                <div style="font-size: 13px; font-weight: 600; line-height: 1.5;">${slide.summaryPoints[1] || slide.subtitle}</div>
                <div class="flashcard-hint-pill">✅ Đã thuộc bài</div>
              </div>
            </div>
          </div>
        </div>
      `;
    } else if (toolType === "mindmap") {
      cardHtml = `
        <div class="lmg-output-card">
          <div class="lmg-card-header">
            <span class="lmg-badge-tag">🧠 SƠ ĐỒ TƯ DUY (MINDMAP)</span>
            <span style="font-size: 11px; color: var(--slate-400);">Cấu trúc slide phân cấp</span>
          </div>
          <div class="mindmap-tree">
            <div class="mindmap-root-node">Slide ${slide.id}: ${slide.title.split(". ")[1] || slide.title}</div>
            <div class="mindmap-branches">
              <div class="mindmap-leaf">📌 Trọng tâm: ${slide.subtitle.slice(0, 48)}...</div>
              <div class="mindmap-leaf">⚙️ Ứng dụng: ${slide.summaryPoints[0]}</div>
              <div class="mindmap-leaf">🎯 Đầu ra: ${slide.summaryPoints[2] || "Đạt chuẩn nghiệm thu"}</div>
            </div>
          </div>
        </div>
      `;
    } else if (toolType === "summary") {
      cardHtml = `
        <div class="lmg-output-card">
          <div class="lmg-card-header">
            <span class="lmg-badge-tag">📄 TÓM TẮT TRỌNG TÂM (SUMMARY)</span>
            <span style="font-size: 11px; color: var(--slate-400);">3 điểm cần nhớ</span>
          </div>
          <ul style="padding-left: 18px; font-size: 13px; color: var(--slate-700); line-height: 1.6;">
            ${slide.summaryPoints.map(p => `<li>${p}</li>`).join("")}
          </ul>
        </div>
      `;
    }

    // Append generated card into chat stream
    chatHistories[currentAgent].push({
      sender: "ai",
      text: cardHtml
    });
    renderChatMessages();

  }, 600);
}

// Global quiz answer click handler
window.handleQuizAnswer = function(btn, isCorrect) {
  const parent = btn.closest(".lmg-output-card");
  const allBtns = parent.querySelectorAll(".quiz-option-btn");
  allBtns.forEach(b => {
    b.classList.add("answered");
    b.disabled = true;
  });

  if (isCorrect) {
    btn.classList.add("correct");
  } else {
    btn.classList.add("incorrect");
    // Also highlight correct answer
    allBtns.forEach(b => {
      if (b.getAttribute("onclick").includes("true")) {
        b.classList.add("correct");
      }
    });
  }

  const exp = parent.querySelector(".quiz-explanation");
  if (exp) exp.style.display = "block";
};

// ============================================================================
// 8. EVENT LISTENERS & UI CONTROLS
// ============================================================================
function bindEvents() {
  // Topbar Trợ lý AI toggle button
  toggleAiDrawerBtn.addEventListener("click", () => {
    isDrawerOpen = !isDrawerOpen;
    assistantDrawer.classList.toggle("collapsed", !isDrawerOpen);
    toggleAiDrawerBtn.classList.toggle("active-pulse", isDrawerOpen);
  });

  // Close drawer button inside header
  closeDrawerBtn.addEventListener("click", () => {
    isDrawerOpen = false;
    assistantDrawer.classList.add("collapsed");
    toggleAiDrawerBtn.classList.remove("active-pulse");
  });

  // Reset chat button
  resetChatBtn.addEventListener("click", () => {
    if (confirm("Bạn có muốn xóa cuộc trò chuyện hiện tại của Agent này và làm mới không?")) {
      chatHistories[currentAgent] = [];
      introDismissed[currentAgent] = false;
      renderAgentView();
    }
  });

  // Agent Tabs Switcher
  agentTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetAgent = tab.dataset.agent;
      if (targetAgent === currentAgent) return;
      currentAgent = targetAgent;
      renderAgentView();
    });
  });

  // Prev / Next slide dock buttons
  prevSlideBtn.addEventListener("click", () => {
    if (currentSlideIndex > 0) {
      selectSlide(currentSlideIndex - 1);
    }
  });

  nextSlideBtn.addEventListener("click", () => {
    if (currentSlideIndex < SLIDES_DATA.length - 1) {
      selectSlide(currentSlideIndex + 1);
    }
  });

  // Send message button & Enter key
  sendBtn.addEventListener("click", () => {
    sendUserMessage(chatInput.value);
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendUserMessage(chatInput.value);
    }
  });

  // Zoom controls
  btnZoomIn.addEventListener("click", () => {
    if (zoomPercent < 130) {
      zoomPercent += 10;
      applyZoom();
    }
  });

  btnZoomOut.addEventListener("click", () => {
    if (zoomPercent > 80) {
      zoomPercent -= 10;
      applyZoom();
    }
  });

  btnFullscreen.addEventListener("click", () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      if (document.exitFullscreen) document.exitFullscreen();
    }
  });

  // Submit lab button demo alert
  document.getElementById("submitLabBtn").addEventListener("click", () => {
    alert("🎉 Bạn đang ở bước kiểm thử CP2: 'Cho thấy luồng hoạt động — bấm thử được'.\n\nBạn có thể quay màn hình 30s thao tác chuyển slide, đổi 3 agent và sinh Quiz/Flashcard để nộp CP2!");
  });
}

function applyZoom() {
  zoomLevelText.textContent = `${zoomPercent}%`;
  presentationCard.style.transform = `scale(${zoomPercent / 100})`;
  presentationCard.style.transformOrigin = "top center";
}

// Start app on DOMContentLoaded
document.addEventListener("DOMContentLoaded", initApp);
