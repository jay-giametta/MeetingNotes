import boto3
import json
import os

s3 = boto3.client('s3')

# Configuration from environment variables
TRANSCRIPTS_PLAIN_PREFIX = os.environ.get('S3_TRANSCRIPTS_PLAIN_PREFIX', 'transcripts_plain/')

def lambda_handler(event, context):
    # Get file info
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    filename = os.path.basename(key).replace('.json', '')
    
    # Download and parse JSON
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = json.loads(obj['Body'].read().decode('utf-8'))
    
    items = data['results']['items']
    segments = data['results'].get('speaker_labels', {}).get('segments', [])
    
    # Build transcript
    transcript = []
    current_speaker = None
    
    for item in items:
        if item.get('type') == 'pronunciation':
            speaker = item.get('speaker_label', 'Unknown')
            word = item['alternatives'][0]['content']
            
            # Add speaker label when speaker changes
            if speaker != current_speaker:
                transcript.append(f"\n\n[Speaker {speaker.replace('spk_', '')}]: {word}")
                current_speaker = speaker
            else:
                transcript.append(f" {word}")
        
        elif item.get('type') == 'punctuation':
            transcript.append(item['alternatives'][0]['content'])
    
    # Save to S3
    output_key = f"{TRANSCRIPTS_PLAIN_PREFIX}{filename}.txt"
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=''.join(transcript).strip(),
        ContentType='text/plain'
    )
    
    return {'statusCode': 200}