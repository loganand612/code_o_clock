import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  CircularProgress,
  Alert,
  IconButton,
  Divider,
  Chip
} from '@mui/material';
import {
  Close,
  MenuBook,
  Schedule,
  CheckCircle
} from '@mui/icons-material';
import { Lesson } from '../types';
import axios from 'axios';

interface LessonModalProps {
  open: boolean;
  onClose: () => void;
  lesson: Lesson | null;
  courseId: string;
}

export default function LessonModal({ open, onClose, lesson, courseId }: LessonModalProps) {
  const [lessonContent, setLessonContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && lesson) {
      fetchLessonContent();
    }
  }, [open, lesson]);

  const fetchLessonContent = async () => {
    if (!lesson) return;

    setLoading(true);
    setError(null);
    setLessonContent('');

    try {
      const response = await axios.post('http://localhost:5000/lesson-content', {
        lesson_title: lesson.title,
        lesson_summary: lesson.summary,
        course_id: courseId
      });

      setLessonContent(response.data.content);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.error || err.message;
        setError(`Failed to load lesson content: ${errorMessage}`);
      } else {
        setError('Failed to load lesson content. Please try again.');
      }
      console.error('Lesson content error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setLessonContent('');
    setError(null);
    onClose();
  };

  if (!lesson) return null;

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          maxHeight: '90vh'
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        pb: 1
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <MenuBook sx={{ color: 'primary.main' }} />
          <Typography variant="h6" component="h2" sx={{ fontWeight: 600 }}>
            {lesson.title}
          </Typography>
        </Box>
        
        <IconButton
          onClick={handleClose}
          sx={{ 
            color: 'text.secondary',
            '&:hover': {
              backgroundColor: 'action.hover'
            }
          }}
        >
          <Close />
        </IconButton>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ p: 3 }}>
        {/* Lesson Summary */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            {lesson.summary}
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              icon={<Schedule />}
              label="15-20 min read"
              size="small"
              variant="outlined"
              color="primary"
            />
            <Chip
              icon={<CheckCircle />}
              label="Comprehensive"
              size="small"
              variant="outlined"
              color="success"
            />
          </Box>
        </Box>

        <Divider sx={{ mb: 3 }} />

        {/* Lesson Content */}
        <Box sx={{ minHeight: 200 }}>
          {loading && (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center',
              py: 4
            }}>
              <CircularProgress size={40} sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                Generating comprehensive lesson content...
              </Typography>
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {lessonContent && !loading && (
            <Box sx={{ 
              '& p': { 
                mb: 2, 
                lineHeight: 1.7,
                fontSize: '1rem'
              },
              '& h1, & h2, & h3, & h4, & h5, & h6': {
                fontWeight: 600,
                mb: 1.5,
                mt: 2,
                color: 'text.primary'
              },
              '& h1': { fontSize: '1.5rem' },
              '& h2': { fontSize: '1.3rem' },
              '& h3': { fontSize: '1.2rem' },
              '& ul, & ol': {
                pl: 3,
                mb: 2
              },
              '& li': {
                mb: 0.5
              },
              '& blockquote': {
                borderLeft: '4px solid',
                borderColor: 'primary.main',
                pl: 2,
                py: 1,
                mb: 2,
                backgroundColor: 'action.hover',
                fontStyle: 'italic'
              },
              '& strong': {
                fontWeight: 600,
                color: 'text.primary'
              }
            }}>
              {lessonContent.split('\n').map((paragraph, index) => {
                if (paragraph.trim() === '') return null;
                
                // Check if it's a heading (starts with # or is all caps)
                if (paragraph.startsWith('#') || (paragraph.length < 50 && paragraph === paragraph.toUpperCase() && paragraph.length > 3)) {
                  const level = paragraph.startsWith('#') ? paragraph.match(/^#+/)?.[0].length || 1 : 2;
                  const text = paragraph.replace(/^#+\s*/, '');
                  const Component = level === 1 ? 'h1' : level === 2 ? 'h2' : 'h3';
                  
                  return (
                    <Typography
                      key={index}
                      component={Component}
                      variant={level === 1 ? 'h5' : level === 2 ? 'h6' : 'subtitle1'}
                      sx={{ 
                        fontWeight: 600, 
                        mb: 1.5, 
                        mt: index > 0 ? 2 : 0,
                        color: 'text.primary'
                      }}
                    >
                      {text}
                    </Typography>
                  );
                }
                
                // Regular paragraph
                return (
                  <Typography
                    key={index}
                    variant="body1"
                    sx={{ 
                      mb: 2, 
                      lineHeight: 1.7,
                      textAlign: 'justify'
                    }}
                  >
                    {paragraph}
                  </Typography>
                );
              })}
            </Box>
          )}

          {!loading && !error && !lessonContent && (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center',
              py: 4,
              textAlign: 'center'
            }}>
              <MenuBook sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body1" color="text.secondary">
                Click "Load Content" to generate detailed lesson material
              </Typography>
            </Box>
          )}
        </Box>
      </DialogContent>

      <Divider />

      <DialogActions sx={{ p: 3, gap: 1 }}>
        <Button
          onClick={handleClose}
          variant="outlined"
          color="primary"
        >
          Close
        </Button>
        
        {error && (
          <Button
            onClick={fetchLessonContent}
            variant="contained"
            color="primary"
            disabled={loading}
          >
            {loading ? (
              <>
                <CircularProgress size={16} color="inherit" sx={{ mr: 1 }} />
                Loading...
              </>
            ) : (
              'Retry'
            )}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
}
