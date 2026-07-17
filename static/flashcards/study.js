document.addEventListener("DOMContentLoaded", () => {
  const cardWrapper = document.getElementById("flashcard-wrapper");
  const reviewPanel = document.getElementById("review-panel");
  const explainPanel = document.getElementById("explain-panel");
  const cardsDataEl = document.getElementById("cards-data");
  
  if (!cardsDataEl) return;

  const cards = JSON.parse(cardsDataEl.textContent);
  let currentIndex = 0;
  let responseStartTime = Date.now();
  let isFlipped = false;

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken');

  function loadCard(index) {
    if (index >= cards.length) {
      // Sessão concluída!
      showSessionFinished();
      return;
    }

    const card = cards[index];
    isFlipped = false;
    cardWrapper.classList.remove("flipped");
    reviewPanel.style.display = "none";
    explainPanel.style.display = "none";

    // Preenche a frente e o verso
    document.getElementById("card-front-text").textContent = card.question;
    document.getElementById("card-back-text").textContent = card.answer;
    document.getElementById("card-explanation-text").textContent = card.explanation || "No hay explicación adicional cargada para esta ficha.";
    
    // Atualiza badges
    document.getElementById("card-subject").textContent = card.deck_subject || "General";
    document.getElementById("card-index").textContent = `Ficha ${index + 1} de ${cards.length}`;

    // Configura botões de IA
    const askJoyBtn = document.getElementById("ask-profe-joy-btn");
    if (askJoyBtn) {
      askJoyBtn.onclick = () => {
        // Redireciona para o chat RAG passando dados do card como parâmetro de contexto
        const msg = encodeURIComponent(`Hola Profe Joy, no entendí bien esta pregunta de ${card.deck_subject}: "${card.question}". La respuesta es "${card.answer}" y la explicación dice "${card.explanation || ''}". ¿Me lo podrías explicar mejor?`);
        window.location.href = `/profe-joy/chat/?msg=${msg}`;
      };
    }

    responseStartTime = Date.now();
  }

  // Evento de Virada (Flip)
  cardWrapper.addEventListener("click", () => {
    if (!isFlipped) {
      isFlipped = true;
      cardWrapper.classList.add("flipped");
      reviewPanel.style.display = "block";
      explainPanel.style.display = "block";
    } else {
      isFlipped = false;
      cardWrapper.classList.remove("flipped");
    }
  });

  // Evento dos Botões de Revisão
  const buttons = document.querySelectorAll(".btn-quality");
  buttons.forEach(button => {
    button.addEventListener("click", async (e) => {
      e.stopPropagation(); // Evita virar o card novamente
      
      const quality = parseInt(button.getAttribute("data-quality"));
      const responseTime = (Date.now() - responseStartTime) / 1000.0;
      const wasCorrect = quality >= 3;
      const card = cards[currentIndex];

      // Desabilita botões temporariamente
      buttons.forEach(b => b.disabled = true);

      try {
        const response = await fetch(`/api/flashcards/${card.id}/review/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
          },
          body: JSON.stringify({
            was_correct: wasCorrect,
            response_time_seconds: responseTime,
            confidence: quality
          })
        });

        if (response.ok) {
          const result = await response.json();
          // Efeito visual rápido de transição
          currentIndex++;
          loadCard(currentIndex);
        } else {
          alert("Error al registrar la revisión.");
        }
      } catch (err) {
        console.error(err);
        alert("Error de conexión.");
      } finally {
        buttons.forEach(b => b.disabled = false);
      }
    });
  });

  function showSessionFinished() {
    document.getElementById("study-card-container").style.display = "none";
    document.getElementById("session-finished-container").style.display = "block";
  }

  // Inicializa o primeiro card
  if (cards.length > 0) {
    loadCard(0);
  } else {
    showSessionFinished();
  }
});
