/*
SQLyog Community v13.1.2 (64 bit)
MySQL - 10.1.40-MariaDB : Database - econsig_db
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`econsig_db` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `econsig_db`;

/*Table structure for table `consulta` */

DROP TABLE IF EXISTS `consulta`;

CREATE TABLE `consulta` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cpf` text,
  `Matrícula` text,
  `Estabelecimento1` text,
  `Estabelecimento2` text,
  `Servidor` text,
  `Data de admissão - Categoria` text,
  `Margem Facultativa` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

/*Data for the table `consulta` */

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
