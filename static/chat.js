(() => {
  const theme = JSON.parse(document.getElementById("theme-data").textContent);
  const box = document.getElementById("messages");
  const form = document.getElementById("form");
  const input = document.getElementById("input");
  const chips = document.getElementById("chips");
  const learn = document.getElementById("learn");

  function addMessage(role, text, meta) {
    const wrap = document.createElement("div");
    wrap.className = "msg " + role;
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text;           // textContent: aman dari HTML injection
    wrap.appendChild(bubble);
    if (meta) {
      const m = document.createElement("div");
      m.className = "meta";
      m.textContent = meta;
      wrap.appendChild(m);
    }
    box.appendChild(wrap);
    box.scrollTop = box.scrollHeight;
    return wrap;
  }

  async function loadHistory() {
    box.innerHTML = "";
    try {
      const rows = await (await fetch(`/api/history/${theme.id}`)).json();
      if (!rows.length) addMessage("bot", theme.greeting);
      else rows.forEach(r => addMessage(r.role, r.text));
    } catch {
      addMessage("bot", theme.greeting);
    }
  }

  async function explainText(message) {
    const res = await fetch("/api/explain", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ theme: theme.id, message }),
    });
    const data = await res.json();
    if (!data.candidates || !data.candidates.length) return "Tidak ada kata yang cocok dengan pattern mana pun.";
    const list = data.candidates.map(c => `${c.intent} (${c.score})`).join(", ");
    return `Kandidat: ${list}. Threshold: ${data.threshold}.`;
  }

  async function send(message) {
    message = message.trim();
    if (!message) return;
    addMessage("user", message);
    input.value = "";
    const typing = addMessage("bot", "Sedang mengetik...");
    typing.querySelector(".bubble").classList.add("typing");
    try {
      const res = await fetch("/api/chat", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ theme: theme.id, message }),
      });
      const data = await res.json();
      typing.remove();
      if (!res.ok) { addMessage("bot", data.error || "Terjadi kesalahan."); return; }
      let meta = "";
      if (learn.checked) meta = `Intent: ${data.intent}, skor ${data.score}. ` + await explainText(message);
      addMessage("bot", data.reply, meta);
    } catch {
      typing.remove();
      addMessage("bot", "Koneksi ke server gagal. Coba kirim ulang.");
    }
  }

  theme.suggestions.forEach(text => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.textContent = text;
    b.addEventListener("click", () => send(text));
    chips.appendChild(b);
  });
  form.addEventListener("submit", e => { e.preventDefault(); send(input.value); });
  document.getElementById("clear").addEventListener("click", async () => {
    if (!confirm("Hapus semua riwayat chat ini?")) return;
    await fetch(`/api/history/${theme.id}`, { method: "DELETE" });
    loadHistory();
  });
  loadHistory();
  input.focus();
})();