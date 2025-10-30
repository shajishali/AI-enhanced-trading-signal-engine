# AWS S3 Integration Guide for AI Trading Engine

This guide explains how to set up and use AWS S3 for file storage in your AI Trading Engine project.

## Overview

The AI Trading Engine now supports AWS S3 for storing:
- Static files (CSS, JavaScript, images)
- Media files (user uploads, charts, reports)
- ML models
- Logs and backups

## Prerequisites

1. **AWS Account**: You need an active AWS account
2. **S3 Bucket**: Create an S3 bucket for your project
3. **IAM User**: Create an IAM user with S3 permissions
4. **AWS Credentials**: Access key ID and secret access key

## AWS Setup

### 1. Create S3 Bucket

1. Log into AWS Console
2. Navigate to S3 service
3. Click "Create bucket"
4. Choose a unique bucket name (e.g., `ai-trading-engine-prod`)
5. Select region (recommended: `us-east-1`)
6. Configure bucket settings:
   - **Versioning**: Enable
   - **Server-side encryption**: Enable
   - **Public access**: Block all public access
   - **Bucket policy**: Configure for your application

### 2. Create IAM User

1. Navigate to IAM service
2. Click "Users" → "Create user"
3. Username: `ai-trading-engine-s3-user`
4. Attach policies:
   - `AmazonS3FullAccess` (or create custom policy)
5. Create access keys
6. Save the Access Key ID and Secret Access Key

### 3. Bucket Policy (Optional)

For additional security, create a bucket policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowAIEngineAccess",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:user/ai-trading-engine-s3-user"
            },
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name",
                "arn:aws:s3:::your-bucket-name/*"
            ]
        }
    ]
}
```

## Project Configuration

### 1. Environment Variables

Add these to your `env.production` file:

```bash
# AWS S3 Configuration
USE_S3=True
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_STORAGE_BUCKET_NAME=your-s3-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

### 2. Install Dependencies

The required packages are already added to `requirements.txt`:

```bash
pip install django-storages boto3
```

### 3. Django Settings

S3 configuration is already set up in:
- `ai_trading_engine/settings.py` (development)
- `ai_trading_engine/settings_production.py` (production)

## Deployment

### 1. Using the Deployment Script

Run the comprehensive deployment script:

```bash
python deploy_to_s3.py --settings=ai_trading_engine.settings_production
```

This script will:
- Test S3 connection
- Create directory structure
- Collect static files
- Migrate existing media files
- Clean up local files

### 2. Using Management Commands

Test S3 connection:
```bash
python manage.py s3_manage test
```

Migrate files:
```bash
python manage.py s3_manage migrate
```

List files:
```bash
python manage.py s3_manage list
```

Upload specific file:
```bash
python manage.py s3_manage upload --file-path=local/file.txt --s3-key=media/file.txt
```

### 3. Manual Steps

If you prefer manual setup:

1. **Collect static files**:
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Migrate media files**:
   ```bash
   python manage.py s3_manage migrate
   ```

3. **Test deployment**:
   ```bash
   python manage.py s3_manage test
   ```

## S3 Directory Structure

Your S3 bucket will have this structure:

```
your-bucket/
├── static/                 # Static files (CSS, JS, images)
│   ├── admin/
│   ├── rest_framework/
│   └── ...
├── media/                  # User uploads and generated files
│   ├── models/            # ML models
│   ├── charts/            # Chart images
│   ├── reports/           # Generated reports
│   └── backups/           # Database backups
└── logs/                  # Application logs
```

## Celery Tasks

The following Celery tasks are available for S3 operations:

- `upload_file_to_s3_task(file_path, s3_key)`: Upload file to S3
- `download_file_from_s3_task(s3_key, local_path)`: Download file from S3
- `migrate_local_files_to_s3_task()`: Migrate existing files
- `cleanup_s3_files_task()`: Clean up old files

## Code Changes

The following files have been updated to use S3:

- `apps/signals/ml_model_training_service.py`: ML model storage
- `apps/signals/performance_optimization_service.py`: Model optimization
- `apps/data/tasks.py`: S3 Celery tasks

## Monitoring and Maintenance

### 1. CloudWatch Monitoring

Set up CloudWatch to monitor:
- S3 request metrics
- Storage usage
- Error rates

### 2. Cost Optimization

Configure S3 lifecycle policies:
- Move old files to cheaper storage classes
- Delete temporary files automatically
- Archive old logs

### 3. Backup Strategy

- Enable S3 versioning
- Set up cross-region replication
- Regular backup verification

## Troubleshooting

### Common Issues

1. **Access Denied**: Check IAM permissions
2. **Bucket Not Found**: Verify bucket name and region
3. **Connection Timeout**: Check network and AWS service status
4. **File Not Found**: Verify S3 key paths

### Debug Commands

Test S3 connection:
```bash
python manage.py s3_manage test
```

Check configuration:
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.AWS_STORAGE_BUCKET_NAME)
```

### Logs

Check application logs for S3-related errors:
```bash
tail -f logs/trading_engine.log | grep -i s3
```

## Security Best Practices

1. **Use IAM Roles**: Instead of access keys when possible
2. **Least Privilege**: Grant minimal required permissions
3. **Encryption**: Enable server-side encryption
4. **Access Logging**: Enable S3 access logging
5. **Regular Rotation**: Rotate access keys regularly

## Performance Optimization

1. **CloudFront CDN**: Use CloudFront for static files
2. **Compression**: Enable S3 compression
3. **Caching**: Set appropriate cache headers
4. **Regional Buckets**: Use buckets close to your users

## Cost Management

1. **Storage Classes**: Use appropriate storage classes
2. **Lifecycle Policies**: Automate file transitions
3. **Monitoring**: Set up billing alerts
4. **Cleanup**: Regular cleanup of temporary files

## Support

For issues related to S3 integration:
1. Check AWS CloudWatch logs
2. Review Django application logs
3. Test S3 connection using management commands
4. Verify IAM permissions and bucket policies

## Next Steps

After successful S3 setup:
1. Set up CloudFront CDN
2. Configure monitoring and alerting
3. Implement backup strategies
4. Optimize costs with lifecycle policies
5. Set up automated cleanup tasks



















