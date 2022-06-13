#!/usr/bin/env bash

RUN_DATE=$(date +"%Y-%m-%d")

BUCKET=deliverer-data-lake

echo "Starting: Daily Mongo Deliverer Process - ${RUN_DATE}"

aws emr create-cluster \
--no-termination-protected \
--applications Name=Hadoop Name=Hive Name=Spark Name=Tez Name=Presto \
--release-label emr-6.6.0 \
--ec2-attributes '{Subnets e SecGroups}' \
--log-uri 'log_paths' \
--steps '[{"Args":["hive-script","--run-hive-script","--args","-f","s3://${BUCKET}/hive/hive_deliverer_location.hql"],"Type":"CUSTOM_JAR","ActionOnFailure":"TERMINATE_CLUSTER","Jar":"command-runner.jar","Properties":"","Name":"Deliverer Location Hive"}
,{"Args":["spark-submit","--deploy-mode","cluster","s3://${BUCKET}/process/deliverer_location_process.py"],"Type":"CUSTOM_JAR","ActionOnFailure":"CONTINUE","Jar":"command-runner.jar","Properties":"","Name":"Deliverer Location Process}
]' \
--configurations 'configs.json' \
--auto-terminate \
--instance-fleets '[
Fleet configs because fleets are better if any machine is not available, it selects another
]' \
--bootstrap-actions '[
any_dependencies needed to process the data
]' \
--ebs-root-volume-size SIZE \
--service-role Role \
--enable-debugging \
--name "Daily Mongo Deliverer Process- ${RUN_DATE}" \
--scale-down-behavior TERMINATE_AT_TASK_COMPLETION \
--region region \
--profile profile
