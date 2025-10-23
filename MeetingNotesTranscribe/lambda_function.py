import boto3
import os
from datetime import datetime

transcribe = boto3.client('transcribe')

# Configuration from environment variables
LANGUAGE_CODE = os.environ.get('TRANSCRIBE_LANGUAGE_CODE', 'en-US')
MAX_SPEAKER_LABELS = int(os.environ.get('TRANSCRIBE_MAX_SPEAKER_LABELS', '10'))
SHOW_SPEAKER_LABELS = os.environ.get('TRANSCRIBE_SHOW_SPEAKER_LABELS', 'true').lower() == 'true'
TRANSCRIPTS_JSON_PREFIX = os.environ.get('S3_TRANSCRIPTS_JSON_PREFIX', 'transcripts_json/')

def lambda_handler(event, context):
    # Get file info
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    # Generate unique job name
    filename = os.path.basename(key).rsplit('.', 1)[0]
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    job_name = f"{filename}-{timestamp}"
    
    # Get file format
    media_format = key.split('.')[-1].lower()
    
    # Start transcription
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': f"s3://{bucket}/{key}"},
        MediaFormat=media_format,
        LanguageCode=LANGUAGE_CODE,
        Settings={
            'ShowSpeakerLabels': SHOW_SPEAKER_LABELS,
            'MaxSpeakerLabels': MAX_SPEAKER_LABELS
        },
        OutputBucketName=bucket,
        OutputKey=f"{TRANSCRIPTS_JSON_PREFIX}{job_name}.json"
    )
    
    return {'statusCode': 200}