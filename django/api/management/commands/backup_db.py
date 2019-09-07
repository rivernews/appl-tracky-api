import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core import management
from django.core.mail import mail_admins

import boto3 
import botocore

import os

# django command: https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/
class Command(BaseCommand):
    OUTPUT_FILENAME = 'db_backup.json'
    DB_BACKUP_DESTINATION_BUCKET_NAME = 'appl-tracky-backup'
    DB_BACKUP_PATH = 'db-backup'
    S3_AWS_REGION = os.environ.get('AWS_REGION', 'us-east-2')

    def handle(self, *args, **options):
        try:
            # dump database data via django command
            # https://stackoverflow.com/a/20480323/9814131
            # https://stackoverflow.com/a/7003567/9814131
            mail_admins(
                subject='Starting DB Backup',
                message=f'The DB Backup cron job is about to start, you should see the result within a few minutes.'
            )


            # boto3 bucket
            # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#bucket


            self.stdout.write('INFO: starting Django command backup database...')


            hashed_filename = f'{datetime.datetime.utcnow().isoformat()}__{self.OUTPUT_FILENAME}'

            with open(hashed_filename, 'w') as f:
                management.call_command('dumpdata', stdout=f)
            

            s3_resource = boto3.resource('s3')

            exists = True
            accessible = True
            try:
                s3_resource.meta.client.head_bucket(Bucket=self.DB_BACKUP_DESTINATION_BUCKET_NAME)
                exists = accessible = True
            except botocore.exceptions.ClientError as e:
                # If a client error is thrown, then check that it was a 404 error.
                # If it was a 404 error, then the bucket does not exist.
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    self.stdout.write(f'Bucket {self.DB_BACKUP_DESTINATION_BUCKET_NAME} is not found.')
                    exists = False
                elif error_code == '403':
                    self.stdout.write(f'ERROR: you have no access to bucket {self.DB_BACKUP_DESTINATION_BUCKET_NAME}.')
                    accessible = False
            
            db_backup_bucket = s3_resource.Bucket(self.DB_BACKUP_DESTINATION_BUCKET_NAME)
            if not exists:
                db_backup_bucket.create(
                    ACL='private',
                    CreateBucketConfiguration={ 'LocationConstraint': self.S3_AWS_REGION }
                )
                exists = True

            if exists and accessible:
                self.stdout.write('INFO: confirm bucket exists and is accessible.')
                db_backup_bucket.upload_file(
                    hashed_filename,
                    f'{self.DB_BACKUP_PATH}/{hashed_filename}',
                )
                self.stdout.write('INFO: successfully backup database.')
                mail_admins(
                    subject='DB Backup Success',
                    message=f'DB backup succeed. Check it out on S3 console: https://s3.console.aws.amazon.com/s3/buckets/{self.DB_BACKUP_DESTINATION_BUCKET_NAME}/?region={self.S3_AWS_REGION}'
                )
            else:
                self.stdout.write(f'ERROR: error occured, see above message.')
                mail_admins(
                    subject='DB Backup Failed',
                    message=f'DB backup failed, here is more message: bucket name `{self.DB_BACKUP_DESTINATION_BUCKET_NAME}`, exists={exists}, accessible={accessible}. Check on the S3 console: https://s3.console.aws.amazon.com/s3/buckets/{self.DB_BACKUP_DESTINATION_BUCKET_NAME}/?region={self.S3_AWS_REGION}'
                )
        
        except Exception as e:
            self.stdout.write(f'ERROR: {repr(e)}')
            mail_admins(
                subject='DB Backup Failed',
                message='DB backup failed, here is more message: ' + repr(e) + f'; ==== end of error message ====; S3 bucket console: https://s3.console.aws.amazon.com/s3/buckets/{self.DB_BACKUP_DESTINATION_BUCKET_NAME}/?region={self.S3_AWS_REGION}',
            )