# ---------------------------------------------------------------
# Wilson Bui
# The "S3-Ecryption-Script" python script
# Version 1.0 - 08/05/2019
# This script searches through a given default AWS Account's S3
# buckets and determines whether or not they are encrypted
# ---------------------------------------------------------------

import boto3
import botocore.client

"""
Instantiate AWS login and create boto3 client object
"""
aws_account = 'default'
boto3.setup_default_session(profile_name = aws_account)
s3 = boto3.client('s3')



def encrypted_buckets():
    """
    Returns a dictionary of all buckets that have encryption
    """
    aws_buckets = s3.list_buckets()['Buckets']
    bucket_list = {}

    for bucket in aws_buckets:
        try:
            bucket_encryption = s3.get_bucket_encryption(Bucket = bucket['Name'])\
                                ['ServerSideEncryptionConfiguration']['Rules'][0]\
                                ['ApplyServerSideEncryptionByDefault']['SSEAlgorithm']
            bucket_list[bucket['Name']] = bucket_encryption
        except:
            continue

    return bucket_list



def encrypted_objects_report(bucket_list, bucket, bucket_objects):
    """
    Primary business logic that generates basic reports regarding the following:
    1). Total objects found in each bucket (if objects > 1000, multiple reports)
    2). Total objects found that adhere to the AES256 SSE Protocol
    3). Total objects found that are unencrypted or do not adhere to AES256 SSE
    4). A basic list of objects that are not encrypted, if any
    """ 
    object_list = {}
    access = True

    for item in bucket_objects['Contents']:
        try:
            meta_data = s3.head_object(Bucket = bucket, Key = item['Key'])
        except:
            print ('\nYou are not allowed to access the bucket: ' + bucket.upper())
            access = False
            break
        
        if item['Size'] == 0:
            continue
        else:
            try:
                object_list[item['Key']] = meta_data['ServerSideEncryption']
            except:
                object_list[item['Key']] = ''

    if access == False:
        return
    else:
        objects_total = len(object_list)
        objects_aes256_encrypted = 0
        objects_kms_encrypted = 0
        objects_kms_encrypted_list = []
        objects_unencrypted = 0
        objects_unencrypted_list = []

        for item in object_list:
            if object_list[item].upper() == 'AES256':
                objects_aes256_encrypted = objects_aes256_encrypted + 1
            elif object_list[item].upper() == 'AWS:KMS':
                objects_kms_encrypted = objects_kms_encrypted + 1
                objects_kms_encrypted_list.append(item)
            else:
                objects_unencrypted = objects_unencrypted + 1
                objects_unencrypted_list.append(item)

        print ('\nReport for encrypted bucket: ' + bucket.upper() + ' - ' + bucket_list[bucket])
        print ('Total objects found: ' + str(objects_total))
        print ('Total AES256-SSE encrypted objects found: ' + str(objects_aes256_encrypted))
        print ('Total KMS-SSE encrypted objects found: ' + str(objects_kms_encrypted))
        print ('Total unencrypted objects found: ' + str(objects_unencrypted) + '\n')

        if objects_kms_encrypted > 0:
            print ('List of kms-encrypted objects:')
            for item in objects_kms_encrypted_list:
                print (item)
                
        if objects_unencrypted > 0:
            print ('\nList of unencrypted objects:')
            for item in objects_unencrypted_list:
                print (item)
                


def main():
    bucket_list = encrypted_buckets()
    
    for bucket in bucket_list:
        access = True
        bucket_objects = s3.list_objects_v2(Bucket=bucket)

        if bucket_objects['IsTruncated']:
            paginator = s3.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket = bucket)
            current_page = 0
            for page in page_iterator:
                current_page = current_page + 1
                print ("Page " + str(current_page) + " of the:")
                bucket_objects = page
                encrypted_objects_report(bucket_list, bucket, bucket_objects)
        else:
            encrypted_objects_report(bucket_list, bucket, bucket_objects)

"""
Main function call
"""
main()
