import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from utils.converters import FileConverter, get_supported_conversions, cleanup_temp_files

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")

# Initialize file converter
converter = FileConverter()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
🤖 **File Converter Bot**

Welcome! I can help you convert files between different formats.

**Supported conversions:**
📄 PDF ↔ DOCX, TXT
🖼️ JPG ↔ PNG, WEBP
🎵 MP3 ↔ WAV, OGG
🎬 MP4 → MP3
📝 TXT ↔ DOCX

Just send me a file and I'll show you available conversion options!
    """
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
**How to use:**
1. Send me any supported file
2. Choose conversion format from the menu
3. Download your converted file!

**Supported formats:**
• Documents: PDF, DOCX, TXT
• Images: JPG, PNG, WEBP
• Audio: MP3, WAV, OGG
• Video: MP4 (converts to audio)

**Tips:**
• Files are automatically deleted after conversion
• Maximum file size depends on Telegram limits
• Conversion may take a few moments for large files
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uploaded documents."""
    try:
        document = update.message.document
        if not document:
            await update.message.reply_text("❌ No document found in the message.")
            return

        # Get file extension
        file_name = document.file_name or "unknown"
        file_extension = os.path.splitext(file_name)[1].lower()
        
        if not file_extension:
            await update.message.reply_text("❌ Cannot determine file type. Please ensure your file has an extension.")
            return

        # Get supported conversions for this file type
        supported_formats = get_supported_conversions(file_extension)
        
        if not supported_formats:
            await update.message.reply_text(
                f"❌ Sorry, I don't support conversion for {file_extension} files yet.\n\n"
                "Supported formats: PDF, DOCX, TXT, JPG, PNG, WEBP, MP3, WAV, OGG, MP4"
            )
            return

        # Create inline keyboard with conversion options
        keyboard = []
        for target_format in supported_formats:
            callback_data = f"convert_{file_extension[1:]}_{target_format}_{document.file_id}"
            keyboard.append([InlineKeyboardButton(
                f"Convert to {target_format.upper()}", 
                callback_data=callback_data
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📁 **File received:** {file_name}\n"
            f"📊 **Size:** {document.file_size / 1024:.1f} KB\n"
            f"🔧 **Type:** {file_extension[1:].upper()}\n\n"
            "Choose conversion format:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await update.message.reply_text("❌ An error occurred while processing your file. Please try again.")

async def handle_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle conversion button clicks."""
    query = update.callback_query
    await query.answer()
    
    try:
        # Parse callback data
        data_parts = query.data.split('_')
        
        # Handle photo conversions with stored file_id
        if len(data_parts) == 3 and data_parts[0] == 'convert' and data_parts[1] == 'photo':
            source_format = 'jpg'
            target_format = data_parts[2]
            file_id = context.user_data.get('photo_file_id')
            if not file_id:
                await query.edit_message_text("❌ Photo file not found. Please send the photo again.")
                return
        # Handle document conversions
        elif len(data_parts) == 4 and data_parts[0] == 'convert':
            source_format = data_parts[1]
            target_format = data_parts[2]
            file_id = data_parts[3]
        else:
            await query.edit_message_text("❌ Invalid conversion request.")
            return
        
        # Update message to show processing
        await query.edit_message_text(
            f"🔄 Converting from {source_format.upper()} to {target_format.upper()}...\n"
            "Please wait, this may take a moment."
        )
        
        # Download file from Telegram
        file = await context.bot.get_file(file_id)
        input_path = f"temp/input_{file_id}.{source_format}"
        await file.download_to_drive(input_path)
        
        # Convert file
        output_path = await converter.convert_file(input_path, source_format, target_format)
        
        if not output_path or not os.path.exists(output_path):
            await query.edit_message_text("❌ Conversion failed. Please try again with a different file.")
            return
        
        # Send converted file
        output_filename = f"converted.{target_format}"
        with open(output_path, 'rb') as converted_file:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=converted_file,
                filename=output_filename,
                caption=f"✅ Successfully converted to {target_format.upper()}!"
            )
        
        await query.edit_message_text(
            f"✅ **Conversion completed!**\n"
            f"📁 {source_format.upper()} → {target_format.upper()}\n"
            f"📤 File sent above.",
            parse_mode='Markdown'
        )
        
        # Clean up temporary files
        cleanup_temp_files([input_path, output_path])
        
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        await query.edit_message_text(
            "❌ Conversion failed due to an error. Please ensure your file is valid and try again."
        )
        
        # Attempt cleanup even on error
        try:
            if 'input_path' in locals():
                cleanup_temp_files([input_path])
            if 'output_path' in locals():
                cleanup_temp_files([output_path])
        except:
            pass

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uploaded photos."""
    try:
        photo = update.message.photo[-1]  # Get highest resolution
        
        # Create inline keyboard for photo conversion
        # Store the file_id in context to avoid callback_data length limits
        context.user_data['photo_file_id'] = photo.file_id
        keyboard = [
            [InlineKeyboardButton("Convert to PNG", callback_data="convert_photo_png")],
            [InlineKeyboardButton("Convert to WEBP", callback_data="convert_photo_webp")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📷 **Photo received!**\n"
            f"📊 **Size:** {photo.file_size / 1024:.1f} KB\n\n"
            "Choose conversion format:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        await update.message.reply_text("❌ An error occurred while processing your photo. Please try again.")

def main() -> None:
    """Start the bot."""
    # Create temp directory if it doesn't exist
    os.makedirs("temp", exist_ok=True)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(handle_conversion))
    
    # Run the bot
    logger.info("Starting File Converter Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
