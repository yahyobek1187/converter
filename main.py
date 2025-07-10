import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from utils.converters import FileConverter, get_supported_conversions, cleanup_temp_files
from utils.languages import get_text, get_user_language, set_user_language

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
    user_lang = get_user_language(context)
    
    # Check if language was ever set (using a permanent flag)
    language_ever_set = context.user_data.get('language_ever_set', False)
    
    # If no language was ever set, show language selection
    if not language_ever_set:
        await show_language_selection(update, context)
        return
    
    # Use default language if somehow lost
    if not user_lang or user_lang not in ['uz', 'en', 'ru']:
        user_lang = 'en'  # Default fallback
    
    welcome_message = f"{get_text(user_lang, 'welcome_title')}\n\n{get_text(user_lang, 'welcome_text')}"
    
    # Create main menu keyboard without language button
    keyboard = [
        [InlineKeyboardButton(get_text(user_lang, 'documents'), callback_data="menu_documents")],
        [InlineKeyboardButton(get_text(user_lang, 'images'), callback_data="menu_images")],
        [InlineKeyboardButton(get_text(user_lang, 'audio'), callback_data="menu_audio")],
        [InlineKeyboardButton(get_text(user_lang, 'video'), callback_data="menu_video")],
        [InlineKeyboardButton(get_text(user_lang, 'send_direct'), callback_data="menu_direct")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

async def show_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show language selection menu."""
    message = get_text('en', 'select_language')
    
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        query = update.callback_query
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    user_lang = get_user_language(context)
    
    help_text = f"""{get_text(user_lang, 'help_title')}

{get_text(user_lang, 'help_method1')}

{get_text(user_lang, 'help_method2')}

{get_text(user_lang, 'help_formats')}

{get_text(user_lang, 'help_tips')}
    """
    
    # Add back to menu button
    keyboard = [[InlineKeyboardButton(get_text(user_lang, 'back_menu'), callback_data="back_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send language selection when the command /language is issued."""
    await show_language_selection(update, context)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uploaded documents."""
    try:
        user_lang = get_user_language(context)
        document = update.message.document
        if not document:
            await update.message.reply_text(get_text(user_lang, 'error_occurred'))
            return

        # Get file extension
        file_name = document.file_name or "unknown"
        file_extension = os.path.splitext(file_name)[1].lower()
        
        if not file_extension:
            await update.message.reply_text(get_text(user_lang, 'file_type_error'))
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
                get_text(user_lang, 'unsupported_format', ext=file_extension[1:].upper())
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
        
        keyboard.append([InlineKeyboardButton(get_text(user_lang, 'back_menu'), callback_data="back_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            get_text(user_lang, 'file_received', 
                    name=file_name, 
                    size=document.file_size / 1024, 
                    type=file_extension[1:].upper()),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error handling document: {e}")
        user_lang = get_user_language(context)
        await update.message.reply_text(get_text(user_lang, 'error_occurred'))

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle menu selections."""
    query = update.callback_query
    await query.answer()
    
    try:
        user_lang = get_user_language(context)
        
        # Handle language selection
        if query.data.startswith('lang_'):
            lang_code = query.data.replace('lang_', '')
            set_user_language(context, lang_code)
            # Redirect to main menu
            await start_menu(update, context)
            return

        
        if query.data == "menu_documents":
            message = get_text(user_lang, 'document_conversion')
            keyboard = [
                [InlineKeyboardButton("PDF → DOCX/TXT", callback_data="type_pdf")],
                [InlineKeyboardButton("DOCX → PDF/TXT", callback_data="type_docx")],
                [InlineKeyboardButton("TXT → DOCX", callback_data="type_txt")],
                [InlineKeyboardButton(get_text(user_lang, 'back_menu'), callback_data="back_menu")]
            ]
            
        elif query.data == "menu_images":
            message = get_text(user_lang, 'image_conversion')
            keyboard = [
                [InlineKeyboardButton("JPG → PNG/WEBP", callback_data="type_jpg")],
                [InlineKeyboardButton("PNG → JPG/WEBP", callback_data="type_png")],
                [InlineKeyboardButton("WEBP → JPG/PNG", callback_data="type_webp")],
                [InlineKeyboardButton(get_text(user_lang, 'back_menu'), callback_data="back_menu")]
            ]
            
        elif query.data == "menu_audio":
            message = get_text(user_lang, 'audio_conversion')
            keyboard = [
                [InlineKeyboardButton("MP3 → WAV/OGG", callback_data="type_mp3")],
                [InlineKeyboardButton("WAV → MP3/OGG", callback_data="type_wav")],
                [InlineKeyboardButton("OGG → MP3/WAV", callback_data="type_ogg")],
                [InlineKeyboardButton(get_text(user_lang, 'back_menu'), callback_data="back_menu")]
            ]
            
        elif query.data == "menu_video":
            message = get_text(user_lang, 'video_conversion')
            keyboard = [
                [InlineKeyboardButton("MP4 → MP3", callback_data="type_mp4")],
                [InlineKeyboardButton(get_text(user_lang, 'back_menu'), callback_data="back_menu")]
            ]
            
        elif query.data == "menu_direct":
            message = get_text(user_lang, 'direct_upload')
            keyboard = [
                [InlineKeyboardButton(get_text(user_lang, 'back_menu'), callback_data="back_menu")]
            ]
            
        elif query.data == "back_menu":
            await start_menu(update, context)
            return
            
        else:
            # Handle file type selection
            await handle_file_type_selection(update, context)
            return
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error handling menu: {e}")
        user_lang = get_user_language(context)
        await query.edit_message_text(get_text(user_lang, 'error_occurred'))

async def start_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show the main menu."""
    user_lang = get_user_language(context)
    message = f"{get_text(user_lang, 'welcome_title')}\n\n{get_text(user_lang, 'welcome_text')}"
    
    keyboard = [
        [InlineKeyboardButton(get_text(user_lang, 'documents'), callback_data="menu_documents")],
        [InlineKeyboardButton(get_text(user_lang, 'images'), callback_data="menu_images")],
        [InlineKeyboardButton(get_text(user_lang, 'audio'), callback_data="menu_audio")],
        [InlineKeyboardButton(get_text(user_lang, 'video'), callback_data="menu_video")],
        [InlineKeyboardButton(get_text(user_lang, 'send_direct'), callback_data="menu_direct")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

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
                user_lang = get_user_language(context)
                await query.edit_message_text(get_text(user_lang, 'photo_not_found'))
                return
        # Handle audio conversions
        elif len(data_parts) == 3 and data_parts[0] == 'convert' and data_parts[1] == 'audio':
            source_format = context.user_data.get('audio_source_format', 'mp3')
            target_format = data_parts[2]
            file_id = context.user_data.get('audio_file_id')
            if not file_id:
                user_lang = get_user_language(context)
                await query.edit_message_text(get_text(user_lang, 'start_over'))
                return
        # Handle video conversions
        elif len(data_parts) == 3 and data_parts[0] == 'convert' and data_parts[1] == 'video':
            source_format = 'mp4'
            target_format = data_parts[2]
            file_id = context.user_data.get('video_file_id')
            if not file_id:
                user_lang = get_user_language(context)
                await query.edit_message_text(get_text(user_lang, 'start_over'))
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
        user_lang = get_user_language(context)
        await query.edit_message_text(
            get_text(user_lang, 'converting', source=source_format.upper(), target=target_format.upper())
        )
        
        # Download file from Telegram
        file = await context.bot.get_file(file_id)
        input_path = f"temp/input_{file_id}.{source_format}"
        await file.download_to_drive(input_path)
        
        # Convert file
        output_path = await converter.convert_file(input_path, source_format, target_format)
        
        if not output_path or not os.path.exists(output_path):
            user_lang = get_user_language(context)
            await query.edit_message_text(get_text(user_lang, 'conversion_failed'))
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
        
        user_lang = get_user_language(context)
        await query.edit_message_text(
            get_text(user_lang, 'conversion_completed', source=source_format.upper(), target=target_format.upper()),
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
        user_lang = get_user_language(context)
        processing_message = await update.message.reply_text(
            get_text(user_lang, 'converting', source=source_format.upper(), target=target_format.upper())
        )
        
        # Download file from Telegram
        file = await context.bot.get_file(file_id)
        input_path = f"temp/input_{file_id}.{source_format}"
        await file.download_to_drive(input_path)
        
        # Convert file
        output_path = await converter.convert_file(input_path, source_format, target_format)
        
        if not output_path or not os.path.exists(output_path):
            await processing_message.edit_text(get_text(user_lang, 'conversion_failed'))
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
            get_text(user_lang, 'conversion_completed', source=source_format.upper(), target=target_format.upper()),
            parse_mode='Markdown'
        )
        
        # Clean up temporary files and clear user data
        cleanup_temp_files([input_path, output_path])
        context.user_data.clear()
        
    except Exception as e:
        logger.error(f"Error during conversion: {e}")
        user_lang = get_user_language(context)
        await update.message.reply_text(get_text(user_lang, 'conversion_failed'))
        
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
        user_lang = get_user_language(context)
        context.user_data['photo_file_id'] = photo.file_id
        keyboard = [
            [InlineKeyboardButton("Convert to PNG", callback_data="convert_photo_png")],
            [InlineKeyboardButton("Convert to WEBP", callback_data="convert_photo_webp")],
            [InlineKeyboardButton(get_text(user_lang, 'back_menu'), callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            get_text(user_lang, 'photo_received', size=photo.file_size / 1024),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        user_lang = get_user_language(context)
        await update.message.reply_text(get_text(user_lang, 'error_occurred'))

async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uploaded audio files."""
    try:
        user_lang = get_user_language(context)
        audio = update.message.audio or update.message.voice
        
        if not audio:
            await update.message.reply_text(get_text(user_lang, 'error_occurred'))
            return
        
        # Check if user has selected target format from menu
        selected_file_type = context.user_data.get('selected_file_type')
        target_format = context.user_data.get('target_format')
        
        if selected_file_type and target_format and selected_file_type in ['mp3', 'wav', 'ogg']:
            # User sent the expected audio type, proceed with conversion
            await convert_file_now(update, context, selected_file_type, target_format, audio.file_id)
            return
        
        # Determine audio format from mime_type or file_name
        source_format = 'mp3'  # Default
        if audio.mime_type:
            if 'wav' in audio.mime_type:
                source_format = 'wav'
            elif 'ogg' in audio.mime_type:
                source_format = 'ogg'
        
        # Create inline keyboard for audio conversion
        supported_formats = get_supported_conversions(f".{source_format}")
        if not supported_formats:
            await update.message.reply_text(get_text(user_lang, 'unsupported_format', ext=source_format))
            return
        
        context.user_data['audio_file_id'] = audio.file_id
        context.user_data['audio_source_format'] = source_format
        
        keyboard = []
        for target_format in supported_formats:
            keyboard.append([InlineKeyboardButton(
                f"Convert to {target_format.upper()}", 
                callback_data=f"convert_audio_{target_format}"
            )])
        
        keyboard.append([InlineKeyboardButton(get_text(user_lang, 'back_menu'), callback_data="back_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            get_text(user_lang, 'audio_received', size=audio.file_size / 1024),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error handling audio: {e}")
        user_lang = get_user_language(context)
        await update.message.reply_text(get_text(user_lang, 'error_occurred'))

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle uploaded video files."""
    try:
        user_lang = get_user_language(context)
        video = update.message.video
        
        if not video:
            await update.message.reply_text(get_text(user_lang, 'error_occurred'))
            return
        
        # Check if user has selected target format from menu
        selected_file_type = context.user_data.get('selected_file_type')
        target_format = context.user_data.get('target_format')
        
        if selected_file_type and target_format and selected_file_type == 'mp4':
            # User sent the expected video type, proceed with conversion
            await convert_file_now(update, context, 'mp4', target_format, video.file_id)
            return
        
        # Create inline keyboard for video conversion (only MP4 to MP3 supported)
        context.user_data['video_file_id'] = video.file_id
        
        keyboard = [
            [InlineKeyboardButton("Convert to MP3", callback_data="convert_video_mp3")],
            [InlineKeyboardButton(get_text(user_lang, 'back_menu'), callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            get_text(user_lang, 'video_received', size=video.file_size / 1024),
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error handling video: {e}")
        user_lang = get_user_language(context)
        await update.message.reply_text(get_text(user_lang, 'error_occurred'))

def main() -> None:
    """Start the bot."""
    # Create temp directory if it doesn't exist
    os.makedirs("temp", exist_ok=True)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(MessageHandler(filters.VOICE, handle_audio))
    application.add_handler(CallbackQueryHandler(handle_conversion))
    
    # Run the bot
    logger.info("Starting File Converter Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
