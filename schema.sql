-- Kisan Mandi Bhav — MySQL schema (XAMPP / MySQL 8). SQLite version is created automatically by db.py.
-- NOTE: MySQL was NOT live-tested in this build; SQLite (app.db) was tested. Check on XAMPP before viva.
CREATE DATABASE IF NOT EXISTS crop_price_db CHARACTER SET utf8mb4;
USE crop_price_db;
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(120), email VARCHAR(120) UNIQUE,
  password_hash VARCHAR(255), role VARCHAR(20) DEFAULT 'farmer', phone VARCHAR(20), state VARCHAR(80),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS prices (
  id INT AUTO_INCREMENT PRIMARY KEY, date DATE, crop VARCHAR(60), mandi VARCHAR(80), state VARCHAR(80),
  min_price INT, max_price INT, modal_price INT, arrivals_quintals INT, rainfall_mm FLOAT, msp_rs_per_quintal INT);
CREATE TABLE IF NOT EXISTS predictions (
  id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, crop VARCHAR(60), mandi VARCHAR(80),
  target_date DATE, predicted_price FLOAT, horizon_days INT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS alerts (
  id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, crop VARCHAR(60), mandi VARCHAR(80),
  target_price FLOAT, channel VARCHAR(20), status VARCHAR(20) DEFAULT 'saved', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
-- Demo admin: admin / admin123 (hash created by app on first run; insert here only if you hash it first)
