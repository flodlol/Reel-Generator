#!/bin/bash
# Quick Setup Helper for New Niches

echo "=========================================="
echo "Meme Video Generator - Niche Setup"
echo "=========================================="
echo ""

# Get niche name
read -p "Enter your niche name (e.g., Cat, Dog, Funny): " NICHE_NAME

# Clean the name
NICHE_NAME=$(echo "$NICHE_NAME" | tr -d ' ')
NICHE_FOLDER="data/niches/!${NICHE_NAME}"

# Check if already exists
if [ -d "$NICHE_FOLDER" ]; then
    echo ""
    echo "⚠️  Niche '$NICHE_NAME' already exists!"
    read -p "Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

echo ""
echo "Creating niche: $NICHE_NAME"
echo ""

# Create directories
mkdir -p "$NICHE_FOLDER"
mkdir -p "$NICHE_FOLDER/Raw-Images"
mkdir -p "$NICHE_FOLDER/Meme-Images"
mkdir -p "$NICHE_FOLDER/Meme-Fade"
mkdir -p "$NICHE_FOLDER/Meme-Final"
mkdir -p "$NICHE_FOLDER/Meme-Description"
mkdir -p "$NICHE_FOLDER/TikTok-Sounds"

echo "✓ Created folder structure"

# Copy templates
if [ ! -f "$NICHE_FOLDER/Credentials.json" ]; then
    cp config/credentials.template.json "$NICHE_FOLDER/Credentials.json"
    echo "✓ Created Credentials.json (PLEASE EDIT WITH YOUR INFO!)"
else
    echo "⚠️  Credentials.json already exists, not overwriting"
fi

if [ ! -f "$NICHE_FOLDER/Quotes.txt" ]; then
    cp config/quotes.template.txt "$NICHE_FOLDER/Quotes.txt"
    echo "✓ Created Quotes.txt template"
else
    echo "⚠️  Quotes.txt already exists, not overwriting"
fi

if [ ! -f "$NICHE_FOLDER/upload_log.json" ]; then
    cp config/upload_log.template.json "$NICHE_FOLDER/upload_log.json"
    echo "✓ Created upload_log.json"
else
    echo "⚠️  upload_log.json already exists, not overwriting"
fi

# Create .gitkeep files
touch "$NICHE_FOLDER/Raw-Images/.gitkeep"
touch "$NICHE_FOLDER/Meme-Images/.gitkeep"
touch "$NICHE_FOLDER/Meme-Fade/.gitkeep"
touch "$NICHE_FOLDER/Meme-Final/.gitkeep"
touch "$NICHE_FOLDER/Meme-Description/.gitkeep"

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit your credentials:"
echo "   nano $NICHE_FOLDER/Credentials.json"
echo ""
echo "2. Add your Firefox profile path (find it with):"
echo "   ls ~/Library/Application\\ Support/Firefox/Profiles/"
echo ""
echo "3. Add quotes:"
echo "   nano $NICHE_FOLDER/Quotes.txt"
echo ""
echo "4. Add images to:"
echo "   $NICHE_FOLDER/Raw-Images/"
echo ""
echo "5. Launch the app:"
echo "   ./launch.sh"
echo ""
