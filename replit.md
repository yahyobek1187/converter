# Overview

This repository contains a fully functional Telegram bot that provides file conversion services. The bot allows users to convert files between various formats including PDF/DOCX/TXT documents, image formats (JPG/PNG/WEBP), audio formats (MP3/WAV/OGG), and video to audio conversion (MP4 to MP3). 

**Status**: ✅ Bot is running successfully and actively handling user requests.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

The application follows a simple modular architecture with clear separation of concerns:

## Core Components
- **Main Bot Application** (`main.py`): Contains the Telegram bot logic, command handlers, and user interaction flows
- **Conversion Utilities** (`utils/converters.py`): Handles the actual file conversion operations between different formats
- **Environment Configuration**: Uses environment variables for sensitive configuration like bot tokens

## Technology Stack
- **Bot Framework**: Python Telegram Bot (python-telegram-bot library)
- **File Processing Libraries**:
  - `pdf2docx`: PDF to DOCX conversion
  - `python-docx`: DOCX document manipulation
  - `Pillow (PIL)`: Image format conversions
  - `pydub`: Audio format conversions
  - `moviepy`: Video to audio conversion
- **Environment Management**: `python-dotenv` for configuration
- **Logging**: Built-in Python logging for monitoring and debugging

# Key Components

## Telegram Bot Handler (`main.py`)
- Implements command handlers for `/start` and `/help` commands
- Provides user-friendly interface with inline keyboards for conversion options
- Manages the conversation flow and file handling
- Includes proper error handling and user feedback

## File Converter (`utils/converters.py`)
- Centralized conversion logic with support for multiple file formats
- Conversion matrix system that defines supported format transformations
- Temporary file management with automatic cleanup
- Extensible design for adding new conversion types

## Supported Conversions
The system supports a comprehensive matrix of file conversions:
- **Documents**: PDF ↔ DOCX ↔ TXT
- **Images**: JPG ↔ PNG ↔ WEBP
- **Audio**: MP3 ↔ WAV ↔ OGG
- **Video to Audio**: MP4 → MP3

# Data Flow

1. **User Interaction**: User sends a file to the Telegram bot
2. **File Reception**: Bot receives and temporarily stores the file
3. **Format Detection**: System identifies the file format and available conversions
4. **User Selection**: Bot presents conversion options via inline keyboard
5. **Conversion Processing**: Selected conversion is executed using appropriate libraries
6. **Result Delivery**: Converted file is sent back to the user
7. **Cleanup**: Temporary files are automatically removed

# External Dependencies

## Required Libraries
- `python-telegram-bot`: Telegram Bot API wrapper
- `pdf2docx`: PDF to Word document conversion
- `python-docx`: Microsoft Word document handling
- `Pillow`: Image processing and format conversion
- `pydub`: Audio file manipulation
- `moviepy`: Video processing for audio extraction
- `python-dotenv`: Environment variable management

## External Services
- **Telegram Bot API**: Primary interface for user interactions
- **File Storage**: Temporary local storage for processing files

# Deployment Strategy

## Environment Configuration
- Bot token must be provided via `BOT_TOKEN` environment variable
- Uses `.env` file for local development configuration
- Includes comprehensive error handling for missing configuration

## Runtime Requirements
- Python 3.7+ environment
- All required libraries installed via requirements management
- Sufficient disk space for temporary file processing
- Network access to Telegram Bot API

## Error Handling
- Graceful handling of missing dependencies with informative error messages
- Automatic cleanup of temporary files to prevent storage issues
- Comprehensive logging for monitoring and debugging
- User-friendly error messages for conversion failures

## Scalability Considerations
- Stateless design allows for easy horizontal scaling
- Temporary file cleanup prevents storage accumulation
- Modular architecture supports adding new conversion types
- Asynchronous handling for improved performance under load