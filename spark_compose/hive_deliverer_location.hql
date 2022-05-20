SET hive.exec.compress.output=true;

CREATE DATABASE IF NOT EXISTS `deliverer_data`
LOCATION 's3://deliverer-data-lake/raw/internal/deliverer_data'
;
DROP TABLE IF EXISTS `deliverer_data`.`deliverer_location`;
CREATE EXTERNAL TABLE `deliverer_data`.`deliverer_location`(
  `order_id` STRING COMMENT 'from deserializer', 
  `deliverer_id` STRING COMMENT 'from deserializer', 
  `delivery_state` STRING COMMENT 'from deserializer', 
  `timestamp` TIMESTAMP COMMENT 'from deserializer', 
  `latitude` FLOAT  COMMENT 'from deserializer', 
  `latitude` FLOAT COMMENT 'from deserializer'
PARTITIONED BY ( 
  `run` date)
ROW FORMAT SERDE 
  'org.openx.data.jsonserde.JsonSerDe' 
WITH SERDEPROPERTIES ( 
  'paths'='order_id,deliverer_id,delivery_state,timestamp,latitude,latitude') 
STORED AS INPUTFORMAT 
  'org.apache.hadoop.mapred.TextInputFormat' 
OUTPUTFORMAT 
  'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION
  's3://deliverer-data-lake/raw/internal/deliverer_data/deliverer_location'
TBLPROPERTIES (
  'classification'='json', 
  'compressionType'='gzip'
)
;
ALTER TABLE `deliverer_data`.`deliverer_location` SET SERDEPROPERTIES ( "ignore.malformed.json" = "true")
; 
MSCK REPAIR TABLE `deliverer_data`.`deliverer_location`
;