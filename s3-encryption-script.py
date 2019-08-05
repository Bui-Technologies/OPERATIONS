import boto3

account = 'aws-hhs-cms-amg-qpp-selfn'
bucket = 'qpp-cms-sn-uploads-impl'

boto3.setup_default_session(profile_name=account)
s3 = boto3.client('s3')
bucket_objects = s3.list_objects_v2(Bucket=bucket)

if bucket_objects['IsTruncated']:
    print('Warning this query response is truncated')
    
d = {}
for item in bucket_objects['Contents']:
    meta_data = s3.head_object(Bucket=bucket,Key=item['Key'])
    d[item['Key']] = meta_data['ServerSideEncryption']
    
for a in d:
    if d[a] != 'AES256':
        print(a,d[a])


