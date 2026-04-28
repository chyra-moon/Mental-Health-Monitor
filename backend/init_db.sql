-- Mental Health Monitor 数据库初始化脚本

CREATE DATABASE IF NOT EXISTS mental_health
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE mental_health;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    role ENUM('student', 'admin') NOT NULL DEFAULT 'student',
    gender VARCHAR(10) DEFAULT NULL,
    class_name VARCHAR(50) DEFAULT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 情绪识别记录表
CREATE TABLE IF NOT EXISTS emotion_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    dominant_emotion VARCHAR(20) NOT NULL,
    confidence DECIMAL(5,4) DEFAULT NULL,
    emotion_scores JSON DEFAULT NULL,
    risk_level ENUM('low', 'medium', 'high') DEFAULT 'low',
    suggestion TEXT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_risk (risk_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 心理问卷记录表
CREATE TABLE IF NOT EXISTS questionnaire_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_score INT NOT NULL DEFAULT 0,
    answers JSON DEFAULT NULL,
    risk_level ENUM('low', 'medium', 'high') DEFAULT 'low',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 风险预警表
CREATE TABLE IF NOT EXISTS risk_warnings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    warning_level ENUM('low', 'medium', 'high') NOT NULL,
    reason TEXT DEFAULT NULL,
    status ENUM('pending', 'handled') NOT NULL DEFAULT 'pending',
    suggestion TEXT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    handled_at DATETIME DEFAULT NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_level_status (warning_level, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 干预建议表
CREATE TABLE IF NOT EXISTS intervention_suggestions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    warning_id INT DEFAULT NULL,
    content TEXT NOT NULL,
    source ENUM('system', 'admin') NOT NULL DEFAULT 'system',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 管理员账号由后端初始化脚本创建，不在 SQL 中硬编码密码
