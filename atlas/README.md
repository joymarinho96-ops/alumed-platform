# 🔬 Alumed Pro - Visualizador Histológico Inteligente

## 📊 Projeto de Histologia Digital com IA

Um visualizador web profissional de imagens histológicas em alta resolução com análise inteligente da Profe Joy!

---

## 🚀 Como Usar

### 1. **Arquivo Principal**
```
visualizador_pro.html
```
- Abra este arquivo no navegador para usar o visualizador
- Requer conexão com a internet (imagem vem do Wikimedia)

### 2. **Funcionalidades**
- ✅ Zoom infinito em imagem 4K
- ✅ Painel lateral com 7 estruturas anotadas
- ✅ Botão "🤖 Análise IA" (Profe Joy)
- ✅ Controles de zoom na tela
- ✅ Design responsivo e moderno

### 3. **Estruturas Incluídas**
1. Parede do Estômago (visão geral)
2. Mucosa (epitélio e glândulas)
3. Fossetas Gástricas
4. Glândulas Gástricas
5. Muscularis Mucosae
6. Submucosa
7. Muscularis Externa

---

## 🤖 Análise IA (Profe Joy)

Clique no botão **"🤖 Análise IA"** para receber análise automática baseada no nível de zoom:

- **Zoom Baixo (< 2x):** Análise panorâmica
- **Zoom Alto (> 2x):** Análise celular detalhada

---

## 📁 Arquivos do Projeto

### HTML
- `visualizador_pro.html` - Visualizador profissional (USE ESTE!)
- `index.html` - Versão original

### Python Scripts
- `scraper.py` - Coleta dados de uma lâmina
- `scraper_laminas.py` - Coleta múltiplas lâminas
- `baixar_laminas.py` - Download de imagens
- `montar_puzzle.py` - Monta tiles do Zoomify
- `upgrade_4k.py` - Upgrade de resolução

### Dados
- `laminas_banco_dados.json` - Base de dados de lâminas
- `imagens_laminas/` - Pasta com imagens baixadas

---

## 🌐 Hospedagem / WebSketch

### Opção 1: Local (Desenvolvimento)
```bash
# Já está rodando em:
http://localhost:5500/visualizador_pro.html
```

### Opção 2: GitHub Pages
1. Faça upload para um repositório GitHub
2. Ative GitHub Pages na aba Settings
3. Acesse: `https://seu-usuario.github.io/seu-repo/visualizador_pro.html`

### Opção 3: Netlify (Recomendado)
1. Faça login em netlify.com
2. Arraste a pasta do projeto
3. Pronto! Recebe uma URL pública

### Opção 4: WebSketch
- Se WebSketch suporta HTML5, você pode:
  1. Copiar o conteúdo do `visualizador_pro.html`
  2. Colar no editor do WebSketch
  3. Ajustar os paths das imagens

---

## 🔧 Customização

### Trocar Imagem
Edite a linha no `visualizador_pro.html`:
```javascript
url: 'https://upload.wikimedia.org/wikipedia/commons/e/e0/Gastric_mucosa_low_mag.jpg',
```

### Adicionar Novas Estruturas
No painel lateral, copie um botão e altere:
```html
<button class="structure-btn ..." onclick="focusStructure(X, Y, ZOOM)">
    <div class="flex justify-between items-center">
        <div>
            <div class="font-semibold">Seu Nome</div>
            <div class="text-xs text-gray-500">Descrição</div>
        </div>
        <span class="text-xs bg-gray-700 px-2 py-1">XXx</span>
    </div>
</button>
```

---

## 📱 Responsividade

- ✅ Desktop (recomendado)
- ✅ Tablet (bom)
- ⚠️ Mobile (limitado - tela pequena)

---

## 🐛 Troubleshooting

**Imagem não carrega:**
- Verifique conexão com internet
- A imagem vem do Wikimedia Commons
- Se o site estiver fora, troque a URL

**Botões não funcionam:**
- Limpe o cache: Ctrl + Shift + Delete
- Recarregue a página: F5

**Zoom não funciona:**
- Use os botões + e - na tela
- Ou use o mouse wheel
- Ou use as teclas de seta

---

## 📚 Tecnologias Usadas

- **OpenSeadragon** - Viewer de imagens (zoom infinito)
- **Tailwind CSS** - Styling
- **Vanilla JavaScript** - Lógica
- **HTML5** - Estrutura

---

## 👨‍💻 Autor

Desenvolvido por: **Matheus L.**
Versão: **2.0 Pro**
Data: **Janeiro 2026**

---

## 📞 Suporte

Para dúvidas ou melhorias, adicione features ou reporte bugs!

---

**Aproveita o show! 🔬✨**
