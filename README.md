# Meeting Notes Automation

An AWS serverless pipeline that automatically transcribes meeting recordings and generates structured meeting notes using AI.

## Overview

This project processes audio/video meeting recordings through a multi-stage pipeline:

1. **Transcription** - Converts audio to text with speaker identification
2. **Parsing** - Formats raw transcription into readable text
3. **AI Processing** - Generates structured meeting notes using Claude
4. **Email Delivery** - Sends formatted notes via email

## Architecture

The system uses four AWS Lambda functions triggered by S3 events:

```
Audio File Upload
    ↓
MeetingNotesTranscribe (AWS Transcribe)
    ↓
transcripts_json/*.json
    ↓
MeetingNotesParseTranscribe (Format)
    ↓
transcripts_plain/*.txt
    ↓
MeetingNotesBedrock (Claude AI)
    ↓
notes_output/*.txt
    ↓
MeetingNotesEmail (SES)
```

## Lambda Functions

### MeetingNotesTranscribe
- **Trigger**: Audio/video file upload to S3
- **Purpose**: Initiates AWS Transcribe job with speaker identification
- **Output**: JSON transcription in `transcripts_json/`
- **Features**: Supports multiple audio formats, identifies up to 10 speakers

### MeetingNotesParseTranscribe
- **Trigger**: JSON file creation in `transcripts_json/`
- **Purpose**: Converts JSON transcription to readable plain text
- **Output**: Formatted transcript in `transcripts_plain/`
- **Features**: Speaker labels, proper punctuation

### MeetingNotesBedrock
- **Trigger**: Plain text transcript in `transcripts_plain/`
- **Purpose**: Generates structured meeting notes using Claude AI
- **Output**: Formatted notes in `notes_output/`
- **Model**: Claude Sonnet 4.5
- **Features**:
  - Extracts meeting date and context from filename
  - Identifies attendees who spoke
  - Organizes notes by topic with hierarchical structure
  - Captures action items and next steps
  - Filters out irrelevant information

### MeetingNotesEmail
- **Trigger**: Notes file creation in `notes_output/`
- **Purpose**: Emails formatted notes to recipient
- **Service**: AWS SES
- **Features**: Attaches notes as file with original filename

## File Naming Convention

Audio files should follow this pattern for optimal metadata extraction:
```
{customer}-{YYYYMMDD}-{description}.{ext}
```

Example: `HealthcareOrg-20241022-weekly-sync.mp3`

## Meeting Notes Format

Generated notes include:

- **Date & Context**: Extracted from filename and transcript
- **Attendees**: Only people who actively spoke
- **Notes**: Organized by topic with hierarchical bullets
  - Current state and baseline
  - Requirements and decisions
  - Planning considerations
  - Open questions
- **Way Ahead**: Action items with owners and deadlines

## AWS Services Used

- **S3**: Storage for audio files, transcripts, and notes
- **Lambda**: Serverless compute for each processing stage
- **Transcribe**: Speech-to-text with speaker diarization
- **Bedrock**: Claude AI for intelligent note generation
- **SES**: Email delivery

## Configuration

All configuration is managed through Lambda environment variables. Each function uses sensible defaults but can be customized:

### MeetingNotesTranscribe
- `TRANSCRIBE_LANGUAGE_CODE` (default: `en-US`)
- `TRANSCRIBE_MAX_SPEAKER_LABELS` (default: `10`)
- `TRANSCRIBE_SHOW_SPEAKER_LABELS` (default: `true`)
- `S3_TRANSCRIPTS_JSON_PREFIX` (default: `transcripts_json/`)

### MeetingNotesParseTranscribe
- `S3_TRANSCRIPTS_PLAIN_PREFIX` (default: `transcripts_plain/`)

### MeetingNotesBedrock
- `BEDROCK_MODEL_ID` (default: Claude Sonnet 4.5 ARN)
- `BEDROCK_MAX_TOKENS` (default: `64000`)
- `BEDROCK_TOP_P` (default: `0.9`)
- `S3_NOTES_OUTPUT_PREFIX` (default: `notes_output/`)

### MeetingNotesEmail
- `EMAIL_SENDER` (required: your verified SES email)
- `EMAIL_RECIPIENT` (required: recipient email)

### IAM Permissions Required

Each Lambda function needs a role with basic Lambda execution permissions plus:

- **MeetingNotesTranscribe**: S3 read/write, `transcribe:StartTranscriptionJob`
- **MeetingNotesParseTranscribe**: S3 read/write
- **MeetingNotesBedrock**: S3 read/write, `bedrock:InvokeModel`
- **MeetingNotesEmail**: S3 read, `ses:SendRawEmail`

## Deployment

### Prerequisites
1. AWS account with access to S3, Lambda, Transcribe, Bedrock, and SES
2. SES verified sender email address
3. S3 bucket for storing files

### Setup Steps

1. **Create S3 Bucket**
   - Create a single S3 bucket (e.g., `meeting-notes-pipeline`)
   - The pipeline will use prefixes to organize files

2. **Deploy Lambda Functions**
   - Package and deploy each Lambda function
   - Set environment variables (see `.env.example` for reference)
   - Configure timeout and memory:
     - MeetingNotesTranscribe: 60s, 256MB
     - MeetingNotesParseTranscribe: 60s, 256MB
     - MeetingNotesBedrock: 300s, 512MB
     - MeetingNotesEmail: 60s, 256MB
   - Attach IAM roles with appropriate permissions (S3, Transcribe, Bedrock, SES)

3. **Configure S3 Event Triggers**

   Each Lambda needs an S3 event notification trigger:

   **MeetingNotesTranscribe:**
   - Event type: `s3:ObjectCreated:*`
   - Prefix: `audio/` (or your chosen upload location)
   - Suffix: `.mp3`, `.wav`, `.m4a`, `.mp4`, etc. (add multiple triggers for different formats)

   **MeetingNotesParseTranscribe:**
   - Event type: `s3:ObjectCreated:*`
   - Prefix: `transcripts_json/`
   - Suffix: `.json`

   **MeetingNotesBedrock:**
   - Event type: `s3:ObjectCreated:*`
   - Prefix: `transcripts_plain/`
   - Suffix: `.txt`

   **MeetingNotesEmail:**
   - Event type: `s3:ObjectCreated:*`
   - Prefix: `notes_output/`
   - Suffix: `.txt`

4. **Test the Pipeline**
   - Upload an audio file to `s3://your-bucket/audio/customer-20241022-meeting.mp3`
   - Monitor CloudWatch Logs for each Lambda function
   - Verify files appear in each stage: `transcripts_json/` → `transcripts_plain/` → `notes_output/`
   - Check email for final notes

### S3 Bucket Structure

After processing, your bucket will contain:
```
your-bucket/
├── audio/
│   └── customer-20241022-meeting.mp3
├── transcripts_json/
│   └── customer-20241022-meeting-20241022-143022.json
├── transcripts_plain/
│   └── customer-20241022-meeting-20241022-143022.txt
└── notes_output/
    └── customer-20241022-meeting-20241022-143022.txt
```