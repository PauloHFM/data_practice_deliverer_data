#!/usr/bin/env pyspark
# -*- coding:utf-8 -*-

from datetime import date, datetime

from pyspark import HiveContext, SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.types import *

date_today = datetime.now().date()

date_earlier = date_today - timedelta(days=1)

spark = (
    SparkSession.builder.appName("Deliverer Location Process - {0}".format(date_today))
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .enableHiveSupport()
    .getOrCreate()
)

deliverer_location_data = spark.sql(
    """
  SELECT
  order_id,
  deliverer_id,
  delivery_state,
  timestamp,
  latitude,
  latitude
  FROM deliverer_data.deliverer_location
  WHERE timestamp BETWEEN '{0}' AND '{1}'
  -- more treatments here if needed
""".format(date_earlier, date_today)
)

deliverer_location_data.write.mode("overwrite").format("parquet").saveAsTable(
    "deliverer_location",
    path=f"s3://deliverer-data-lake/treated/internal/deliverer_location/run={date_today}",
)


# Example of final tables
deliverer_location_aggregated = spark.sql(
    """
  SELECT
  CAST(timestamp AS DATE) AS date_deliver,
  delivery_state,
  COUNT(DISTINCT order_id) AS count_orders,
  COUNT(DISTINCT deliverer_id) AS count_distinct_deliverers,
  FROM deliverer_data.deliverer_location -- could be from treated and other tables
  GROUP BY
    CAST(timestamp AS DATE),
    delivery_state
"""
)

deliverer_location_aggregated.write.mode("overwrite").format("parquet").saveAsTable(
    "deliverer_location_aggregated",
    path=f"s3://deliverer-data-lake/final/internal/deliverer_location_aggregated",
)

spark.stop()
exit()
