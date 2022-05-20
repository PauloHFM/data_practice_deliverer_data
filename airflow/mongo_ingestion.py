import pandas as pd
import pymongo
from pymongo import *
from bson.objectid import ObjectId
from datetime import datetime, timedelta, date
import logging
import boto3
import sqlalchemy
import argparse
import gzip

from credentials import credentials, incremental_fields

# Period of ingestion: Daily

parser = argparse.ArgumentParser(description='Deliverer Data Ingestion')
# parser.add_argument('-f", '--folder', required=True, help='Output folder')
parser.add_argument('-d', '--date', required=True, help='Date to RUN')
# parser.add_argument('-s', '--schema', required=True, help='Schema to import')
# parser.add_argument('-t', '--table', required=True, help='Table to import')
# parser.add_argument('-n', '--rows-batch', required=True, help='Records per batch')
args = vars(parser.parse_args())


logging.getLogger().setLevel(logging.INFO)


def get_collection_conn(table_info):
    """
    Return the collection connection on MongoDB.

    This function is mainly useful to preview the values of the
    Series without displaying all of it.

    Parameters
    ----------
    table_info : dict
        Dictionary containg many information about
        the connection to MongoDB desired:
        'host','port','schema','table',
        'incremental_field','date','next_date'

    Return
    ------
    pandas.Series
        Subset of the original series with the n first values.

    """
    client = MongoClient(
        f"mongodb://{table_info['host']}:{table_info['port']}/")
    database_conn = client[table_info['schema']]
    collection_conn = database_conn[table_info['table']]
    return collection_conn


def get_n_parts(table_info):
    rows_batch_mongo = '10000'

    collection_conn = get_collection_conn(table_info)

    if table_info['incremental_field'] is not None:
        count_docs = collection_conn.count_documents({table_info['incremental_field']: {
                                                     "$gte": table_info['date'], "$lt": table_info['next_date']}})
    else:
        count_docs = collection_conn.count_documents({})

    rows_number = int(rows_batch_mongo)
    number_parts = count_docs // rows_number if count_docs % rows_number == 0 else count_docs // rows_number + 1

    return number_parts


def get_part_incremental(table_info, part):
    rows_batch_mongo = '10000'

    rows_number = int(rows_batch_mongo)
    limit = int(rows_number)
    if part == 0:
        skip = 0
    elif part > 0:
        skip = (part * int(rows_number)) + 1
    else:
        part = 0

    collection_conn = get_collection_conn(table_info)
    query = collection_conn.find(
        {
            table_info['incremental_field']: {
                "$gte": table_info['date'], "$lt": table_info['next_date']}}).sort(
        "_id", -1).skip(skip).limit(limit)
    data = list(query)
    df = pd.DataFrame(data)

    return df


def write_compact_json(df, date, source, part):
    date_part = table_info['date'].strftime("%Y-%m-%d")
    file_name = '{0}-{1}-{2}-part_{3}.jsonl'.format(
        table_info['schema'], table_info['table'], date_part, str(part).zfill(6))

    with open(file_name, 'w', encoding='utf-8') as f:
        df.to_json(f, lines=True, orient='records', date_format='iso',
                   default_handler=str, force_ascii=False)
        f.write('\n')

    file_name_compress = file_name + '.gz'

    with open(file_name, 'rb') as f_in, gzip.open(file_name_compress, 'wb') as f_out:
        f_out.writelines(f_in)

    logging.info(f" File {file_name_compress} completed!")

    return file_name_compress


def upload_to_s3(file_name, bucket, table_info):
    # If S3 object_name was not specified, use file_name
    if table_info is None:
        object_name = file_name
    else:
        date_part = table_info['date'].strftime("%Y-%m-%d")
        object_name = f"raw/internal/{table_info['schema']}/{table_info['table']}/run={date_part}/{file_name}"

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        logging.info(f" {file_name} uploaded to {object_name}")
    except ClientError as e:
        logging.error(e)
        return False
    return True


day = datetime.strptime(args['date'], '%Y-%m-%d')

date = day.replace(hour=0, minute=0, second=0, microsecond=0)

next_date = date + timedelta(days=1)

bucket = 'deliverer-data-lake'

table_information = {
    'host': 'localhost',
    'port': '27017',
    'schema': 'deliverer_data',
    'table': 'deliverer_location',
    'incremental_field': 'timestamp',
    'date': date,
    'next_date': next_date,
}

now_table = datetime.now()
logging.info(f"  Processing: {schema}, {table} at {str(now_table)}")

number_parts = int(get_n_parts(table_information))

for part in range(number_parts):
    df_part = get_part_incremental(table_information, part)
    file_name = write_compact_json(df_part, table_information, part)
    upload_to_s3(file_name, bucket, table_information)

end_table = datetime.now()
logging.info(f"  Finished: {schema}, {table} at {str(end_table)}")
