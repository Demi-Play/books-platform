# 📚 Литературная Платформа
 Web Application for system controls of content

# ✨ Основные возможности
- Регистрация и авторизация пользователей
- Публикация и модерация книг
- Читательские клубы
- Система рекомендаций
- Интерактивное взаимодействие

## 📋 Описание проекта
Веб-приложение для чтения, публикации и обсуждения книг с развитой системой социального взаимодействия.

## 🚀 Требования к окружению
- Python 3.10+
- pip
- virtualenv (опционально, но рекомендуется)

## 🔐 Безопасность
- Хеширование паролей
- Защита от CSRF-атак
- Многоуровневая система прав
- Модерация контента

## 🛠 Технологический стек
- Flask
- SQLAlchemy
- Jinja2
- MUI CSS
- Flask-Login
- Flask-WTF

## 🐛 Возможные проблемы и решения
- Проблемы с зависимостями: `pip install --upgrade pip`
- Ошибки базы данных: `flask db migrate` и `flask db upgrade`

## 🆘 Поддержка
При возникновении проблем создайте Issue в репозитории или свяжитесь с разработчиком.

## 🔧 Установка и настройка

### 1. Клонирование репозитория
```bash
git clone https://github.com/Demi-Play/books-platform.git
cd books-platform
```

### 2. Создание виртуального окружения
Для Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Установка дополнительных зависимостей

Языковая модель spaCy

```bash
python -m spacy download ru_core_news_sm
python -m spacy download ru_core_news_md
```

Установка моделей

```bash
pip install textblob
```

### 5. Запуск приложения
Перейдите в каталог с файлом run.py и запустите его через терминал следующим образом: 
```bash
python run.py
```

