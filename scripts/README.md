# Scripts de Extração e Administração

Esta pasta contém scripts utilitários do ecossistema ALUMED OS / Conecta FCM.

## 🕷️ Scraping da Biblioteca Wix

| Script | Descrição |
|---|---|
| `extrair_biblioteca.py` | **Principal** — Extrai links de PDFs/arquivos da biblioteca Wix via Playwright |
| `crawl_wix.py` | Exploração inicial das pastas do Wix FileShare |
| `extract_all_wix_links.py` | Extração recursiva com integração ao model `DigitalBook` |
| `debug_playwright.py` | Debug de seletores e estrutura DOM do Wix |
| `apply_wix_links_to_db.py` | Aplica o `links_biblioteca.json` nos registros do banco |
| `download_key_pdfs.py` | Baixa os PDFs mais importantes para armazenamento local |

## 📚 Banco de Dados e Ingestão

| Script | Descrição |
|---|---|
| `populate_all_medicina.py` | Popula a tabela `DigitalBook` com o catálogo de Medicina |
| `ingest_academic_base.py` | Ingere a base acadêmica (cursos, matérias, anos) no banco |

## ▶️ Como rodar o script principal

```bash
# 1. Instalar dependências
pip install playwright
playwright install chromium

# 2. Rodar a extração
python scripts/extrair_biblioteca.py
```

O resultado será salvo em `scripts/links_biblioteca.json`.
