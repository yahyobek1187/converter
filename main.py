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

**Choose an option:**
"""
    
    # Create main menu keyboard
    keyboard = [
        [InlineKeyboardButton("📄 Documents", callback_data="menu_documents")],
        [InlineKeyboardButton("🖼️ Images", callback_data="menu_images")],
        [InlineKeyboardButton("🎵 Audio", callback_data="menu_audio")],
        [InlineKeyboardButton("🎬 Video", callback_data="menu_video")],
        [InlineKeyboardButton("📤 Send File Directly", callback_data="menu_direct")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
**How to use:**

**Method 1: Menu System (Recommended)**
1. Use /start to open the main menu
2. Choose your file type (Documents, Images, Audio, Video)
3. Select the source format you want to convert from
4. Choose the target format you want to convert to
5. Send your file and get the converted result!

**Method 2: Direct Upload**
1. Send any supported file directly
2. Choose conversion format from the buttons
3. Download your converted file!

**Supported formats:**
📄 Documents: PDF, DOCX, TXT
🖼️ Images: JPG, PNG, WEBP
🎵 Audio: MP3, WAV, OGG
🎬 Video: MP4 → MP3

**Tips:**
• Menu system provides step-by-step guidance
• Files are automatically deleted after conversion
• Conversion may take a few moments for large files
    """
    
    # Add back to menu button
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

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

        # Check if user has selected target format from menu
        selected_file_type = context.user_data.get('selected_file_type')
        target_format = context.user_data.get('target_format')
        
        if selected_file_type and target_format and file_extension[1:] == selected_file_type:
            # User sent the expected file type, proceed with conversion
            context.user_data['document_file_id'] = document.file_id
            context.user_data['document_file_name'] = file_name
            
            # Start conversion automatically
            await convert_file_now(update, context, file_extension[1:], target_format, document.file_id)
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
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")])
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

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle menu selections."""
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data == "menu_documents":
            message = """
📄 **Document Conversion**

Choose the format you want to convert:
"""
            keyboard = [
                [InlineKeyboardButton("PDF → DOCX/TXT", callback_data="type_pdf")],
                [InlineKeyboardButton("DOCX → PDF/TXT", callback_data="type_docx")],
                [InlineKeyboardButton("TXT → DOCX", callback_data="type_txt")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]
            ]
            
        elif query.data == "menu_images":
            message = """
🖼️ **Image Conversion**

Choose the format you want to convert:
"""
            keyboard = [
                [InlineKeyboardButton("JPG → PNG/WEBP", callback_data="type_jpg")],
                [InlineKeyboardButton("PNG → JPG/WEBP", callback_data="type_png")],
                [InlineKeyboardButton("WEBP → JPG/PNG", callback_data="type_webp")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]
            ]
            
        elif query.data == "menu_audio":
            message = """
🎵 **Audio Conversion**

Choose the format you want to convert:
"""
            keyboard = [
                [InlineKeyboardButton("MP3 → WAV/OGG", callback_data="type_mp3")],
                [InlineKeyboardButton("WAV → MP3/OGG", callback_data="type_wav")],
                [InlineKeyboardButton("OGG → MP3/WAV", callback_data="type_ogg")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]
            ]
            
        elif query.data == "menu_video":
            message = """
🎬 **Video Conversion**

Choose the format you want to convert:
"""
            keyboard = [
                [InlineKeyboardButton("MP4 → MP3", callback_data="type_mp4")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]
            ]
            
        elif query.data == "menu_direct":
            message = """
📤 **Direct File Upload**

Simply send me any supported file and I'll show you conversion options:

**Supported formats:**
📄 PDF, DOCX, TXT
🖼️ JPG, PNG, WEBP
🎵 MP3, WAV, OGG
🎬 MP4
"""
            keyboard = [
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]
            ]
            
        elif query.data == "back_menu":
            message = """
🤖 **File Converter Bot**

Welcome! I can help you convert files between different formats.

**Choose an option:**
"""
            keyboard = [
                [InlineKeyboardButton("📄 Documents", callback_data="menu_documents")],
                [InlineKeyboardButton("🖼️ Images", callback_data="menu_images")],
                [InlineKeyboardButton("🎵 Audio", callback_data="menu_audio")],
                [InlineKeyboardButton("🎬 Video", callback_data="menu_video")],
                [InlineKeyboardButton("📤 Send File Directly", callback_data="menu_direct")]
            ]
            
        else:
            # Handle file type selection
            await handle_file_type_selection(update, context)
            return
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error handling menu: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")

async def handle_file_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle file type selection and show target format options."""
    query = update.callback_query
    
    try:
        file_type = query.data.replace("type_", "")
        context.user_data['selected_file_type'] = file_type
        
        # Get supported conversions
        supported_formats = get_supported_conversions(f".{file_type}")
        
        if not supported_formats:
            await query.edit_message_text("❌ No conversions available for this format.")
            return
            
        message = f"""
📎 **{file_type.upper()} Conversion**

Choose target format:
"""
        
        keyboard = []
        for target_format in supported_formats:
            keyboard.append([InlineKeyboardButton(
                f"Convert to {target_format.upper()}", 
                callback_data=f"target_{target_format}"
            )])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error handling file type selection: {e}")
        await query.edit_message_text("❌ An error occurred. Please try again.")

async def handle_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle conversion button clicks."""
    query = update.callback_query
    await query.answer()
    
    try:
        # Handle target format selection from menu
        if query.data.startswith('target_'):
            target_format = query.data.replace('target_', '')
            source_format = context.user_data.get('selected_file_type')
            
            if not source_format:
                await query.edit_message_text("❌ Please start over. Send /start to begin.")
                return
                
            # Ask user to send the file
            message = f"""
📎 **Ready to Convert**

**From:** {source_format.upper()}
**To:** {target_format.upper()}

Please send your {source_format.upper()} file now and I'll convert it to {target_format.upper()}.
"""
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            context.user_data['target_format'] = target_format
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            return
            
        # Parse callback data for direct file conversion
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
            # Not a conversion request, might be menu handling
            await handle_menu(update, context)
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
        
        # Clean up temporary files and clear user data
        cleanup_temp_files([input_path, output_path])
        context.user_data.clear()
        
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

async def convert_file_now(update: Update, context: ContextTypes.DEFAULT_TYPE, source_format: str, target_format: str, file_id: str) -> None:
    """Convert file immediately after menu selection."""
    try:
        # Send processing message
        processing_message = await update.message.reply_text(
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
            await processing_message.edit_text("❌ Conversion failed. Please try again with a different file.")
            return
        
        # Send converted file
        output_filename = f"converted.{target_format}"
        with open(output_path, 'rb') as converted_file:
            await context.bot.send_document(
                chat_id=update.message.chat_id,
                document=converted_file,
                filename=output_filename,
                caption=f"✅ Successfully converted to {target_format.upper()}!"
            )
        
        await processing_message.edit_text(
            f"✅ **Conversion completed!**\n"
            f"📁 {source_format.upper()} → {target_format.upper()}\n"
            f"📤 File sent above.",
            parse_mode='Markdown'
        )
        
        # Clean up temporary files and clear user data
        cleanup_temp_files([input_path, output_path])
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        await update.message.reply_text(
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
        
        # Check if user has selected target format from menu
        selected_file_type = context.user_data.get('selected_file_type')
        target_format = context.user_data.get('target_format')
        
        if selected_file_type and target_format and selected_file_type in ['jpg', 'jpeg', 'png', 'webp']:
            # User sent the expected image type, proceed with conversion
            await convert_file_now(update, context, 'jpg', target_format, photo.file_id)
            return
        
        # Create inline keyboard for photo conversion
        # Store the file_id in context to avoid callback_data length limits
        context.user_data['photo_file_id'] = photo.file_id
        keyboard = [
            [InlineKeyboardButton("Convert to PNG", callback_data="convert_photo_png")],
            [InlineKeyboardButton("Convert to WEBP", callback_data="convert_photo_webp")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_menu")]
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
