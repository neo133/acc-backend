-- MariaDB dump 10.19  Distrib 10.5.15-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: acc
-- ------------------------------------------------------
-- Server version	10.5.15-MariaDB-0+deb11u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `bag_counting_master`
--

DROP TABLE IF EXISTS `bag_counting_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bag_counting_master` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vehicle_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `transaction_id` int(11) NOT NULL,
  `api_status` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bag_counting_master_FK` (`vehicle_id`),
  KEY `bag_counting_master_FK_1` (`transaction_id`),
  CONSTRAINT `bag_counting_master_FK` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicle_master` (`id`),
  CONSTRAINT `bag_counting_master_FK_1` FOREIGN KEY (`transaction_id`) REFERENCES `transaction_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `bag_counting_master`
--

LOCK TABLES `bag_counting_master` WRITE;
/*!40000 ALTER TABLE `bag_counting_master` DISABLE KEYS */;
INSERT INTO `bag_counting_master` VALUES (83,1,'2022-06-18 13:39:16',66,NULL),(84,1,'2022-06-18 13:39:24',66,NULL),(85,1,'2022-06-18 13:39:36',66,NULL);
/*!40000 ALTER TABLE `bag_counting_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `maintenance_master`
--

DROP TABLE IF EXISTS `maintenance_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `maintenance_master` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `printing_belt_id` int(11) DEFAULT NULL,
  `loader_belt_id` int(11) DEFAULT NULL,
  `reason` varchar(100) DEFAULT NULL,
  `duration` datetime NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `comment` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `maintenance_master_FK` (`printing_belt_id`),
  KEY `maintenance_master_FK_1` (`loader_belt_id`),
  CONSTRAINT `maintenance_master_FK` FOREIGN KEY (`printing_belt_id`) REFERENCES `printing_belt_master` (`id`),
  CONSTRAINT `maintenance_master_FK_1` FOREIGN KEY (`loader_belt_id`) REFERENCES `vehicle_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `maintenance_master`
--

LOCK TABLES `maintenance_master` WRITE;
/*!40000 ALTER TABLE `maintenance_master` DISABLE KEYS */;
INSERT INTO `maintenance_master` VALUES (1,NULL,2,'Belt camera not working','2022-06-17 19:49:00','Comment example','2022-06-17 11:20:58'),(2,NULL,1,'Belt camera not working','2022-06-17 18:58:00','comment','2022-06-17 11:28:35');
/*!40000 ALTER TABLE `maintenance_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `packer_master`
--

DROP TABLE IF EXISTS `packer_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `packer_master` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `machine_id` varchar(10) NOT NULL,
  `packer_type` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `packer_master_UN` (`machine_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `packer_master`
--

LOCK TABLES `packer_master` WRITE;
/*!40000 ALTER TABLE `packer_master` DISABLE KEYS */;
INSERT INTO `packer_master` VALUES (1,'p-100',0),(2,'p-101',0),(3,'p-102',1);
/*!40000 ALTER TABLE `packer_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `printing_belt_master`
--

DROP TABLE IF EXISTS `printing_belt_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `printing_belt_master` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `machine_id` varchar(10) NOT NULL,
  `packer_id` int(11) DEFAULT NULL,
  `is_active` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `printing_belt_master_UN` (`machine_id`),
  KEY `printing_belt_master_FK` (`packer_id`),
  CONSTRAINT `printing_belt_master_FK` FOREIGN KEY (`packer_id`) REFERENCES `packer_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `printing_belt_master`
--

LOCK TABLES `printing_belt_master` WRITE;
/*!40000 ALTER TABLE `printing_belt_master` DISABLE KEYS */;
INSERT INTO `printing_belt_master` VALUES (1,'pr-101',1,1),(2,'pr-102',1,1),(3,'pr-103',1,1),(4,'pr-104',2,1),(5,'pr-105',2,1),(6,'pr-106',3,1),(7,'pr-107',3,1),(8,'pr-108',3,1);
/*!40000 ALTER TABLE `printing_belt_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tag_counting_master`
--

DROP TABLE IF EXISTS `tag_counting_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tag_counting_master` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `printing_belt_id` int(11) NOT NULL,
  `transaction_id` int(11) NOT NULL,
  `is_labled` tinyint(4) NOT NULL DEFAULT 1,
  `local_image_location` varchar(300) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `api_status` int(11) DEFAULT NULL,
  `s3_image_location` varchar(300) DEFAULT NULL,
  `is_false_alert` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `tag_counting_master_FK` (`printing_belt_id`),
  KEY `tag_counting_master_FK_1` (`transaction_id`),
  CONSTRAINT `tag_counting_master_FK` FOREIGN KEY (`printing_belt_id`) REFERENCES `printing_belt_master` (`id`),
  CONSTRAINT `tag_counting_master_FK_1` FOREIGN KEY (`transaction_id`) REFERENCES `transaction_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tag_counting_master`
--

LOCK TABLES `tag_counting_master` WRITE;
/*!40000 ALTER TABLE `tag_counting_master` DISABLE KEYS */;
INSERT INTO `tag_counting_master` VALUES (88,1,66,1,NULL,'2022-06-18 13:39:20',NULL,NULL,0),(89,1,66,0,NULL,'2022-06-18 13:39:26',NULL,NULL,0),(90,1,66,1,NULL,'2022-06-18 13:39:32',NULL,NULL,0),(91,2,67,1,'','2022-06-20 03:55:52',NULL,'',0),(92,2,67,0,'','2022-06-20 03:55:52',NULL,'',0),(93,2,67,0,'','2022-06-20 03:55:52',NULL,'',0),(94,2,67,1,'','2022-06-20 03:55:52',NULL,'',0);
/*!40000 ALTER TABLE `tag_counting_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transaction_master`
--

DROP TABLE IF EXISTS `transaction_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `transaction_master` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `printing_belt_id` int(11) DEFAULT NULL,
  `vehicle_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `licence_number` varchar(100) DEFAULT NULL,
  `bag_type` varchar(100) DEFAULT NULL,
  `bag_count` int(11) DEFAULT NULL,
  `is_active` tinyint(4) DEFAULT 1,
  `stopped_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `transaction_master_FK` (`printing_belt_id`),
  KEY `transaction_master_FK_1` (`vehicle_id`),
  CONSTRAINT `transaction_master_FK` FOREIGN KEY (`printing_belt_id`) REFERENCES `printing_belt_master` (`id`),
  CONSTRAINT `transaction_master_FK_1` FOREIGN KEY (`vehicle_id`) REFERENCES `vehicle_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=75 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transaction_master`
--

LOCK TABLES `transaction_master` WRITE;
/*!40000 ALTER TABLE `transaction_master` DISABLE KEYS */;
INSERT INTO `transaction_master` VALUES (66,1,1,'2022-06-18 13:39:14','\'FDSOFJDS','ACC Gold',18,0,'2022-06-19 21:09:00'),(67,2,5,'2022-06-19 12:58:07','fdsf','ACC Suraksha',10,0,'2022-06-19 21:13:16'),(68,1,1,'2022-06-19 21:27:56','d231','ACC Gold',20,0,'2022-06-19 21:56:23'),(69,6,3,'2022-06-19 21:41:42','123d','ACC Suraksha',10,0,'2022-06-19 21:55:07'),(70,6,3,'2022-06-19 21:42:11','123d','ACC Suraksha',10,0,'2022-06-19 22:32:22'),(71,2,5,'2022-06-19 21:42:59','21f','ACC Suraksha',70,1,NULL),(72,4,6,'2022-06-19 21:43:52','21dsa','ACC Gold',3,1,NULL),(73,3,7,'2022-06-19 21:53:37','3ft','ACC Suraksha',670,1,NULL),(74,1,1,'2022-06-19 21:56:45','2313','ACC Suraksha',22,1,NULL);
/*!40000 ALTER TABLE `transaction_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_master`
--

DROP TABLE IF EXISTS `user_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_master` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(45) NOT NULL,
  `last_name` varchar(45) DEFAULT NULL,
  `phone_number` varchar(25) DEFAULT NULL,
  `email` varchar(45) NOT NULL,
  `password` varchar(100) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `role` varchar(50) DEFAULT 'user',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  UNIQUE KEY `phone_number_UNIQUE` (`phone_number`)
) ENGINE=InnoDB AUTO_INCREMENT=175 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_master`
--

LOCK TABLES `user_master` WRITE;
/*!40000 ALTER TABLE `user_master` DISABLE KEYS */;
INSERT INTO `user_master` VALUES (1,'Akshay','Chaturvedi','8057466860','akshay.chaturvedi@frinks.ai','$2a$10$kPCMB10Ift/mFl4Q9.6M3u7mOVCm464tetX2oLgthcnaJinnNQFLq','2022-06-13 08:05:45','2022-06-13 13:36:22','user');
/*!40000 ALTER TABLE `user_master` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vehicle_master`
--

DROP TABLE IF EXISTS `vehicle_master`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `vehicle_master` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `machine_id` varchar(10) NOT NULL,
  `vehicle_type` tinyint(4) NOT NULL,
  `container` int(11) DEFAULT NULL,
  `printing_belt_id` int(11) DEFAULT NULL,
  `is_active` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `vehicle_master_UN` (`machine_id`),
  KEY `vehicle_master_FK` (`printing_belt_id`),
  CONSTRAINT `vehicle_master_FK` FOREIGN KEY (`printing_belt_id`) REFERENCES `printing_belt_master` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vehicle_master`
--

LOCK TABLES `vehicle_master` WRITE;
/*!40000 ALTER TABLE `vehicle_master` DISABLE KEYS */;
INSERT INTO `vehicle_master` VALUES (1,'v-100',0,NULL,1,1),(2,'v-101',0,NULL,4,1),(3,'v-102',1,3,6,0),(5,'v-103',1,5,2,0),(6,'v-104',0,NULL,4,0),(7,'v-105',0,NULL,3,0);
/*!40000 ALTER TABLE `vehicle_master` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-06-20 17:40:00
