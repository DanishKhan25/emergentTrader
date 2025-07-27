#!/bin/bash

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="oracle_models_backup_$DATE.tar.gz"

echo "💾 CREATING ORACLE CLOUD BACKUP"
echo "Backup file: $BACKUP_FILE"

# Create compressed backup
echo "📦 Creating compressed backup..."
tar -czf $BACKUP_FILE \
    python_backend/models/ \
    python_backend/logs/ \
    --exclude="*.pyc" \
    --exclude="__pycache__"

BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
echo "✅ Backup created: $BACKUP_FILE ($BACKUP_SIZE)"

# Optional: Upload to Oracle Object Storage (requires OCI CLI setup)
if command -v oci &> /dev/null; then
    echo "☁️  Uploading to Oracle Object Storage..."
    
    # Create bucket if it doesn't exist
    oci os bucket create --name emergent-trader-backups --compartment-id YOUR_COMPARTMENT_ID 2>/dev/null || true
    
    # Upload backup
    oci os object put \
        --bucket-name emergent-trader-backups \
        --file $BACKUP_FILE \
        --name "backups/$BACKUP_FILE" \
        --force
    
    echo "✅ Backup uploaded to Object Storage"
    
    # Clean up local backup file
    rm $BACKUP_FILE
    echo "🧹 Local backup file cleaned up"
else
    echo "ℹ️  OCI CLI not configured. Backup saved locally: $BACKUP_FILE"
    echo "📋 To upload to Object Storage:"
    echo "   1. Install OCI CLI: bash -c \"\$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)\""
    echo "   2. Configure: oci setup config"
    echo "   3. Run this script again"
fi

echo ""
echo "📊 Backup Summary:"
echo "   File: $BACKUP_FILE"
echo "   Size: $BACKUP_SIZE"
echo "   Date: $(date)"
