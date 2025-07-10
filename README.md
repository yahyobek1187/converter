# Telegram File Converter Bot

A Python Telegram bot that converts files between different formats using various libraries.

## Features

- **Document Conversion**: PDF ↔ DOCX ↔ TXT
- **Image Conversion**: JPG ↔ PNG ↔ WEBP  
- **Audio Conversion**: MP3 ↔ WAV ↔ OGG
- **Video to Audio**: MP4 → MP3

## Setup

1. Get a bot token from [@BotFather](https://t.me/BotFather) on Telegram
2. Add your bot token to the environment variables as `BOT_TOKEN`
3. Run the bot using the configured workflow

## Usage

1. Send `/start` to see the welcome message
2. Send any supported file to the bot
3. Choose your desired conversion format from the inline buttons
4. Download the converted file

## Supported Conversions

| From | To |
|------|-----|
| PDF | DOCX, TXT |
| DOCX | PDF, TXT |
| TXT | DOCX |
| JPG/JPEG | PNG, WEBP |
| PNG | JPG, WEBP |
| WEBP | JPG, PNG |
| MP3 | WAV, OGG |
| WAV | MP3, OGG |
| OGG | MP3, WAV |
| MP4 | MP3 |

## Project Structure

```
├── main.py              # Main bot application
├── utils/
│   ├── __init__.py
│   └── converters.py    # File conversion utilities
├── temp/                # Temporary file storage
├── .env                 # Environment variables
└── README.md           # This file
```

## Dependencies

All dependencies are automatically managed by Replit. The main libraries used:

- `python-telegram-bot` - Telegram Bot API
- `pdf2docx` - PDF to DOCX conversion
- `python-docx` - DOCX manipulation
- `Pillow` - Image processing
- `pydub` - Audio conversion
- `moviepy` - Video processing
- `reportlab` - PDF generation