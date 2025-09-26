from googletrans import Translator, LANGUAGES
from typing import Optional, Dict

class TranslationService:
    """
    Service for translating text using Google Translate API
    """
    
    def __init__(self):
        self.translator = Translator()
        self.supported_languages = {code: name.title() for code, name in LANGUAGES.items()}
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text
        """
        if not text or not text.strip():
            return "en"
        try:
            detection = self.translator.detect(text)
            return detection.lang
        except Exception as e:
            print(f"Language detection failed: {e}")
            return "en"  # Default to English
    
    def translate_text(self, text: str, source_lang: str = 'auto', target_lang: str = 'en') -> Optional[str]:
        """
        Translate text from source language to target language
        """
        if not text or not text.strip():
            return text
        
        try:
            # Auto-detect source language if not specified
            if source_lang == 'auto':
                source_lang = self.detect_language(text)
            
            # Don't translate if source and target are the same
            if source_lang == target_lang:
                return text
            
            translation = self.translator.translate(text, src=source_lang, dest=target_lang)
            return translation.text
                
        except Exception as e:
            print(f"Translation error: {e}")
            return f"[{self.get_language_name(target_lang)} Translation] {text}"
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get dictionary of supported language codes and names
        """
        return self.supported_languages.copy()
    
    def translate_lesson_content(self, content: str, target_lang: str = 'ta') -> str:
        """
        Translate lesson content, handling paragraphs and preserving formatting
        """
        if not content:
            return content
        
        # Split content into paragraphs
        paragraphs = content.split('\n')
        translated_paragraphs = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Translate each paragraph
                translated_paragraph = self.translate_text(paragraph, 'auto', target_lang)
                translated_paragraphs.append(translated_paragraph)
            else:
                # Preserve empty lines
                translated_paragraphs.append(paragraph)
        
        return '\n'.join(translated_paragraphs)
    
    def get_language_name(self, lang_code: str) -> str:
        """
        Get the full language name from language code
        """
        return self.supported_languages.get(lang_code, lang_code.upper())

# Global translation service instance
translation_service = TranslationService()
