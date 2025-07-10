"""
Language support for the Telegram bot.
Supports Uzbek, English, and Russian.
"""

LANGUAGES = {
    'uz': {
        'welcome_title': '🤖 **Fayl Konverter Bot**',
        'welcome_text': 'Xush kelibsiz! Men fayllarni turli formatlar orasida konvertatsiya qilishda yordam beraman.\n\n**Variantni tanlang:**',
        'documents': '📄 Hujjatlar',
        'images': '🖼️ Rasmlar', 
        'audio': '🎵 Audio',
        'video': '🎬 Video',
        'send_direct': '📤 To\'g\'ridan-to\'g\'ri fayl yuborish',
        'back_menu': '🔙 Menyuga qaytish',
        'back': '🔙 Orqaga',
        'language': '🌐 Til',
        'document_conversion': '📄 **Hujjat Konvertatsiyasi**\n\nKonvertatsiya qilmoqchi bo\'lgan formatni tanlang:',
        'image_conversion': '🖼️ **Rasm Konvertatsiyasi**\n\nKonvertatsiya qilmoqchi bo\'lgan formatni tanlang:',
        'audio_conversion': '🎵 **Audio Konvertatsiyasi**\n\nKonvertatsiya qilmoqchi bo\'lgan formatni tanlang:',
        'video_conversion': '🎬 **Video Konvertatsiyasi**\n\nKonvertatsiya qilmoqchi bo\'lgan formatni tanlang:',
        'direct_upload': '📤 **To\'g\'ridan-to\'g\'ri Fayl Yuklash**\n\nQo\'llab-quvvatlanadigan faylni yuboring va konvertatsiya variantlarini ko\'rsataman:\n\n**Qo\'llab-quvvatlanadigan formatlar:**\n📄 PDF, DOCX, TXT\n🖼️ JPG, PNG, WEBP\n🎵 MP3, WAV, OGG\n🎬 MP4',
        'ready_convert': '📎 **Konvertatsiyaga tayyor**\n\n**Dan:** {source}\n**Ga:** {target}\n\nEndi {source} faylingizni yuboring va men uni {target}ga konvertatsiya qilaman.',
        'file_received': '📁 **Fayl qabul qilindi:** {name}\n📊 **Hajmi:** {size:.1f} KB\n🔧 **Turi:** {type}\n\nKonvertatsiya formatini tanlang:',
        'photo_received': '📷 **Rasm qabul qilindi!**\n📊 **Hajmi:** {size:.1f} KB\n\nKonvertatsiya formatini tanlang:',
        'audio_received': '🎵 **Audio fayl qabul qilindi!**\n📊 **Hajmi:** {size:.1f} KB\n\nKonvertatsiya formatini tanlang:',
        'video_received': '🎬 **Video fayl qabul qilindi!**\n📊 **Hajmi:** {size:.1f} KB\n\nKonvertatsiya formatini tanlang:',
        'converting': '🔄 {source}dan {target}ga konvertatsiya qilinmoqda...\nIltimos kuting, bu biroz vaqt olishi mumkin.',
        'conversion_completed': '✅ **Konvertatsiya yakunlandi!**\n📁 {source} → {target}\n📤 Fayl yuqorida yuborildi.',
        'conversion_failed': '❌ Konvertatsiya muvaffaqiyatsiz tugadi. Boshqa fayl bilan qayta urinib ko\'ring.',
        'invalid_request': '❌ Noto\'g\'ri konvertatsiya so\'rovi.',
        'photo_not_found': '❌ Rasm fayli topilmadi. Rasmni qayta yuboring.',
        'start_over': '❌ Iltimos qaytadan boshlang. Boshlash uchun /start buyrug\'ini yuboring.',
        'unsupported_format': '❌ Kechirasiz, men {ext} fayllar uchun konvertatsiyani qo\'llab-quvvatlamayman.\n\nQo\'llab-quvvatlanadigan formatlar: PDF, DOCX, TXT, JPG, PNG, WEBP, MP3, WAV, OGG, MP4',
        'file_type_error': '❌ Fayl turini aniqlab bo\'lmadi. Faylingizda kengaytma borligiga ishonch hosil qiling.',
        'error_occurred': '❌ Xatolik yuz berdi. Iltimos qayta urinib ko\'ring.',
        'help_title': '**Qanday foydalanish:**',
        'help_method1': '**1-usul: Menyu tizimi (Tavsiya etiladi)**\n1. Asosiy menyuni ochish uchun /start buyrug\'ini ishlating\n2. Fayl turingizni tanlang (Hujjatlar, Rasmlar, Audio, Video)\n3. Konvertatsiya qilmoqchi bo\'lgan manba formatni tanlang\n4. Nishon formatni tanlang\n5. Faylingizni yuboring va natijani oling!',
        'help_method2': '**2-usul: To\'g\'ridan-to\'g\'ri yuklash**\n1. Qo\'llab-quvvatlanadigan faylni to\'g\'ridan-to\'g\'ri yuboring\n2. Tugmalardan konvertatsiya formatini tanlang\n3. Konvertatsiya qilingan faylni yuklab oling!',
        'help_formats': '**Qo\'llab-quvvatlanadigan formatlar:**\n📄 Hujjatlar: PDF, DOCX, TXT\n🖼️ Rasmlar: JPG, PNG, WEBP\n🎵 Audio: MP3, WAV, OGG\n🎬 Video: MP4 → MP3',
        'help_tips': '**Maslahatlar:**\n• Menyu tizimi qadam-ba-qadam yo\'l-yo\'riq beradi\n• Fayllar konvertatsiyadan keyin avtomatik o\'chiriladi\n• Konvertatsiya katta fayllar uchun biroz vaqt olishi mumkin\n• Tilni o\'zgartirish uchun /language buyrug\'ini ishlating',
        'select_language': '🌐 **Tilni tanlang / Select Language / Выберите язык:**'
    },
    
    'en': {
        'welcome_title': '🤖 **File Converter Bot**',
        'welcome_text': 'Welcome! I can help you convert files between different formats.\n\n**Choose an option:**',
        'documents': '📄 Documents',
        'images': '🖼️ Images',
        'audio': '🎵 Audio', 
        'video': '🎬 Video',
        'send_direct': '📤 Send File Directly',
        'back_menu': '🔙 Back to Menu',
        'back': '🔙 Back',
        'language': '🌐 Language',
        'document_conversion': '📄 **Document Conversion**\n\nChoose the format you want to convert:',
        'image_conversion': '🖼️ **Image Conversion**\n\nChoose the format you want to convert:',
        'audio_conversion': '🎵 **Audio Conversion**\n\nChoose the format you want to convert:',
        'video_conversion': '🎬 **Video Conversion**\n\nChoose the format you want to convert:',
        'direct_upload': '📤 **Direct File Upload**\n\nSimply send me any supported file and I\'ll show you conversion options:\n\n**Supported formats:**\n📄 PDF, DOCX, TXT\n🖼️ JPG, PNG, WEBP\n🎵 MP3, WAV, OGG\n🎬 MP4',
        'ready_convert': '📎 **Ready to Convert**\n\n**From:** {source}\n**To:** {target}\n\nPlease send your {source} file now and I\'ll convert it to {target}.',
        'file_received': '📁 **File received:** {name}\n📊 **Size:** {size:.1f} KB\n🔧 **Type:** {type}\n\nChoose conversion format:',
        'photo_received': '📷 **Photo received!**\n📊 **Size:** {size:.1f} KB\n\nChoose conversion format:',
        'audio_received': '🎵 **Audio file received!**\n📊 **Size:** {size:.1f} KB\n\nChoose conversion format:',
        'video_received': '🎬 **Video file received!**\n📊 **Size:** {size:.1f} KB\n\nChoose conversion format:',
        'converting': '🔄 Converting from {source} to {target}...\nPlease wait, this may take a moment.',
        'conversion_completed': '✅ **Conversion completed!**\n📁 {source} → {target}\n📤 File sent above.',
        'conversion_failed': '❌ Conversion failed. Please try again with a different file.',
        'invalid_request': '❌ Invalid conversion request.',
        'photo_not_found': '❌ Photo file not found. Please send the photo again.',
        'start_over': '❌ Please start over. Send /start to begin.',
        'unsupported_format': '❌ Sorry, I don\'t support conversion for {ext} files yet.\n\nSupported formats: PDF, DOCX, TXT, JPG, PNG, WEBP, MP3, WAV, OGG, MP4',
        'file_type_error': '❌ Cannot determine file type. Please ensure your file has an extension.',
        'error_occurred': '❌ An error occurred. Please try again.',
        'help_title': '**How to use:**',
        'help_method1': '**Method 1: Menu System (Recommended)**\n1. Use /start to open the main menu\n2. Choose your file type (Documents, Images, Audio, Video)\n3. Select the source format you want to convert from\n4. Choose the target format you want to convert to\n5. Send your file and get the converted result!',
        'help_method2': '**Method 2: Direct Upload**\n1. Send any supported file directly\n2. Choose conversion format from the buttons\n3. Download your converted file!',
        'help_formats': '**Supported formats:**\n📄 Documents: PDF, DOCX, TXT\n🖼️ Images: JPG, PNG, WEBP\n🎵 Audio: MP3, WAV, OGG\n🎬 Video: MP4 → MP3',
        'help_tips': '**Tips:**\n• Menu system provides step-by-step guidance\n• Files are automatically deleted after conversion\n• Conversion may take a few moments for large files\n• Use /language command to change language',
        'select_language': '🌐 **Select Language / Tilni tanlang / Выберите язык:**'
    },
    
    'ru': {
        'welcome_title': '🤖 **Бот Конвертера Файлов**',
        'welcome_text': 'Добро пожаловать! Я могу помочь конвертировать файлы между различными форматами.\n\n**Выберите опцию:**',
        'documents': '📄 Документы',
        'images': '🖼️ Изображения',
        'audio': '🎵 Аудио',
        'video': '🎬 Видео',
        'send_direct': '📤 Отправить файл напрямую',
        'back_menu': '🔙 Вернуться в меню',
        'back': '🔙 Назад',
        'language': '🌐 Язык',
        'document_conversion': '📄 **Конвертация Документов**\n\nВыберите формат для конвертации:',
        'image_conversion': '🖼️ **Конвертация Изображений**\n\nВыберите формат для конвертации:',
        'audio_conversion': '🎵 **Конвертация Аудио**\n\nВыберите формат для конвертации:',
        'video_conversion': '🎬 **Конвертация Видео**\n\nВыберите формат для конвертации:',
        'direct_upload': '📤 **Прямая Загрузка Файла**\n\nПросто отправьте любой поддерживаемый файл, и я покажу варианты конвертации:\n\n**Поддерживаемые форматы:**\n📄 PDF, DOCX, TXT\n🖼️ JPG, PNG, WEBP\n🎵 MP3, WAV, OGG\n🎬 MP4',
        'ready_convert': '📎 **Готов к Конвертации**\n\n**Из:** {source}\n**В:** {target}\n\nПожалуйста, отправьте ваш файл {source} сейчас, и я конвертирую его в {target}.',
        'file_received': '📁 **Файл получен:** {name}\n📊 **Размер:** {size:.1f} КБ\n🔧 **Тип:** {type}\n\nВыберите формат конвертации:',
        'photo_received': '📷 **Фото получено!**\n📊 **Размер:** {size:.1f} КБ\n\nВыберите формат конвертации:',
        'audio_received': '🎵 **Аудио файл получен!**\n📊 **Размер:** {size:.1f} КБ\n\nВыберите формат конвертации:',
        'video_received': '🎬 **Видео файл получен!**\n📊 **Размер:** {size:.1f} КБ\n\nВыберите формат конвертации:',
        'converting': '🔄 Конвертация из {source} в {target}...\nПожалуйста подождите, это может занять некоторое время.',
        'conversion_completed': '✅ **Конвертация завершена!**\n📁 {source} → {target}\n📤 Файл отправлен выше.',
        'conversion_failed': '❌ Конвертация не удалась. Попробуйте с другим файлом.',
        'invalid_request': '❌ Неверный запрос конвертации.',
        'photo_not_found': '❌ Файл фото не найден. Пожалуйста, отправьте фото снова.',
        'start_over': '❌ Пожалуйста, начните сначала. Отправьте /start для начала.',
        'unsupported_format': '❌ Извините, я не поддерживаю конвертацию файлов {ext}.\n\nПоддерживаемые форматы: PDF, DOCX, TXT, JPG, PNG, WEBP, MP3, WAV, OGG, MP4',
        'file_type_error': '❌ Не удается определить тип файла. Убедитесь, что у файла есть расширение.',
        'error_occurred': '❌ Произошла ошибка. Пожалуйста, попробуйте снова.',
        'help_title': '**Как использовать:**',
        'help_method1': '**Метод 1: Система Меню (Рекомендуется)**\n1. Используйте /start для открытия главного меню\n2. Выберите тип файла (Документы, Изображения, Аудио, Видео)\n3. Выберите исходный формат для конвертации\n4. Выберите целевой формат\n5. Отправьте файл и получите результат!',
        'help_method2': '**Метод 2: Прямая Загрузка**\n1. Отправьте любой поддерживаемый файл напрямую\n2. Выберите формат конвертации из кнопок\n3. Скачайте конвертированный файл!',
        'help_formats': '**Поддерживаемые форматы:**\n📄 Документы: PDF, DOCX, TXT\n🖼️ Изображения: JPG, PNG, WEBP\n🎵 Аудио: MP3, WAV, OGG\n🎬 Видео: MP4 → MP3',
        'help_tips': '**Советы:**\n• Система меню предоставляет пошаговое руководство\n• Файлы автоматически удаляются после конвертации\n• Конвертация может занять некоторое время для больших файлов\n• Используйте команду /language для смены языка',
        'select_language': '🌐 **Выберите язык / Select Language / Tilni tanlang:**'
    }
}

def get_text(user_lang: str, key: str, **kwargs) -> str:
    """Get localized text for the given key and language."""
    lang = user_lang if user_lang in LANGUAGES else 'en'
    text = LANGUAGES[lang].get(key, LANGUAGES['en'].get(key, key))
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text
    return text

def get_user_language(context) -> str:
    """Get user's preferred language from context."""
    return context.user_data.get('language', None)

def set_user_language(context, language: str) -> None:
    """Set user's preferred language in context."""
    if language in LANGUAGES:
        context.user_data['language'] = language