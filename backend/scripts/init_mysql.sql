CREATE DATABASE IF NOT EXISTS `paper_ai_system`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `paper_ai_system`;

CREATE TABLE IF NOT EXISTS `paper` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(512) NULL,
  `authors` TEXT NULL,
  `year` VARCHAR(32) NULL,
  `keywords` TEXT NULL,
  `research_problem` TEXT NULL,
  `method` TEXT NULL,
  `dataset` TEXT NULL,
  `metrics` TEXT NULL,
  `contribution` TEXT NULL,
  `limitation` TEXT NULL,
  `conclusion` TEXT NULL,
  `file_name` VARCHAR(255) NOT NULL,
  `file_path` VARCHAR(1024) NOT NULL,
  `file_size` INT NOT NULL DEFAULT 0,
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_paper_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `qa_record` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `paper_id` INT NOT NULL,
  `question` TEXT NOT NULL,
  `answer` TEXT NOT NULL,
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_qa_record_paper_id` (`paper_id`),
  INDEX `idx_qa_record_create_time` (`create_time`),
  CONSTRAINT `fk_qa_record_paper_id`
    FOREIGN KEY (`paper_id`) REFERENCES `paper` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `paper_note` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `paper_id` INT NOT NULL,
  `note_style` VARCHAR(255) NULL,
  `content` TEXT NOT NULL,
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_paper_note_paper_id` (`paper_id`),
  INDEX `idx_paper_note_create_time` (`create_time`),
  CONSTRAINT `fk_paper_note_paper_id`
    FOREIGN KEY (`paper_id`) REFERENCES `paper` (`id`)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `workflow_log` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `workflow_type` VARCHAR(32) NOT NULL,
  `paper_id` INT NULL,
  `request_content` TEXT NULL,
  `response_content` TEXT NULL,
  `status` VARCHAR(32) NOT NULL DEFAULT 'success',
  `error_message` TEXT NULL,
  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  INDEX `idx_workflow_log_workflow_type` (`workflow_type`),
  INDEX `idx_workflow_log_paper_id` (`paper_id`),
  INDEX `idx_workflow_log_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
