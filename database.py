import sqlite3
import os
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "onear.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_connection()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS vocabularies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language TEXT NOT NULL,
        word TEXT NOT NULL,
        definition TEXT NOT NULL,
        example TEXT,
        UNIQUE(language, word)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS learning_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        word_id INTEGER NOT NULL,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(word_id) REFERENCES vocabularies(id),
        UNIQUE(user_id, word_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        language TEXT NOT NULL,
        score INTEGER NOT NULL,
        total_questions INTEGER NOT NULL,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS grammars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language TEXT NOT NULL,
        title TEXT NOT NULL,
        question TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        options TEXT NOT NULL,
        explanation TEXT,
        UNIQUE(language, question)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_vocabularies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        language TEXT NOT NULL,
        word TEXT NOT NULL,
        definition TEXT NOT NULL,
        example TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS user_grammars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        language TEXT NOT NULL,
        title TEXT NOT NULL,
        question TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        options TEXT NOT NULL,
        explanation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    conn.commit()
    conn.close()

def create_user(username):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None

def get_user_by_username(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    conn.close()
    return user

def add_vocabularies(language, words):
    conn = get_connection()
    c = conn.cursor()
    for word_data in words:
        try:
            c.execute('''INSERT INTO vocabularies (language, word, definition, example)
                        VALUES (?, ?, ?, ?)''',
                     (language, word_data['word'], word_data['definition'], word_data.get('example', '')))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

def get_vocabularies_by_language(language):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM vocabularies WHERE language = ?', (language,))
    words = c.fetchall()
    conn.close()
    return words

def get_all_languages():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT DISTINCT language FROM vocabularies')
    languages = [row[0] for row in c.fetchall()]
    conn.close()
    return languages

def record_learning(user_id, word_id):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO learning_history (user_id, word_id)
                    VALUES (?, ?)''', (user_id, word_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_user_learned_count(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM learning_history WHERE user_id = ?', (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_user_learned_by_language(user_id, language):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM learning_history lh
                JOIN vocabularies v ON lh.word_id = v.id
                WHERE lh.user_id = ? AND v.language = ?''',
             (user_id, language))
    count = c.fetchone()[0]
    conn.close()
    return count

def save_quiz_result(user_id, language, score, total_questions):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO quiz_results (user_id, language, score, total_questions)
                VALUES (?, ?, ?, ?)''',
             (user_id, language, score, total_questions))
    conn.commit()
    conn.close()

def get_user_best_quiz_score(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT MAX(score) FROM quiz_results WHERE user_id = ?''', (user_id,))
    score = c.fetchone()[0]
    conn.close()
    return score if score else 0

def get_ranking():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''SELECT u.id, u.username, COUNT(lh.id) as learned_count
                FROM users u
                LEFT JOIN learning_history lh ON u.id = lh.user_id
                GROUP BY u.id
                ORDER BY learned_count DESC''')
    ranking = c.fetchall()
    conn.close()
    return ranking

def get_user_rank(user_id):
    ranking = get_ranking()
    for idx, row in enumerate(ranking, 1):
        if row['id'] == user_id:
            return idx
    return None

def add_grammars(language, grammars):
    import json
    conn = get_connection()
    c = conn.cursor()
    for grammar in grammars:
        try:
            options_json = json.dumps(grammar['options']) if isinstance(grammar['options'], list) else grammar['options']
            c.execute('''INSERT INTO grammars (language, title, question, correct_answer, options, explanation)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (language, grammar['title'], grammar['question'], grammar['correct_answer'],
                      options_json, grammar.get('explanation', '')))
        except sqlite3.IntegrityError:
            pass
    conn.commit()
    conn.close()

def get_grammars_by_language(language):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM grammars WHERE language = ?', (language,))
    grammars = c.fetchall()
    conn.close()
    return grammars

def add_user_vocabulary(user_id, language, word, definition, example):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''INSERT INTO user_vocabularies (user_id, language, word, definition, example)
                    VALUES (?, ?, ?, ?, ?)''',
                 (user_id, language, word, definition, example))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_user_vocabularies(user_id, language):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM user_vocabularies WHERE user_id = ? AND language = ?',
             (user_id, language))
    vocabs = c.fetchall()
    conn.close()
    return vocabs

def add_user_grammar(user_id, language, title, question, correct_answer, options, explanation):
    import json
    try:
        conn = get_connection()
        c = conn.cursor()
        options_json = json.dumps(options) if isinstance(options, list) else options
        c.execute('''INSERT INTO user_grammars (user_id, language, title, question, correct_answer, options, explanation)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (user_id, language, title, question, correct_answer, options_json, explanation))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_user_grammars(user_id, language):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM user_grammars WHERE user_id = ? AND language = ?',
             (user_id, language))
    grammars = c.fetchall()
    conn.close()
    return grammars

def get_all_grammars_by_language(language):
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM grammars WHERE language = ?', (language,))
    grammars = c.fetchall()
    conn.close()
    return grammars

def add_language(language):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute('INSERT INTO vocabularies (language, word, definition) VALUES (?, ?, ?)',
                 (language, 'sample', 'Sample word'))
        conn.commit()
        conn.close()
        return True
    except:
        return False
