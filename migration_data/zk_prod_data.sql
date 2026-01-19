/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.5.2-MariaDB, for Win64 (AMD64)
--
-- Host: 127.0.0.1    Database: zk_prod
-- ------------------------------------------------------
-- Server version	11.5.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` (`version_num`) VALUES ('cd97d1b14125');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `att_daily_attendance`
--

DROP TABLE IF EXISTS `att_daily_attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `att_daily_attendance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) DEFAULT NULL,
  `date` date NOT NULL,
  `timetable_id` int(11) DEFAULT NULL,
  `check_in` datetime DEFAULT NULL,
  `check_out` datetime DEFAULT NULL,
  `on_duty` varchar(10) DEFAULT NULL,
  `off_duty` varchar(10) DEFAULT NULL,
  `late_minutes` int(11) DEFAULT NULL,
  `early_minutes` int(11) DEFAULT NULL,
  `worked_minutes` int(11) DEFAULT NULL,
  `overtime_minutes` int(11) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `exception_reason` varchar(100) DEFAULT NULL,
  `schedule_type` varchar(20) DEFAULT 'FIXED',
  `source_logs_count` int(11) DEFAULT 0,
  `is_absent` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_daily_att` (`employee_id`,`date`),
  KEY `timetable_id` (`timetable_id`),
  KEY `ix_att_daily_attendance_id` (`id`),
  KEY `ix_att_daily_attendance_date` (`date`)
) ENGINE=MyISAM AUTO_INCREMENT=656 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `att_daily_attendance`
--

LOCK TABLES `att_daily_attendance` WRITE;
/*!40000 ALTER TABLE `att_daily_attendance` DISABLE KEYS */;
INSERT INTO `att_daily_attendance` (`id`, `employee_id`, `date`, `timetable_id`, `check_in`, `check_out`, `on_duty`, `off_duty`, `late_minutes`, `early_minutes`, `worked_minutes`, `overtime_minutes`, `status`, `exception_reason`, `schedule_type`, `source_logs_count`, `is_absent`) VALUES (649,1,'2025-12-02',1,'2025-12-02 08:00:00','2025-12-02 17:00:00','08:00','17:00',0,0,480,0,'Normal',NULL,'FLEX',2,0);
INSERT INTO `att_daily_attendance` (`id`, `employee_id`, `date`, `timetable_id`, `check_in`, `check_out`, `on_duty`, `off_duty`, `late_minutes`, `early_minutes`, `worked_minutes`, `overtime_minutes`, `status`, `exception_reason`, `schedule_type`, `source_logs_count`, `is_absent`) VALUES (654,2,'2025-12-02',1,'2025-12-02 08:00:00','2025-12-02 17:00:00','08:00','17:00',0,0,480,0,'Normal',NULL,'FLEX',2,0);
INSERT INTO `att_daily_attendance` (`id`, `employee_id`, `date`, `timetable_id`, `check_in`, `check_out`, `on_duty`, `off_duty`, `late_minutes`, `early_minutes`, `worked_minutes`, `overtime_minutes`, `status`, `exception_reason`, `schedule_type`, `source_logs_count`, `is_absent`) VALUES (655,3,'2025-12-02',1,'2025-12-02 08:00:00','2025-12-02 16:00:00','08:00','17:00',0,0,420,0,'Early/Partial',NULL,'FLEX',2,0);
INSERT INTO `att_daily_attendance` (`id`, `employee_id`, `date`, `timetable_id`, `check_in`, `check_out`, `on_duty`, `off_duty`, `late_minutes`, `early_minutes`, `worked_minutes`, `overtime_minutes`, `status`, `exception_reason`, `schedule_type`, `source_logs_count`, `is_absent`) VALUES (653,1,'2025-12-15',1,'2025-12-15 08:00:00','2025-12-15 17:45:00','08:00','17:00',0,0,525,45,'Normal, Overtime',NULL,'FLEX',2,0);
/*!40000 ALTER TABLE `att_daily_attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `att_employee_shifts`
--

DROP TABLE IF EXISTS `att_employee_shifts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `att_employee_shifts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) DEFAULT NULL,
  `shift_id` int(11) DEFAULT NULL,
  `start_date` date NOT NULL,
  `end_date` date DEFAULT NULL,
  `scope` varchar(20) DEFAULT 'EMPLOYEE',
  `department_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `employee_id` (`employee_id`),
  KEY `shift_id` (`shift_id`),
  KEY `ix_att_employee_shifts_id` (`id`),
  KEY `department_id` (`department_id`)
) ENGINE=MyISAM AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `att_employee_shifts`
--

LOCK TABLES `att_employee_shifts` WRITE;
/*!40000 ALTER TABLE `att_employee_shifts` DISABLE KEYS */;
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (1,1,1,'2025-09-01',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (2,2,1,'2025-09-01',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (3,3,1,'2025-09-01',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (4,4,2,'2025-09-01',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (5,5,2,'2025-09-01',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (6,6,2,'2025-09-01',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (7,7,3,'2025-09-01',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (8,8,3,'2025-09-01',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (9,9,3,'2025-09-01',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (10,10,3,'2025-09-01',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (11,4,1,'2025-12-22',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (15,1,1,'2025-12-22',NULL,'EMPLOYEE',NULL);
INSERT INTO `att_employee_shifts` (`id`, `employee_id`, `shift_id`, `start_date`, `end_date`, `scope`, `department_id`) VALUES (16,1,1,'2025-12-22',NULL,'EMPLOYEE',NULL);
/*!40000 ALTER TABLE `att_employee_shifts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `att_holidays`
--

DROP TABLE IF EXISTS `att_holidays`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `att_holidays` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `start_date` date NOT NULL,
  `end_date` date NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_att_holidays_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `att_holidays`
--

LOCK TABLES `att_holidays` WRITE;
/*!40000 ALTER TABLE `att_holidays` DISABLE KEYS */;
/*!40000 ALTER TABLE `att_holidays` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `att_leaves`
--

DROP TABLE IF EXISTS `att_leaves`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `att_leaves` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) DEFAULT NULL,
  `leave_type` varchar(50) DEFAULT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `employee_id` (`employee_id`),
  KEY `ix_att_leaves_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `att_leaves`
--

LOCK TABLES `att_leaves` WRITE;
/*!40000 ALTER TABLE `att_leaves` DISABLE KEYS */;
INSERT INTO `att_leaves` (`id`, `employee_id`, `leave_type`, `start_time`, `end_time`, `reason`, `status`) VALUES (1,1,'Vacation','2025-12-24 00:00:00','2025-12-26 23:59:00','Christmas Break','Approved');
INSERT INTO `att_leaves` (`id`, `employee_id`, `leave_type`, `start_time`, `end_time`, `reason`, `status`) VALUES (2,2,'Sick Leave','2025-12-10 08:00:00','2025-12-10 18:00:00','Flu','Approved');
/*!40000 ALTER TABLE `att_leaves` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `att_schedule_overrides`
--

DROP TABLE IF EXISTS `att_schedule_overrides`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `att_schedule_overrides` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `employee_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `timetable_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_sched_override` (`employee_id`,`date`),
  KEY `timetable_id` (`timetable_id`),
  KEY `ix_att_schedule_overrides_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `att_schedule_overrides`
--

LOCK TABLES `att_schedule_overrides` WRITE;
/*!40000 ALTER TABLE `att_schedule_overrides` DISABLE KEYS */;
/*!40000 ALTER TABLE `att_schedule_overrides` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `att_shift_timetables`
--

DROP TABLE IF EXISTS `att_shift_timetables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `att_shift_timetables` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `shift_id` int(11) DEFAULT NULL,
  `timetable_id` int(11) DEFAULT NULL,
  `day_index` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `shift_id` (`shift_id`),
  KEY `timetable_id` (`timetable_id`),
  KEY `ix_att_shift_timetables_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `att_shift_timetables`
--

LOCK TABLES `att_shift_timetables` WRITE;
/*!40000 ALTER TABLE `att_shift_timetables` DISABLE KEYS */;
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (1,1,1,0);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (2,1,1,1);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (3,1,1,2);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (4,1,1,3);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (5,1,1,4);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (6,2,2,0);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (7,2,2,1);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (8,2,2,2);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (9,2,2,3);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (10,2,2,4);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (11,3,3,0);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (12,3,3,1);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (13,3,3,2);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (14,3,3,3);
INSERT INTO `att_shift_timetables` (`id`, `shift_id`, `timetable_id`, `day_index`) VALUES (15,3,3,4);
/*!40000 ALTER TABLE `att_shift_timetables` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `att_shifts`
--

DROP TABLE IF EXISTS `att_shifts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `att_shifts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_att_shifts_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `att_shifts`
--

LOCK TABLES `att_shifts` WRITE;
/*!40000 ALTER TABLE `att_shifts` DISABLE KEYS */;
INSERT INTO `att_shifts` (`id`, `name`) VALUES (1,'Turno Administrativo');
INSERT INTO `att_shifts` (`id`, `name`) VALUES (2,'Produccion Rotativo');
INSERT INTO `att_shifts` (`id`, `name`) VALUES (3,'Soporte Flexible');
/*!40000 ALTER TABLE `att_shifts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `att_timetables`
--

DROP TABLE IF EXISTS `att_timetables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `att_timetables` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `on_duty_time` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `off_duty_time` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `late_allow_minutes` int(11) DEFAULT NULL,
  `early_leave_allow_minutes` int(11) DEFAULT NULL,
  `check_in_start` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `check_in_end` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `check_out_start` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `check_out_end` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `break_minutes` int(11) DEFAULT NULL,
  `rounding_rule` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `required_minutes` int(11) DEFAULT NULL,
  `work_days` int(11) DEFAULT NULL,
  `is_flexible` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_att_timetables_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `att_timetables`
--

LOCK TABLES `att_timetables` WRITE;
/*!40000 ALTER TABLE `att_timetables` DISABLE KEYS */;
INSERT INTO `att_timetables` (`id`, `name`, `on_duty_time`, `off_duty_time`, `late_allow_minutes`, `early_leave_allow_minutes`, `check_in_start`, `check_in_end`, `check_out_start`, `check_out_end`, `break_minutes`, `rounding_rule`, `required_minutes`, `work_days`, `is_flexible`) VALUES (1,'Turno flexible','08:00','17:00',5,5,'07:30','08:15','16:45','18:00',60,'none',480,1,1);
INSERT INTO `att_timetables` (`id`, `name`, `on_duty_time`, `off_duty_time`, `late_allow_minutes`, `early_leave_allow_minutes`, `check_in_start`, `check_in_end`, `check_out_start`, `check_out_end`, `break_minutes`, `rounding_rule`, `required_minutes`, `work_days`, `is_flexible`) VALUES (2,'Produccion Manana','06:00','14:00',3,5,'05:30','06:10','13:50','14:30',30,'5min',0,1,0);
/*!40000 ALTER TABLE `att_timetables` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attendance_logs`
--

DROP TABLE IF EXISTS `attendance_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attendance_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) DEFAULT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `punch` int(11) DEFAULT NULL,
  `verify_mode` int(11) DEFAULT NULL,
  `workstate` int(11) DEFAULT NULL,
  `workcode` int(11) DEFAULT NULL,
  `punch_source` varchar(50) DEFAULT NULL,
  `raw_json` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`raw_json`)),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_att_log` (`device_id`,`user_id`,`timestamp`),
  KEY `ix_attendance_logs_user_id` (`user_id`),
  KEY `ix_attendance_logs_id` (`id`),
  KEY `ix_attendance_logs_timestamp` (`timestamp`)
) ENGINE=MyISAM AUTO_INCREMENT=405 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance_logs`
--

LOCK TABLES `attendance_logs` WRITE;
/*!40000 ALTER TABLE `attendance_logs` DISABLE KEYS */;
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (11,1,'1','2025-12-01 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (12,1,'1','2025-12-01 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (13,1,'1','2025-12-02 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (14,1,'1','2025-12-02 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (15,1,'1','2025-12-03 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (16,1,'1','2025-12-03 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (17,1,'1','2025-12-04 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (18,1,'1','2025-12-04 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (19,1,'1','2025-12-05 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (20,1,'1','2025-12-05 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (21,1,'1','2025-12-08 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (22,1,'1','2025-12-08 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (23,1,'1','2025-12-09 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (24,1,'1','2025-12-09 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (25,1,'1','2025-12-10 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (26,1,'1','2025-12-10 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (27,1,'1','2025-12-11 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (28,1,'1','2025-12-11 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (29,1,'1','2025-12-12 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (30,1,'1','2025-12-12 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (31,1,'1','2025-12-15 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (32,1,'1','2025-12-15 17:45:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (33,1,'1','2025-12-16 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (34,1,'1','2025-12-16 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (35,1,'1','2025-12-17 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (36,1,'1','2025-12-17 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (37,1,'1','2025-12-18 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (38,1,'1','2025-12-18 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (39,1,'1','2025-12-19 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (40,1,'1','2025-12-19 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (41,1,'1','2025-12-22 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (42,1,'1','2025-12-22 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (43,1,'1','2025-12-23 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (44,1,'1','2025-12-23 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (45,1,'2','2025-12-01 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (46,1,'2','2025-12-01 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (47,1,'2','2025-12-02 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (48,1,'2','2025-12-02 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (49,1,'2','2025-12-03 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (50,1,'2','2025-12-03 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (51,1,'2','2025-12-04 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (52,1,'2','2025-12-04 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (53,1,'2','2025-12-05 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (54,1,'2','2025-12-05 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (55,1,'2','2025-12-08 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (56,1,'2','2025-12-08 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (57,1,'2','2025-12-09 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (58,1,'2','2025-12-09 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (59,1,'2','2025-12-10 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (60,1,'2','2025-12-10 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (61,1,'2','2025-12-11 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (62,1,'2','2025-12-11 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (63,1,'2','2025-12-12 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (64,1,'2','2025-12-12 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (65,1,'2','2025-12-15 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (66,1,'2','2025-12-15 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (67,1,'2','2025-12-16 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (68,1,'2','2025-12-16 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (69,1,'2','2025-12-17 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (70,1,'2','2025-12-17 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (71,1,'2','2025-12-18 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (72,1,'2','2025-12-18 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (73,1,'2','2025-12-19 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (74,1,'2','2025-12-19 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (75,1,'2','2025-12-22 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (76,1,'2','2025-12-22 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (77,1,'2','2025-12-23 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (78,1,'2','2025-12-23 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (79,1,'3','2025-12-01 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (80,1,'3','2025-12-01 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (81,1,'3','2025-12-02 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (82,1,'3','2025-12-02 16:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (83,1,'3','2025-12-03 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (84,1,'3','2025-12-03 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (85,1,'3','2025-12-04 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (86,1,'3','2025-12-04 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (87,1,'3','2025-12-05 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (88,1,'3','2025-12-05 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (89,1,'3','2025-12-08 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (90,1,'3','2025-12-08 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (91,1,'3','2025-12-09 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (92,1,'3','2025-12-09 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (93,1,'3','2025-12-10 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (94,1,'3','2025-12-10 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (95,1,'3','2025-12-11 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (96,1,'3','2025-12-11 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (97,1,'3','2025-12-12 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (98,1,'3','2025-12-12 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (99,1,'3','2025-12-15 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (100,1,'3','2025-12-15 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (101,1,'3','2025-12-16 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (102,1,'3','2025-12-16 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (103,1,'3','2025-12-17 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (104,1,'3','2025-12-17 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (105,1,'3','2025-12-18 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (106,1,'3','2025-12-18 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (107,1,'3','2025-12-19 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (108,1,'3','2025-12-19 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (109,1,'3','2025-12-22 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (110,1,'3','2025-12-22 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (111,1,'3','2025-12-23 08:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (112,1,'3','2025-12-23 17:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (113,1,'4','2025-12-01 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (114,1,'4','2025-12-01 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (115,1,'4','2025-12-02 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (116,1,'4','2025-12-02 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (117,1,'4','2025-12-03 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (118,1,'4','2025-12-03 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (119,1,'4','2025-12-04 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (120,1,'4','2025-12-04 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (121,1,'4','2025-12-05 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (122,1,'4','2025-12-05 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (123,1,'4','2025-12-08 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (124,1,'4','2025-12-08 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (125,1,'4','2025-12-09 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (126,1,'4','2025-12-09 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (127,1,'4','2025-12-10 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (128,1,'4','2025-12-10 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (129,1,'4','2025-12-11 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (130,1,'4','2025-12-11 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (131,1,'4','2025-12-12 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (132,1,'4','2025-12-12 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (133,1,'4','2025-12-15 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (134,1,'4','2025-12-15 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (135,1,'4','2025-12-16 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (136,1,'4','2025-12-16 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (137,1,'4','2025-12-17 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (138,1,'4','2025-12-17 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (139,1,'4','2025-12-18 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (140,1,'4','2025-12-18 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (141,1,'4','2025-12-19 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (142,1,'4','2025-12-19 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (143,1,'4','2025-12-22 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (144,1,'4','2025-12-22 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (145,1,'4','2025-12-23 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (146,1,'4','2025-12-23 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (147,1,'5','2025-12-01 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (148,1,'5','2025-12-01 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (149,1,'5','2025-12-02 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (150,1,'5','2025-12-02 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (151,1,'5','2025-12-03 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (152,1,'5','2025-12-03 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (153,1,'5','2025-12-04 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (154,1,'5','2025-12-04 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (155,1,'5','2025-12-05 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (156,1,'5','2025-12-05 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (157,1,'5','2025-12-08 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (158,1,'5','2025-12-08 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (159,1,'5','2025-12-09 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (160,1,'5','2025-12-09 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (161,1,'5','2025-12-10 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (162,1,'5','2025-12-10 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (163,1,'5','2025-12-11 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (164,1,'5','2025-12-11 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (165,1,'5','2025-12-12 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (166,1,'5','2025-12-12 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (167,1,'5','2025-12-15 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (168,1,'5','2025-12-15 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (169,1,'5','2025-12-16 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (170,1,'5','2025-12-16 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (171,1,'5','2025-12-17 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (172,1,'5','2025-12-17 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (173,1,'5','2025-12-18 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (174,1,'5','2025-12-18 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (175,1,'5','2025-12-19 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (176,1,'5','2025-12-19 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (177,1,'5','2025-12-22 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (178,1,'5','2025-12-22 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (179,1,'5','2025-12-23 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (180,1,'5','2025-12-23 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (181,1,'6','2025-12-01 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (182,1,'6','2025-12-01 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (183,1,'6','2025-12-02 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (184,1,'6','2025-12-02 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (185,1,'6','2025-12-03 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (186,1,'6','2025-12-03 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (187,1,'6','2025-12-04 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (188,1,'6','2025-12-04 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (189,1,'6','2025-12-05 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (190,1,'6','2025-12-05 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (191,1,'6','2025-12-08 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (192,1,'6','2025-12-08 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (193,1,'6','2025-12-09 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (194,1,'6','2025-12-09 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (195,1,'6','2025-12-10 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (196,1,'6','2025-12-10 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (197,1,'6','2025-12-11 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (198,1,'6','2025-12-11 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (199,1,'6','2025-12-12 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (200,1,'6','2025-12-12 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (201,1,'6','2025-12-15 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (202,1,'6','2025-12-15 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (203,1,'6','2025-12-16 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (204,1,'6','2025-12-16 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (205,1,'6','2025-12-17 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (206,1,'6','2025-12-17 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (207,1,'6','2025-12-18 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (208,1,'6','2025-12-18 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (209,1,'6','2025-12-19 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (210,1,'6','2025-12-19 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (211,1,'6','2025-12-22 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (212,1,'6','2025-12-22 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (213,1,'6','2025-12-23 06:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (214,1,'6','2025-12-23 14:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (215,1,'7','2025-12-01 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (216,1,'7','2025-12-01 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (217,1,'7','2025-12-02 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (218,1,'7','2025-12-02 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (219,1,'7','2025-12-03 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (220,1,'7','2025-12-03 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (221,1,'7','2025-12-04 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (222,1,'7','2025-12-04 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (223,1,'7','2025-12-05 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (224,1,'7','2025-12-05 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (225,1,'7','2025-12-08 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (226,1,'7','2025-12-08 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (227,1,'7','2025-12-09 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (228,1,'7','2025-12-09 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (229,1,'7','2025-12-10 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (230,1,'7','2025-12-10 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (231,1,'7','2025-12-11 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (232,1,'7','2025-12-11 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (233,1,'7','2025-12-12 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (234,1,'7','2025-12-12 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (235,1,'7','2025-12-15 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (236,1,'7','2025-12-15 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (237,1,'7','2025-12-16 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (238,1,'7','2025-12-16 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (239,1,'7','2025-12-17 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (240,1,'7','2025-12-17 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (241,1,'7','2025-12-18 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (242,1,'7','2025-12-18 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (243,1,'7','2025-12-19 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (244,1,'7','2025-12-19 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (245,1,'7','2025-12-22 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (246,1,'7','2025-12-22 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (247,1,'7','2025-12-23 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (248,1,'7','2025-12-23 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (249,1,'8','2025-12-01 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (250,1,'8','2025-12-01 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (251,1,'8','2025-12-02 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (252,1,'8','2025-12-02 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (253,1,'8','2025-12-03 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (254,1,'8','2025-12-03 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (255,1,'8','2025-12-04 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (256,1,'8','2025-12-04 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (257,1,'8','2025-12-05 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (258,1,'8','2025-12-05 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (259,1,'8','2025-12-08 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (260,1,'8','2025-12-08 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (261,1,'8','2025-12-09 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (262,1,'8','2025-12-09 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (263,1,'8','2025-12-10 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (264,1,'8','2025-12-10 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (265,1,'8','2025-12-11 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (266,1,'8','2025-12-11 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (267,1,'8','2025-12-12 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (268,1,'8','2025-12-12 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (269,1,'8','2025-12-15 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (270,1,'8','2025-12-15 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (271,1,'8','2025-12-16 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (272,1,'8','2025-12-16 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (273,1,'8','2025-12-17 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (274,1,'8','2025-12-17 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (275,1,'8','2025-12-18 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (276,1,'8','2025-12-18 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (277,1,'8','2025-12-19 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (278,1,'8','2025-12-19 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (279,1,'8','2025-12-22 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (280,1,'8','2025-12-22 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (281,1,'8','2025-12-23 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (282,1,'8','2025-12-23 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (283,1,'9','2025-12-01 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (284,1,'9','2025-12-01 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (285,1,'9','2025-12-02 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (286,1,'9','2025-12-02 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (287,1,'9','2025-12-03 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (288,1,'9','2025-12-03 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (289,1,'9','2025-12-04 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (290,1,'9','2025-12-04 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (291,1,'9','2025-12-05 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (292,1,'9','2025-12-05 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (293,1,'9','2025-12-08 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (294,1,'9','2025-12-08 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (295,1,'9','2025-12-09 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (296,1,'9','2025-12-09 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (297,1,'9','2025-12-10 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (298,1,'9','2025-12-10 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (299,1,'9','2025-12-11 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (300,1,'9','2025-12-11 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (301,1,'9','2025-12-12 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (302,1,'9','2025-12-12 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (303,1,'9','2025-12-15 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (304,1,'9','2025-12-15 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (305,1,'9','2025-12-16 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (306,1,'9','2025-12-16 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (307,1,'9','2025-12-17 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (308,1,'9','2025-12-17 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (309,1,'9','2025-12-18 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (310,1,'9','2025-12-18 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (311,1,'9','2025-12-19 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (312,1,'9','2025-12-19 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (313,1,'9','2025-12-22 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (314,1,'9','2025-12-22 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (315,1,'9','2025-12-23 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (316,1,'9','2025-12-23 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (317,1,'10','2025-12-01 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (318,1,'10','2025-12-01 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (319,1,'10','2025-12-02 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (320,1,'10','2025-12-02 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (321,1,'10','2025-12-03 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (322,1,'10','2025-12-03 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (323,1,'10','2025-12-04 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (324,1,'10','2025-12-04 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (325,1,'10','2025-12-05 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (326,1,'10','2025-12-05 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (327,1,'10','2025-12-08 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (328,1,'10','2025-12-08 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (329,1,'10','2025-12-09 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (330,1,'10','2025-12-09 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (331,1,'10','2025-12-10 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (332,1,'10','2025-12-10 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (333,1,'10','2025-12-11 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (334,1,'10','2025-12-11 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (335,1,'10','2025-12-12 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (336,1,'10','2025-12-12 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (337,1,'10','2025-12-15 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (338,1,'10','2025-12-15 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (339,1,'10','2025-12-16 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (340,1,'10','2025-12-16 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (341,1,'10','2025-12-17 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (342,1,'10','2025-12-17 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (343,1,'10','2025-12-18 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (344,1,'10','2025-12-18 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (345,1,'10','2025-12-19 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (346,1,'10','2025-12-19 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (347,1,'10','2025-12-22 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (348,1,'10','2025-12-22 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (349,1,'10','2025-12-23 07:00:00',0,0,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (350,1,'10','2025-12-23 23:00:00',1,1,NULL,NULL,NULL,'seed',NULL);
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (351,1,'99999','2025-03-12 12:31:28',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (352,1,'99999','2025-03-12 12:46:01',1,1,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 1}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (353,1,'99999','2025-03-12 13:28:40',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (354,1,'99999','2025-03-12 19:39:48',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (355,1,'99999','2025-03-13 09:39:50',1,1,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 1}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (356,1,'99999','2025-03-13 10:20:53',1,1,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 1}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (357,1,'99999','2025-03-13 15:21:08',1,1,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 1}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (358,1,'99999','2025-03-15 00:42:06',1,1,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 1}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (359,1,'99999','2025-05-06 20:17:03',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (360,1,'99999','2025-05-13 11:47:50',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (361,1,'99999','2025-05-13 11:48:05',1,1,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 1}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (362,1,'99999','2025-06-07 21:58:38',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (363,1,'99999','2025-06-11 12:28:44',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (364,1,'99999','2025-08-03 22:30:47',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (365,1,'99999','2025-08-12 20:40:36',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (366,1,'99999','2025-12-08 23:04:36',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (367,1,'99999','2025-12-08 23:06:11',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (368,1,'99999','2025-12-08 23:06:28',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (369,1,'99999','2025-12-09 00:31:56',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (370,1,'99999','2025-12-09 00:53:57',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (371,1,'99999','2025-12-09 00:53:59',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (372,1,'99999','2025-12-09 01:01:00',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (373,1,'99999','2025-12-09 01:01:30',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (374,1,'99999','2025-12-09 01:01:32',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (375,1,'99999','2025-12-09 01:01:35',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (376,1,'99999','2025-12-09 01:07:16',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (377,1,'99999','2025-12-09 01:07:18',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (378,1,'99999','2025-12-09 01:07:23',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (379,1,'99999','2025-12-09 01:07:25',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (380,1,'99999','2025-12-09 01:17:30',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (381,1,'99999','2025-12-09 01:17:32',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (382,1,'99999','2025-12-09 01:32:32',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (383,1,'99999','2025-12-09 01:46:51',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (384,1,'99999','2025-12-09 01:46:53',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (385,1,'99999','2025-12-10 19:41:34',1,1,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 1}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (386,1,'99999','2025-12-13 01:01:29',1,1,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 1}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (387,1,'99999','2025-12-13 20:02:54',1,1,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 1}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (388,1,'99999','2025-12-18 22:30:10',1,1,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 1}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (389,1,'99999','2025-12-18 22:30:16',2,2,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 2}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (390,1,'99999','2025-12-18 22:30:21',3,3,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 3}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (391,1,'99999','2025-12-18 22:30:27',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (392,1,'99999','2025-12-20 19:47:02',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (393,1,'99999','2025-12-20 19:47:07',1,1,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 1}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (394,1,'99999','2025-12-20 19:47:27',2,2,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 2}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (395,1,'99999','2025-12-20 19:47:45',3,3,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 3}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (396,1,'99999','2025-12-20 19:47:51',4,4,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 4}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (397,1,'99999','2025-12-20 19:47:58',5,5,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 5}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (398,1,'99999','2025-12-21 02:46:17',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (399,1,'99999','2025-12-25 00:29:43',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (400,1,'99999','2025-12-25 00:29:45',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (401,1,'99999','2025-12-28 01:08:29',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (402,1,'99999','2025-12-31 00:52:11',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (403,1,'99999','2025-12-31 08:50:37',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
INSERT INTO `attendance_logs` (`id`, `device_id`, `user_id`, `timestamp`, `status`, `punch`, `verify_mode`, `workstate`, `workcode`, `punch_source`, `raw_json`) VALUES (404,1,'99999','2026-01-02 17:01:22',0,0,0,NULL,NULL,NULL,'{\"uid\": 1, \"raw_status\": 0, \"raw_punch\": 0}');
/*!40000 ALTER TABLE `attendance_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_users`
--

DROP TABLE IF EXISTS `auth_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(200) NOT NULL,
  `role` varchar(20) DEFAULT NULL,
  `employee_id` int(11) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_auth_users_username` (`username`),
  KEY `employee_id` (`employee_id`),
  KEY `ix_auth_users_id` (`id`),
  CONSTRAINT `auth_users_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `employees` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_users`
--

LOCK TABLES `auth_users` WRITE;
/*!40000 ALTER TABLE `auth_users` DISABLE KEYS */;
INSERT INTO `auth_users` (`id`, `username`, `password_hash`, `role`, `employee_id`, `active`, `created_at`) VALUES (1,'raul','$2b$12$x7UAAO524vWYaWCuUoV29uN/cvPbvhg0uoKr0/0PZXERbZv5mUBj2','admin',NULL,1,'2026-01-07 23:20:30');
/*!40000 ALTER TABLE `auth_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `biometric_templates`
--

DROP TABLE IF EXISTS `biometric_templates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biometric_templates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `type` varchar(20) NOT NULL,
  `index` int(11) DEFAULT 0,
  `valid` int(11) DEFAULT 1,
  `data` text NOT NULL,
  `version` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `biometric_templates`
--

LOCK TABLES `biometric_templates` WRITE;
/*!40000 ALTER TABLE `biometric_templates` DISABLE KEYS */;
/*!40000 ALTER TABLE `biometric_templates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `companies`
--

DROP TABLE IF EXISTS `companies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `companies` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(50) DEFAULT NULL,
  `address` varchar(200) DEFAULT NULL,
  `website` varchar(100) DEFAULT NULL,
  `logo_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_companies_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `companies`
--

LOCK TABLES `companies` WRITE;
/*!40000 ALTER TABLE `companies` DISABLE KEYS */;
INSERT INTO `companies` (`id`, `name`, `code`, `address`, `website`, `logo_path`) VALUES (1,'TechSur SRL',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `companies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departments`
--

DROP TABLE IF EXISTS `departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `departments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(50) DEFAULT NULL,
  `company_id` int(11) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `company_id` (`company_id`),
  KEY `parent_id` (`parent_id`),
  KEY `ix_departments_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departments`
--

LOCK TABLES `departments` WRITE;
/*!40000 ALTER TABLE `departments` DISABLE KEYS */;
INSERT INTO `departments` (`id`, `name`, `code`, `company_id`, `parent_id`) VALUES (1,'Administracion',NULL,1,NULL);
INSERT INTO `departments` (`id`, `name`, `code`, `company_id`, `parent_id`) VALUES (2,'Produccion',NULL,1,NULL);
INSERT INTO `departments` (`id`, `name`, `code`, `company_id`, `parent_id`) VALUES (3,'Soporte Tecnico',NULL,1,NULL);
/*!40000 ALTER TABLE `departments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devices`
--

DROP TABLE IF EXISTS `devices`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `devices` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `ip` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `port` int(11) DEFAULT NULL,
  `password` int(11) DEFAULT NULL,
  `zone` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `zone_id` int(11) DEFAULT NULL,
  `enabled` tinyint(1) DEFAULT NULL,
  `serialnumber` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `device_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `platform` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `firmware_version` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mac` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_seen` datetime DEFAULT NULL,
  `last_error` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `user_count` int(11) DEFAULT NULL,
  `face_count` int(11) DEFAULT NULL,
  `fp_count` int(11) DEFAULT NULL,
  `transaction_count` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `zone_id` (`zone_id`),
  KEY `ix_devices_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devices`
--

LOCK TABLES `devices` WRITE;
/*!40000 ALTER TABLE `devices` DISABLE KEYS */;
INSERT INTO `devices` (`id`, `name`, `ip`, `port`, `password`, `zone`, `location`, `zone_id`, `enabled`, `serialnumber`, `device_name`, `platform`, `firmware_version`, `mac`, `last_seen`, `last_error`, `user_count`, `face_count`, `fp_count`, `transaction_count`, `created_at`) VALUES (1,'Main Door','192.168.1.201',4370,0,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,0,0,0,'2025-12-22 15:41:30');
/*!40000 ALTER TABLE `devices` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employees`
--

DROP TABLE IF EXISTS `employees`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `employees` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `department_id` int(11) DEFAULT NULL,
  `position_id` int(11) DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mobile_phone` varchar(50) DEFAULT NULL,
  `hire_date` date DEFAULT NULL,
  `address` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `photo_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `birthday` date DEFAULT NULL,
  `ssn` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_employees_user_id` (`user_id`),
  KEY `department_id` (`department_id`),
  KEY `position_id` (`position_id`),
  KEY `ix_employees_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employees`
--

LOCK TABLES `employees` WRITE;
/*!40000 ALTER TABLE `employees` DISABLE KEYS */;
INSERT INTO `employees` (`id`, `user_id`, `name`, `department_id`, `position_id`, `email`, `phone`, `mobile_phone`, `hire_date`, `address`, `city`, `country`, `photo_path`, `gender`, `birthday`, `ssn`, `active`) VALUES (1,'1','Ana Lopez',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1);
INSERT INTO `employees` (`id`, `user_id`, `name`, `department_id`, `position_id`, `email`, `phone`, `mobile_phone`, `hire_date`, `address`, `city`, `country`, `photo_path`, `gender`, `birthday`, `ssn`, `active`) VALUES (2,'2','Carlos Mendez',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1);
INSERT INTO `employees` (`id`, `user_id`, `name`, `department_id`, `position_id`, `email`, `phone`, `mobile_phone`, `hire_date`, `address`, `city`, `country`, `photo_path`, `gender`, `birthday`, `ssn`, `active`) VALUES (3,'3','Laura Perez',1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1);
INSERT INTO `employees` (`id`, `user_id`, `name`, `department_id`, `position_id`, `email`, `phone`, `mobile_phone`, `hire_date`, `address`, `city`, `country`, `photo_path`, `gender`, `birthday`, `ssn`, `active`) VALUES (4,'4','Juan Gomez',2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1);
INSERT INTO `employees` (`id`, `user_id`, `name`, `department_id`, `position_id`, `email`, `phone`, `mobile_phone`, `hire_date`, `address`, `city`, `country`, `photo_path`, `gender`, `birthday`, `ssn`, `active`) VALUES (5,'5','Marcos Diaz',2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1);
INSERT INTO `employees` (`id`, `user_id`, `name`, `department_id`, `position_id`, `email`, `phone`, `mobile_phone`, `hire_date`, `address`, `city`, `country`, `photo_path`, `gender`, `birthday`, `ssn`, `active`) VALUES (6,'6','Lucia Romero',2,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1);
INSERT INTO `employees` (`id`, `user_id`, `name`, `department_id`, `position_id`, `email`, `phone`, `mobile_phone`, `hire_date`, `address`, `city`, `country`, `photo_path`, `gender`, `birthday`, `ssn`, `active`) VALUES (7,'7','Sofia Torres',3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1);
INSERT INTO `employees` (`id`, `user_id`, `name`, `department_id`, `position_id`, `email`, `phone`, `mobile_phone`, `hire_date`, `address`, `city`, `country`, `photo_path`, `gender`, `birthday`, `ssn`, `active`) VALUES (8,'8','Pedro Sanchez',3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1);
INSERT INTO `employees` (`id`, `user_id`, `name`, `department_id`, `position_id`, `email`, `phone`, `mobile_phone`, `hire_date`, `address`, `city`, `country`, `photo_path`, `gender`, `birthday`, `ssn`, `active`) VALUES (9,'9','Valentina Rios',3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1);
INSERT INTO `employees` (`id`, `user_id`, `name`, `department_id`, `position_id`, `email`, `phone`, `mobile_phone`, `hire_date`, `address`, `city`, `country`, `photo_path`, `gender`, `birthday`, `ssn`, `active`) VALUES (10,'10','Diego Fernandez',3,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,1);
/*!40000 ALTER TABLE `employees` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `import_batches`
--

DROP TABLE IF EXISTS `import_batches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `import_batches` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) DEFAULT NULL,
  `imported_at` datetime DEFAULT current_timestamp(),
  `count` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `device_id` (`device_id`),
  KEY `ix_import_batches_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `import_batches`
--

LOCK TABLES `import_batches` WRITE;
/*!40000 ALTER TABLE `import_batches` DISABLE KEYS */;
INSERT INTO `import_batches` (`id`, `device_id`, `imported_at`, `count`) VALUES (1,1,'2026-01-07 17:55:07',54);
/*!40000 ALTER TABLE `import_batches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `job_logs`
--

DROP TABLE IF EXISTS `job_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `job_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `job_id` varchar(36) NOT NULL,
  `device_id` int(11) DEFAULT NULL,
  `level` varchar(20) DEFAULT NULL,
  `message` text NOT NULL,
  `timestamp` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `job_id` (`job_id`),
  KEY `ix_job_logs_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `job_logs`
--

LOCK TABLES `job_logs` WRITE;
/*!40000 ALTER TABLE `job_logs` DISABLE KEYS */;
INSERT INTO `job_logs` (`id`, `job_id`, `device_id`, `level`, `message`, `timestamp`) VALUES (1,'b15a6dac-2928-48aa-82f8-b6a9de32a15b',1,'INFO','Iniciando importaci├│n desde 192.168.1.201:4370...','2026-01-07 17:55:05');
INSERT INTO `job_logs` (`id`, `job_id`, `device_id`, `level`, `message`, `timestamp`) VALUES (2,'b15a6dac-2928-48aa-82f8-b6a9de32a15b',1,'INFO','Borrar despu├®s de descargar: No','2026-01-07 17:55:05');
INSERT INTO `job_logs` (`id`, `job_id`, `device_id`, `level`, `message`, `timestamp`) VALUES (3,'b15a6dac-2928-48aa-82f8-b6a9de32a15b',1,'INFO','Se obtuvieron 54 registros del dispositivo.','2026-01-07 17:55:07');
INSERT INTO `job_logs` (`id`, `job_id`, `device_id`, `level`, `message`, `timestamp`) VALUES (4,'b15a6dac-2928-48aa-82f8-b6a9de32a15b',1,'INFO','Guardados 54 nuevos registros en base de datos.','2026-01-07 17:55:07');
/*!40000 ALTER TABLE `job_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jobs`
--

DROP TABLE IF EXISTS `jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `jobs` (
  `id` varchar(36) NOT NULL,
  `type` varchar(50) NOT NULL,
  `device_id` int(11) DEFAULT NULL,
  `status` enum('PENDING','RUNNING','COMPLETED','FAILED','CANCELLED') DEFAULT NULL,
  `progress` int(11) DEFAULT NULL,
  `started_at` datetime DEFAULT NULL,
  `finished_at` datetime DEFAULT NULL,
  `error` text DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `device_id` (`device_id`),
  KEY `ix_jobs_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jobs`
--

LOCK TABLES `jobs` WRITE;
/*!40000 ALTER TABLE `jobs` DISABLE KEYS */;
INSERT INTO `jobs` (`id`, `type`, `device_id`, `status`, `progress`, `started_at`, `finished_at`, `error`, `created_at`) VALUES ('b15a6dac-2928-48aa-82f8-b6a9de32a15b','import_attendance',1,'COMPLETED',100,'2026-01-07 17:55:05','2026-01-07 17:55:07',NULL,'2026-01-07 17:55:05');
/*!40000 ALTER TABLE `jobs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `positions`
--

DROP TABLE IF EXISTS `positions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `positions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(50) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_positions_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `positions`
--

LOCK TABLES `positions` WRITE;
/*!40000 ALTER TABLE `positions` DISABLE KEYS */;
/*!40000 ALTER TABLE `positions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `settings` (
  `key` varchar(50) NOT NULL,
  `value` varchar(255) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`key`),
  KEY `ix_settings_key` (`key`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `device_id` int(11) NOT NULL,
  `uid` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `privilege` int(11) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  `group_id` int(11) DEFAULT NULL,
  `user_id` varchar(50) DEFAULT NULL,
  `card` varchar(50) DEFAULT NULL,
  `finger_count` int(11) DEFAULT 0,
  `face_count` int(11) DEFAULT 0,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uix_device_uid` (`device_id`,`uid`),
  KEY `ix_users_id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` (`id`, `device_id`, `uid`, `name`, `privilege`, `password`, `group_id`, `user_id`, `card`, `finger_count`, `face_count`, `updated_at`) VALUES (1,1,1,'Ana Lopez',0,NULL,NULL,'1',NULL,0,0,NULL);
INSERT INTO `users` (`id`, `device_id`, `uid`, `name`, `privilege`, `password`, `group_id`, `user_id`, `card`, `finger_count`, `face_count`, `updated_at`) VALUES (2,1,2,'Carlos Mendez',0,NULL,NULL,'2',NULL,0,0,NULL);
INSERT INTO `users` (`id`, `device_id`, `uid`, `name`, `privilege`, `password`, `group_id`, `user_id`, `card`, `finger_count`, `face_count`, `updated_at`) VALUES (3,1,3,'Laura Perez',0,NULL,NULL,'3',NULL,0,0,NULL);
INSERT INTO `users` (`id`, `device_id`, `uid`, `name`, `privilege`, `password`, `group_id`, `user_id`, `card`, `finger_count`, `face_count`, `updated_at`) VALUES (4,1,4,'Juan Gomez',0,NULL,NULL,'4',NULL,0,0,NULL);
INSERT INTO `users` (`id`, `device_id`, `uid`, `name`, `privilege`, `password`, `group_id`, `user_id`, `card`, `finger_count`, `face_count`, `updated_at`) VALUES (5,1,5,'Marcos Diaz',0,NULL,NULL,'5',NULL,0,0,NULL);
INSERT INTO `users` (`id`, `device_id`, `uid`, `name`, `privilege`, `password`, `group_id`, `user_id`, `card`, `finger_count`, `face_count`, `updated_at`) VALUES (6,1,6,'Lucia Romero',0,NULL,NULL,'6',NULL,0,0,NULL);
INSERT INTO `users` (`id`, `device_id`, `uid`, `name`, `privilege`, `password`, `group_id`, `user_id`, `card`, `finger_count`, `face_count`, `updated_at`) VALUES (7,1,7,'Sofia Torres',0,NULL,NULL,'7',NULL,0,0,NULL);
INSERT INTO `users` (`id`, `device_id`, `uid`, `name`, `privilege`, `password`, `group_id`, `user_id`, `card`, `finger_count`, `face_count`, `updated_at`) VALUES (8,1,8,'Pedro Sanchez',0,NULL,NULL,'8',NULL,0,0,NULL);
INSERT INTO `users` (`id`, `device_id`, `uid`, `name`, `privilege`, `password`, `group_id`, `user_id`, `card`, `finger_count`, `face_count`, `updated_at`) VALUES (9,1,9,'Valentina Rios',0,NULL,NULL,'9',NULL,0,0,NULL);
INSERT INTO `users` (`id`, `device_id`, `uid`, `name`, `privilege`, `password`, `group_id`, `user_id`, `card`, `finger_count`, `face_count`, `updated_at`) VALUES (10,1,10,'Diego Fernandez',0,NULL,NULL,'10',NULL,0,0,NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `zones`
--

DROP TABLE IF EXISTS `zones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `zones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `code` varchar(50) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_zones_id` (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `zones`
--

LOCK TABLES `zones` WRITE;
/*!40000 ALTER TABLE `zones` DISABLE KEYS */;
/*!40000 ALTER TABLE `zones` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-01-19 14:50:23
