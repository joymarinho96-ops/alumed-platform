# 📤 GUIA DE EXPORTAÇÃO - Alumed Pro

## 🎯 Para WebSketch

### Método 1: Upload Direto
1. Acesse WebSketch
2. Clique em "New Project"
3. Selecione "HTML Project"
4. Copie o conteúdo de `visualizador_pro.html`
5. Cole no editor
6. Salve e pronto!

### Método 2: Via Arquivo
1. Baixe o arquivo `visualizador_pro.html`
2. Vá para WebSketch > Import
3. Selecione o arquivo HTML
4. Aguarde processar

---

## 🌐 Para GitHub Pages

### Setup:
```bash
# 1. Crie um repo em github.com
# Nome: seu-usuario.github.io

# 2. Clone localmente
git clone https://github.com/seu-usuario/seu-usuario.github.io.git

# 3. Copie os arquivos
cp visualizador_pro.html seu-usuario.github.io/
cp -r imagens_laminas/ seu-usuario.github.io/

# 4. Commit e push
cd seu-usuario.github.io
git add .
git commit -m "Add Alumed Pro Histology Viewer"
git push origin main

# 5. Acesse em:
# https://seu-usuario.github.io/visualizador_pro.html
```

---

## 🚀 Para Netlify

### Setup Rápido:
1. Acesse [netlify.com](https://netlify.com)
2. Clique em "Drop files here"
3. Arraste a pasta `HHISTOLOGY`
4. Pronto! Recebe URL pública

### Setup com Git:
```bash
# 1. Instale Netlify CLI
npm install -g netlify-cli

# 2. Login
netlify login

# 3. Deploy
netlify deploy --prod --dir=.

# Acesse a URL gerada!
```

---

## 📦 Para Google Drive / Google Sites

### Opção 1: Embed HTML
1. Google Sites > Inserir > Incorporar
2. Cole o link do visualizador hospedado

### Opção 2: Link Compartilhável
1. Hospede em Netlify/GitHub Pages
2. Copie o link público
3. Compartilhe!

---

## 💾 Estrutura de Arquivos para Exportar

```
alumed-pro/
├── visualizador_pro.html      ✅ PRINCIPAL
├── index.html                  (opcional)
├── README.md                   (documentação)
├── project.json                (metadados)
└── imagens_laminas/
    └── lamina_amiguinho_hd.jpg (imagem)
```

---

## 🔗 Link para Compartilhar

**Opção 1: Copie este link**
```
http://localhost:5500/visualizador_pro.html
```
(Funciona apenas localmente com Live Server)

**Opção 2: Hospede e compartilhe**
```
https://seu-dominio.com/visualizador_pro.html
```

---

## ⚙️ Ajustes Finais

Antes de exportar, verifique:

- [ ] Imagem está carregando corretamente
- [ ] Botões de zoom funcionam
- [ ] Análise IA está ativa
- [ ] Sem erros no console (F12)
- [ ] Responsividade OK em telas diferentes

---

## 🚨 Troubleshooting

**"Imagem não carrega"**
- Verifique URL da imagem em `visualizador_pro.html`
- Mude para URL local se desejar: `imagens_laminas/lamina_amiguinho_hd.jpg`

**"Estilos quebrados"**
- Certifique que Tailwind CDN está ativo
- Verifique internet

**"Scripts não funcionam"**
- Abra F12 e veja console
- Verifique erros de JavaScript
- Limpe cache (Ctrl+Shift+Delete)

---

## 📊 Resumo Rápido

| Destino | Facilidade | Tempo | Custo |
|---------|-----------|-------|-------|
| WebSketch | ⭐⭐⭐⭐⭐ | 2 min | Grátis |
| GitHub Pages | ⭐⭐⭐⭐ | 5 min | Grátis |
| Netlify | ⭐⭐⭐⭐⭐ | 3 min | Grátis |
| Servidor Próprio | ⭐⭐⭐ | 15 min | 💰 |

---

## ✅ Checklist Pré-Exportação

- [ ] Testei no navegador
- [ ] Todos os links funcionam
- [ ] Imagem carrega OK
- [ ] Console sem erros
- [ ] README criado
- [ ] Files organizados
- [ ] Pronto para compartilhar!

---

**Agora é só compartilhar e aproveitar! 🚀🔬**
