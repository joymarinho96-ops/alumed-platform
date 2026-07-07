# Configuração do Projeto Alumed

Siga os passos abaixo para configurar e rodar o projeto após clonar o repositório.

## 1. Configurar o Ambiente Virtual

Certifique-se de que o ambiente virtual está ativo. Se você ainda não criou um:

```bash
python -m venv venv
```

Para ativar:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

## 2. Instalar Dependências

Instale as bibliotecas necessárias listadas no `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 3. Configurar o Banco de Dados e Migrações

Execute os comandos abaixo para criar as tabelas no banco de dados e carregar as migrações dos aplicativos:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 4. Criar Superusuário (Opcional)

Para acessar o painel administrativo:

```bash
python manage.py createsuperuser
```

## 5. Rodar o Servidor

Inicie o servidor de desenvolvimento:

```bash
python manage.py runserver
```

O projeto estará acessível em `http://127.0.0.1:8000/`.
