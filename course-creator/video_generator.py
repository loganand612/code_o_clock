import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap
from moviepy.editor import *
import tempfile
import uuid
from datetime import datetime

class VideoGenerator:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def create_summary_video(self, title, summary, style="modern", duration=60):
        """
        Create a 1-minute summary video with multiple styles
        """
        try:
            # Generate unique filename
            video_id = str(uuid.uuid4())[:8]
            video_path = os.path.join(self.temp_dir, f"summary_{video_id}.mp4")
            
            # Create video based on style
            if style == "modern":
                video_path = self._create_modern_video(title, summary, duration)
            elif style == "minimal":
                video_path = self._create_minimal_video(title, summary, duration)
            elif style == "educational":
                video_path = self._create_educational_video(title, summary, duration)
            else:
                video_path = self._create_modern_video(title, summary, duration)
                
            return video_path
            
        except Exception as e:
            print(f"Error creating video: {str(e)}")
            return None
    
    def _create_modern_video(self, title, summary, duration):
        """Create a modern-style video with gradients and animations"""
        try:
            # Split content into segments for better pacing
            segments = self._split_content_for_video(title, summary, duration)
            
            clips = []
            current_time = 0
            
            for i, segment in enumerate(segments):
                # Create background with gradient
                bg_clip = self._create_gradient_background(segment['duration'])
                
                # Add text overlay
                text_clip = self._create_text_overlay(
                    segment['text'], 
                    segment['duration'],
                    font_size=segment.get('font_size', 48),
                    color=segment.get('color', 'white')
                )
                
                # Combine background and text
                video_clip = CompositeVideoClip([bg_clip, text_clip])
                clips.append(video_clip)
                current_time += segment['duration']
            
            # Concatenate all clips
            final_video = concatenate_videoclips(clips)
            
            # Generate TTS audio
            audio_path = self._generate_tts_audio(summary, duration)
            if audio_path:
                audio_clip = AudioFileClip(audio_path)
                final_video = final_video.set_audio(audio_clip)
            
            # Export video
            video_path = os.path.join(self.temp_dir, f"modern_{uuid.uuid4()[:8]}.mp4")
            final_video.write_videofile(
                video_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up
            final_video.close()
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
                
            return video_path
            
        except Exception as e:
            print(f"Error creating modern video: {str(e)}")
            return None
    
    def _create_minimal_video(self, title, summary, duration):
        """Create a minimal, clean video"""
        try:
            # Create simple white background
            bg_clip = ColorClip(size=(1280, 720), color=(255, 255, 255), duration=duration)
            
            # Create title slide
            title_duration = min(10, duration * 0.2)
            title_clip = self._create_text_overlay(
                title, 
                title_duration,
                font_size=64,
                color='#2c3e50',
                position='center'
            )
            
            # Create summary slides
            summary_duration = duration - title_duration
            summary_clip = self._create_text_overlay(
                summary, 
                summary_duration,
                font_size=36,
                color='#34495e',
                position='center'
            )
            
            # Combine clips
            final_video = CompositeVideoClip([
                bg_clip,
                title_clip.set_start(0),
                summary_clip.set_start(title_duration)
            ])
            
            # Add audio
            audio_path = self._generate_tts_audio(summary, duration)
            if audio_path:
                audio_clip = AudioFileClip(audio_path)
                final_video = final_video.set_audio(audio_clip)
            
            # Export
            video_path = os.path.join(self.temp_dir, f"minimal_{uuid.uuid4()[:8]}.mp4")
            final_video.write_videofile(
                video_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            final_video.close()
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
                
            return video_path
            
        except Exception as e:
            print(f"Error creating minimal video: {str(e)}")
            return None
    
    def _create_educational_video(self, title, summary, duration):
        """Create an educational-style video with bullet points and animations"""
        try:
            # Create professional background
            bg_clip = self._create_professional_background(duration)
            
            # Split summary into key points
            key_points = self._extract_key_points(summary)
            
            clips = []
            time_per_point = duration / (len(key_points) + 1)  # +1 for title
            
            # Title slide
            title_clip = self._create_text_overlay(
                title, 
                time_per_point,
                font_size=56,
                color='#1a365d',
                position='center'
            )
            clips.append(title_clip)
            
            # Key points slides
            for point in key_points:
                point_clip = self._create_bullet_point_overlay(
                    point, 
                    time_per_point,
                    font_size=42,
                    color='#2d3748'
                )
                clips.append(point_clip)
            
            # Combine all clips
            final_video = CompositeVideoClip([
                bg_clip,
                *[clip.set_start(i * time_per_point) for i, clip in enumerate(clips)]
            ])
            
            # Add audio
            audio_path = self._generate_tts_audio(summary, duration)
            if audio_path:
                audio_clip = AudioFileClip(audio_path)
                final_video = final_video.set_audio(audio_clip)
            
            # Export
            video_path = os.path.join(self.temp_dir, f"educational_{uuid.uuid4()[:8]}.mp4")
            final_video.write_videofile(
                video_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            final_video.close()
            if audio_path and os.path.exists(audio_path):
                os.remove(audio_path)
                
            return video_path
            
        except Exception as e:
            print(f"Error creating educational video: {str(e)}")
            return None
    
    def _create_gradient_background(self, duration):
        """Create a gradient background"""
        try:
            # Create a gradient using PIL
            img = Image.new('RGB', (1280, 720), color='#667eea')
            draw = ImageDraw.Draw(img)
            
            # Create gradient effect
            for i in range(720):
                color_value = int(255 * (i / 720))
                draw.line([(0, i), (1280, i)], fill=(102 + color_value//3, 126 + color_value//3, 234 + color_value//3))
            
            # Convert to video clip
            img_path = os.path.join(self.temp_dir, f"bg_{uuid.uuid4()[:8]}.png")
            img.save(img_path)
            
            bg_clip = ImageClip(img_path, duration=duration)
            return bg_clip
            
        except Exception as e:
            print(f"Error creating gradient background: {str(e)}")
            # Fallback to solid color
            return ColorClip(size=(1280, 720), color=(102, 126, 234), duration=duration)
    
    def _create_professional_background(self, duration):
        """Create a professional background"""
        try:
            # Create a subtle gradient background
            img = Image.new('RGB', (1280, 720), color='#f7fafc')
            draw = ImageDraw.Draw(img)
            
            # Add subtle pattern
            for i in range(0, 1280, 40):
                for j in range(0, 720, 40):
                    if (i + j) % 80 == 0:
                        draw.rectangle([i, j, i+20, j+20], fill='#e2e8f0')
            
            img_path = os.path.join(self.temp_dir, f"pro_bg_{uuid.uuid4()[:8]}.png")
            img.save(img_path)
            
            bg_clip = ImageClip(img_path, duration=duration)
            return bg_clip
            
        except Exception as e:
            print(f"Error creating professional background: {str(e)}")
            return ColorClip(size=(1280, 720), color=(247, 250, 252), duration=duration)
    
    def _create_text_overlay(self, text, duration, font_size=48, color='white', position='center'):
        """Create text overlay with proper formatting"""
        try:
            # Wrap text for better display
            wrapped_text = self._wrap_text_for_display(text, font_size)
            
            # Create text clip
            text_clip = TextClip(
                wrapped_text,
                fontsize=font_size,
                color=color,
                font='Arial-Bold',
                method='caption',
                size=(1000, 400),
                align='center'
            ).set_duration(duration)
            
            # Position the text
            if position == 'center':
                text_clip = text_clip.set_position('center')
            else:
                text_clip = text_clip.set_position(position)
            
            return text_clip
            
        except Exception as e:
            print(f"Error creating text overlay: {str(e)}")
            return TextClip("Error", fontsize=font_size, color=color).set_duration(duration)
    
    def _create_bullet_point_overlay(self, text, duration, font_size=42, color='#2d3748'):
        """Create bullet point overlay"""
        try:
            # Add bullet point
            bullet_text = f"• {text}"
            
            text_clip = TextClip(
                bullet_text,
                fontsize=font_size,
                color=color,
                font='Arial',
                method='caption',
                size=(1000, 200),
                align='left'
            ).set_duration(duration).set_position('center')
            
            return text_clip
            
        except Exception as e:
            print(f"Error creating bullet point overlay: {str(e)}")
            return TextClip("• Error", fontsize=font_size, color=color).set_duration(duration)
    
    def _wrap_text_for_display(self, text, font_size):
        """Wrap text appropriately for video display"""
        # Calculate characters per line based on font size
        chars_per_line = max(30, min(80, 1200 // (font_size // 2)))
        
        # Split into words and wrap
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= chars_per_line:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines[:6])  # Limit to 6 lines max
    
    def _split_content_for_video(self, title, summary, duration):
        """Split content into timed segments"""
        segments = []
        
        # Title segment
        title_duration = min(8, duration * 0.15)
        segments.append({
            'text': title,
            'duration': title_duration,
            'font_size': 64,
            'color': 'white'
        })
        
        # Summary segments
        remaining_duration = duration - title_duration
        summary_words = summary.split()
        
        # Split summary into 2-3 segments
        words_per_segment = len(summary_words) // 3
        segment_duration = remaining_duration / 3
        
        for i in range(3):
            start_idx = i * words_per_segment
            end_idx = start_idx + words_per_segment if i < 2 else len(summary_words)
            segment_text = " ".join(summary_words[start_idx:end_idx])
            
            if segment_text.strip():
                segments.append({
                    'text': segment_text,
                    'duration': segment_duration,
                    'font_size': 36,
                    'color': 'white'
                })
        
        return segments
    
    def _extract_key_points(self, summary):
        """Extract key points from summary"""
        # Simple extraction - split by sentences and take first few
        sentences = summary.split('. ')
        key_points = []
        
        for sentence in sentences[:4]:  # Max 4 key points
            if len(sentence.strip()) > 10:  # Avoid very short sentences
                key_points.append(sentence.strip())
        
        return key_points
    
    def _generate_tts_audio(self, text, duration):
        """Generate text-to-speech audio using free services"""
        try:
            from gtts import gTTS
            
            # Limit text length for TTS
            max_chars = 500  # Adjust based on duration
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
            
            # Generate TTS
            tts = gTTS(text=text, lang='en', slow=False)
            audio_path = os.path.join(self.temp_dir, f"audio_{uuid.uuid4()[:8]}.mp3")
            tts.save(audio_path)
            
            return audio_path
            
        except Exception as e:
            print(f"Error generating TTS audio: {str(e)}")
            return None
    
    def cleanup(self):
        """Clean up temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Error cleaning up: {str(e)}")

# Global instance
video_generator = VideoGenerator()
