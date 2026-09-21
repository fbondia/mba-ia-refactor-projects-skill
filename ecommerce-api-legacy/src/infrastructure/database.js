const sqlite3 = require('sqlite3').verbose();
const crypto = require('crypto');
const { hashPassword } = require('../services/passwordService');

const SCHEMA = `
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL CHECK(price >= 0), active INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id) ON DELETE RESTRICT
);
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY, enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    amount REAL NOT NULL CHECK(amount >= 0), status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY, action TEXT NOT NULL, created_at DATETIME NOT NULL
);`;

class Database {
    constructor(path) {
        this.connection = new sqlite3.Database(path);
    }

    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.run(sql, params, function callback(error) {
                if (error) reject(error);
                else resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.get(sql, params, (error, row) => error ? reject(error) : resolve(row));
        });
    }

    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.connection.all(sql, params, (error, rows) => error ? reject(error) : resolve(rows));
        });
    }

    exec(sql) {
        return new Promise((resolve, reject) => {
            this.connection.exec(sql, (error) => error ? reject(error) : resolve());
        });
    }

    close() {
        return new Promise((resolve, reject) => {
            this.connection.close((error) => error ? reject(error) : resolve());
        });
    }

    async transaction(work) {
        await this.run('BEGIN IMMEDIATE');
        try {
            const result = await work();
            await this.run('COMMIT');
            return result;
        } catch (error) {
            await this.run('ROLLBACK');
            throw error;
        }
    }

    async initialize() {
        await this.exec(SCHEMA);
        const { count } = await this.get('SELECT COUNT(*) AS count FROM courses');
        if (count === 0) await this.seed();
    }

    async seed() {
        await this.transaction(async () => {
            await this.run(
                'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
                ['Leonan', 'leonan@fullcycle.com.br', hashPassword(crypto.randomBytes(24).toString('base64url'))]
            );
            await this.run(
                'INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)',
                ['Clean Architecture', 997, 'Docker', 497]
            );
            await this.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
            await this.run(
                "INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997, 'PAID')"
            );
        });
    }
}

module.exports = { Database };
