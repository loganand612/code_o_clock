import React, { useState } from 'react';
import axios from 'axios';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  CircularProgress, 
  Card, 
  CardContent, 
  Chip, 
  Alert, 
  Snackbar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Divider,
  Grid
} from '@mui/material';
import { 
  VideoLibrary, 
  PlayArrow, 
  Download, 
  Refresh,
  Style,
  School,
  Visibility
} from '@mui/icons-material';

import { CourseStepProps, Module, Lesson } from '../types';

interface CourseOutcomeProps extends Omit<CourseStepProps, 'setCourseData'> {
  onBack: () => void; // Make onBack required for this component
}

interface VideoGenerationState {
  loading: boolean;
  error: string | null;
  generatedVideos: Array<{
    id: string;
    title: string;
    url: string;
    style: string;
    duration: number;
    type: string;
  }>;
}

export default function CourseOutcome({ onBack, courseData }: CourseOutcomeProps) {
  const [videoState, setVideoState] = useState<VideoGenerationState>({
    loading: false,
    error: null,
    generatedVideos: []
  });
  const [selectedStyle, setSelectedStyle] = useState('modern');

  const updateVideoState = (updates: Partial<VideoGenerationState>) => {
    setVideoState(prev => ({ ...prev, ...updates }));
  };

  const handleGenerateCourseOverview = async () => {
    updateVideoState({ loading: true, error: null });
    
    try {
      const response = await axios.post('http://localhost:5000/generate-course-overview', {
        course_title: courseData.generatedCourse?.course || 'Course',
        course_description: courseData.description || '',
        modules: courseData.generatedCourse?.modules || []
      });
      
      if (response.data && response.data.video_url) {
        const newVideo = {
          id: response.data.video_id,
          title: `${courseData.generatedCourse?.course} - Overview`,
          url: `http://localhost:5000${response.data.video_url}`,
          style: response.data.style,
          duration: response.data.duration,
          type: 'overview'
        };
        
        updateVideoState({
          generatedVideos: [...videoState.generatedVideos, newVideo],
          loading: false
        });
      } else {
        updateVideoState({ error: 'Failed to generate course overview video', loading: false });
      }
    } catch (err: any) {
      updateVideoState({ 
        error: err?.response?.data?.error || 'Error generating course overview video', 
        loading: false 
      });
    }
  };

  const handleGenerateLessonVideo = async (lesson: Lesson, moduleTitle: string) => {
    updateVideoState({ loading: true, error: null });
    
    try {
      const response = await axios.post('http://localhost:5000/generate-lesson-video', {
        lesson_title: lesson.title,
        lesson_summary: lesson.summary,
        lesson_detail: lesson.detail,
        style: selectedStyle
      });
      
      if (response.data && response.data.video_url) {
        const newVideo = {
          id: response.data.video_id,
          title: `${moduleTitle}: ${lesson.title}`,
          url: `http://localhost:5000${response.data.video_url}`,
          style: response.data.style,
          duration: response.data.duration,
          type: 'lesson'
        };
        
        updateVideoState({
          generatedVideos: [...videoState.generatedVideos, newVideo],
          loading: false
        });
      } else {
        updateVideoState({ error: 'Failed to generate lesson video', loading: false });
      }
    } catch (err: any) {
      updateVideoState({ 
        error: err?.response?.data?.error || 'Error generating lesson video', 
        loading: false 
      });
    }
  };

  const handleGenerateSummaryVideo = async () => {
    updateVideoState({ loading: true, error: null });
    
    try {
      // Create a comprehensive summary from all lessons
      const summary = courseData.generatedCourse?.modules
        .map(module => 
          `${module.title}: ${module.lessons.map(lesson => lesson.summary).join(' ')}`
        ).join('\n\n') || '';
      
      const response = await axios.post('http://localhost:5000/generate-video', {
        title: courseData.generatedCourse?.course || 'Course Summary',
        summary: summary,
        style: selectedStyle,
        duration: 60
      });
      
      if (response.data && response.data.video_url) {
        const newVideo = {
          id: response.data.video_id,
          title: `${courseData.generatedCourse?.course} - Complete Summary`,
          url: `http://localhost:5000${response.data.video_url}`,
          style: response.data.style,
          duration: response.data.duration,
          type: 'summary'
        };
        
        updateVideoState({
          generatedVideos: [...videoState.generatedVideos, newVideo],
          loading: false
        });
      } else {
        updateVideoState({ error: 'Failed to generate summary video', loading: false });
      }
    } catch (err: any) {
      updateVideoState({ 
        error: err?.response?.data?.error || 'Error generating summary video', 
        loading: false 
      });
    }
  };

  return (
    <Paper elevation={0} sx={{ p: 4, maxWidth: '1000px', mx: 'auto' }}>
      <Typography variant="h4" component="h1" align="center" gutterBottom>
        <VideoLibrary sx={{ mr: 2, verticalAlign: 'middle' }} />
        Generated Course & Videos
      </Typography>
      
      {courseData.generatedCourse ? (
        <Box sx={{ mt: 3 }}>
          {/* Course Title */}
          <Typography variant="h5" gutterBottom color="primary">
            {courseData.generatedCourse.course}
          </Typography>
          
          {/* Video Generation Controls */}
          <Card sx={{ mb: 4, bgcolor: 'primary.50' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                <Style sx={{ mr: 1, verticalAlign: 'middle' }} />
                Video Generation Options
              </Typography>
              
              <Grid container spacing={2} alignItems="center" sx={{ mb: 2 }}>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Video Style</InputLabel>
                    <Select
                      value={selectedStyle}
                      label="Video Style"
                      onChange={(e) => setSelectedStyle(e.target.value)}
                    >
                      <MenuItem value="modern">Modern (Gradient Background)</MenuItem>
                      <MenuItem value="minimal">Minimal (Clean & Simple)</MenuItem>
                      <MenuItem value="educational">Educational (Bullet Points)</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={handleGenerateCourseOverview}
                      disabled={videoState.loading}
                      startIcon={<PlayArrow />}
                      size="small"
                    >
                      Course Overview
                    </Button>
                    <Button
                      variant="contained"
                      color="secondary"
                      onClick={handleGenerateSummaryVideo}
                      disabled={videoState.loading}
                      startIcon={<Refresh />}
                      size="small"
                    >
                      Complete Summary
                    </Button>
                  </Box>
                </Grid>
              </Grid>
              
              {videoState.loading && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body2">Generating video...</Typography>
                </Box>
              )}
              
              {videoState.error && (
                <Alert severity="error" sx={{ mt: 1 }}>
                  {videoState.error}
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Generated Videos */}
          {videoState.generatedVideos.length > 0 && (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Download sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Generated Videos
                </Typography>
                <Grid container spacing={2}>
                  {videoState.generatedVideos.map((video) => (
                    <Grid item xs={12} sm={6} md={4} key={video.id}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="subtitle2" gutterBottom>
                            {video.title}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                            <Chip 
                              label={video.style} 
                              size="small" 
                              color="primary" 
                              variant="outlined" 
                            />
                            <Chip 
                              label={`${video.duration}s`} 
                              size="small" 
                              color="secondary" 
                              variant="outlined" 
                            />
                          </Box>
                          <Button
                            variant="outlined"
                            fullWidth
                            startIcon={<Download />}
                            href={video.url}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            Download
                          </Button>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          )}

          {/* Course Content */}
          <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
            <School sx={{ mr: 1, verticalAlign: 'middle' }} />
            Course Content
          </Typography>
          
          {courseData.generatedCourse.modules.map((module: Module, moduleIndex: number) => (
            <Card key={moduleIndex} sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, color: 'primary.main' }}>
                  Module {moduleIndex + 1}: {module.title}
                </Typography>
                
                {module.lessons.map((lesson: Lesson, lessonIndex: number) => (
                  <Box key={lessonIndex} sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold', flex: 1 }}>
                        Lesson {lessonIndex + 1}: {lesson.title}
                      </Typography>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => handleGenerateLessonVideo(lesson, module.title)}
                        disabled={videoState.loading}
                        startIcon={<VideoLibrary />}
                      >
                        Generate Video
                      </Button>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {lesson.summary}
                    </Typography>
                    <Typography variant="body1" sx={{ textAlign: 'justify' }}>
                      {lesson.detail}
                    </Typography>
                    
                    {lessonIndex < module.lessons.length - 1 && <Divider sx={{ mt: 2 }} />}
                  </Box>
                ))}
              </CardContent>
            </Card>
          ))}
        </Box>
      ) : (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <CircularProgress />
        </Box>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          variant="text"
          color="primary"
          onClick={onBack}
        >
          Previous
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={() => window.print()}
          startIcon={<Visibility />}
        >
          Print Course
        </Button>
      </Box>

      <Snackbar 
        open={!!videoState.error} 
        autoHideDuration={6000} 
        onClose={() => updateVideoState({ error: null })}
      >
        <Alert onClose={() => updateVideoState({ error: null })} severity="error">
          {videoState.error}
        </Alert>
      </Snackbar>
    </Paper>
  );
}