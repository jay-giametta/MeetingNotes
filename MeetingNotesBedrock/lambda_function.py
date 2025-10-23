import json
import boto3
import os
from datetime import datetime
from prompt import PROMPT_TEMPLATE

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime')

# Configuration from environment variables
MODEL_ID = os.environ.get('BEDROCK_MODEL_ID')
MAX_TOKENS = int(os.environ.get('BEDROCK_MAX_TOKENS', '64000'))
TOP_P = float(os.environ.get('BEDROCK_TOP_P', '0.9'))
NOTES_OUTPUT_PREFIX = os.environ.get('S3_NOTES_OUTPUT_PREFIX', 'notes_output/')

# Prompt customization variables
ROLE = os.environ.get('PROMPT_ROLE', 'a professional')
TYPICAL_PARTICIPANTS = os.environ.get('PROMPT_TYPICAL_PARTICIPANTS', 'clients, partners, and team members')
FOCUS_AREAS = os.environ.get('PROMPT_FOCUS_AREAS', 'solutions, decisions, or project outcomes')
PRIORITIES = os.environ.get('PROMPT_PRIORITIES', 'requirements, technical constraints, business drivers, decision points')
ACTION_ITEMS_SCOPE = os.environ.get('PROMPT_ACTION_ITEMS_SCOPE', 'the team')
EXAMPLE_COMMITMENT = os.environ.get('PROMPT_EXAMPLE_COMMITMENT', 'Person will send document by Friday')
EXAMPLE_TENTATIVE = os.environ.get('PROMPT_EXAMPLE_TENTATIVE', 'Team to explore options (timeline TBD)')
EXAMPLE_CONDITIONAL = os.environ.get('PROMPT_EXAMPLE_CONDITIONAL', 'If approved, will schedule meeting in Q2')

def lambda_handler(event, context):
    # Get file info
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    filename = os.path.basename(key)
    
    # Download transcript
    obj = s3.get_object(Bucket=bucket, Key=key)
    transcript = obj['Body'].read().decode('utf-8')
    
    # Parse filename for metadata
    base_name = os.path.splitext(filename)[0]
    parts = base_name.split('-')
    
    # Find date in filename (YYYYMMDD format)
    date_str = ''
    customer = parts[0] if parts else 'unknown'
    
    for part in parts:
        if len(part) == 8 and part.isdigit():
            date_str = f"{part[0:4]}-{part[4:6]}-{part[6:8]}"
            break
    
    # Build AI prompt
    prompt = PROMPT_TEMPLATE.format(
        date=date_str,
        context=base_name,
        transcript=transcript,
        role=ROLE,
        typical_participants=TYPICAL_PARTICIPANTS,
        focus_areas=FOCUS_AREAS,
        priorities=PRIORITIES,
        action_items_scope=ACTION_ITEMS_SCOPE,
        example_commitment=EXAMPLE_COMMITMENT,
        example_tentative=EXAMPLE_TENTATIVE,
        example_conditional=EXAMPLE_CONDITIONAL
    )
    
    # Call Bedrock
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": MAX_TOKENS,
            "top_p": TOP_P,
            "messages": [{"role": "user", "content": prompt}]
        })
    )
    
    # Extract processed notes
    result = json.loads(response['body'].read())
    notes = result['content'][0]['text'].strip()
    
    # Save to S3
    output_key = f"{NOTES_OUTPUT_PREFIX}{filename}"
    s3.put_object(
        Bucket=bucket,
        Key=output_key,
        Body=notes,
        ContentType='text/plain',
        Metadata={
            'customer': customer,
            'meeting_date': date_str,
            'source_file': key,
            'processed_date': datetime.now().isoformat()
        }
    )
    
    return {'statusCode': 200}