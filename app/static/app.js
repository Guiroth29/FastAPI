const state = {
  page: 1,
  pageSize: 10,
  totalPages: 1,
  search: "",
};

const els = {
  healthApp: document.getElementById("health-app"),
  healthDb: document.getElementById("health-db"),
  feedback: document.getElementById("feedback"),
  tableWrap: document.getElementById("table-wrap"),
  pageLabel: document.getElementById("page-label"),
  searchInput: document.getElementById("search-input"),
  form: document.getElementById("book-form"),
  btnHealth: document.getElementById("btn-health"),
  btnSearch: document.getElementById("btn-search"),
  btnClear: document.getElementById("btn-clear"),
  btnPrev: document.getElementById("btn-prev"),
  btnNext: document.getElementById("btn-next"),
};

function setFeedback(message, kind = "good") {
  els.feedback.textContent = message;
  els.feedback.className = `feedback ${kind}`;
}

async function request(path, options = {}) {
  const response = await fetch(path, options);
  if (response.status === 204) {
    return null;
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail || `Erro HTTP ${response.status}`;
    throw new Error(detail);
  }

  return payload;
}

function renderTable(books) {
  if (!books.length) {
    els.tableWrap.innerHTML = '<p style="margin:14px">Nenhum livro encontrado.</p>';
    return;
  }

  const rows = books
    .map((book) => {
      const createdAt = new Date(book.createdAt).toLocaleString("pt-BR");
      return `
        <tr>
          <td>${book.title}</td>
          <td>${book.author}</td>
          <td>${book.isbn}</td>
          <td>${book.pages ?? "-"}</td>
          <td>${book.published_year ?? "-"}</td>
          <td>${createdAt}</td>
        </tr>
      `;
    })
    .join("");

  els.tableWrap.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>TÍTULO</th>
          <th>AUTOR</th>
          <th>ISBN</th>
          <th>PÁGINAS</th>
          <th>ANO</th>
          <th>CRIADO EM</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function updatePagination() {
  els.pageLabel.textContent = `Página ${state.page} de ${state.totalPages}`;
  els.btnPrev.disabled = state.page <= 1;
  els.btnNext.disabled = state.page >= state.totalPages;
}

async function loadHealth() {
  try {
    const data = await request("/health");
    els.healthApp.textContent = data.status;
    els.healthDb.textContent = data.database;
    const kind = data.database === "connected" ? "good" : "warn";
    setFeedback(`Health check: app=${data.status}, db=${data.database}`, kind);
  } catch (error) {
    els.healthApp.textContent = "error";
    els.healthDb.textContent = "error";
    setFeedback(error.message, "warn");
  }
}

async function loadBooks(page = 1) {
  state.page = page;
  const params = new URLSearchParams({
    page: String(state.page),
    page_size: String(state.pageSize),
  });

  let path = `/books/?${params.toString()}`;
  if (state.search) {
    params.set("q", state.search);
    path = `/books/search?${params.toString()}`;
  }

  try {
    const data = await request(path);
    state.page = data.currentPage;
    state.totalPages = data.totalPages || 1;
    renderTable(data.data || []);
    updatePagination();
  } catch (error) {
    renderTable([]);
    setFeedback(error.message, "warn");
  }
}

function formToPayload(form) {
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  if (!payload.description) {
    delete payload.description;
  }

  if (payload.pages) {
    payload.pages = Number(payload.pages);
  } else {
    delete payload.pages;
  }

  if (payload.published_year) {
    payload.published_year = Number(payload.published_year);
  } else {
    delete payload.published_year;
  }

  return payload;
}

async function createBook(event) {
  event.preventDefault();
  const payload = formToPayload(els.form);

  try {
    await request("/books/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    els.form.reset();
    setFeedback("Livro criado com sucesso.", "good");
    await loadBooks(1);
    await loadHealth();
  } catch (error) {
    setFeedback(error.message, "warn");
  }
}

function bindEvents() {
  els.btnHealth.addEventListener("click", loadHealth);

  els.form.addEventListener("submit", createBook);

  els.btnSearch.addEventListener("click", () => {
    state.search = els.searchInput.value.trim();
    loadBooks(1);
  });

  els.btnClear.addEventListener("click", () => {
    els.searchInput.value = "";
    state.search = "";
    loadBooks(1);
  });

  els.btnPrev.addEventListener("click", () => {
    if (state.page > 1) {
      loadBooks(state.page - 1);
    }
  });

  els.btnNext.addEventListener("click", () => {
    if (state.page < state.totalPages) {
      loadBooks(state.page + 1);
    }
  });
}

async function init() {
  bindEvents();
  await loadHealth();
  await loadBooks(1);
}

init();
