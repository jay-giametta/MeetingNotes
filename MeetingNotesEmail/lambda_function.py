import boto3
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

s3 = boto3.client('s3')
ses = boto3.client('ses')

# Configuration from environment variables
SENDER = os.environ.get('EMAIL_SENDER')
RECIPIENT = os.environ.get('EMAIL_RECIPIENT')

def lambda_handler(event, context):
    # Get file info
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    filename = os.path.basename(key)
    
    # Download file
    notes = s3.get_object(Bucket=bucket, Key=key)['Body'].read().decode('utf-8')
    
    # Create email
    msg = MIMEMultipart()
    msg['From'] = SENDER
    msg['To'] = RECIPIENT
    msg['Subject'] = filename
    msg.attach(MIMEText('Meeting notes attached.', 'plain'))
    
    # Attach file
    attachment = MIMEApplication(notes.encode('utf-8'))
    attachment.add_header('Content-Disposition', 'attachment', filename=filename)
    msg.attach(attachment)
    
    # Send
    ses.send_raw_email(
        Source=SENDER,
        Destinations=[RECIPIENT],
        RawMessage={'Data': msg.as_string()}
    )
    
    return {'statusCode': 200}