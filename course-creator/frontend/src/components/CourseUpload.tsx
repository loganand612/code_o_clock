import React, { useCallback, useState } from 'react';
import { 
  Box, 
  Button, 
  Typography, 
  Paper, 
  Tab, 
  Tabs,
  CircularProgress,
  Alert,
  Snackbar,
  TextField,
  Chip,
  IconButton,
  Card,
  CardContent,
  Divider
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import LinkIcon from '@mui/icons-material/Link';
import DescriptionIcon from '@mui/icons-material/Description';
import axios from 'axios';

import { CourseData, CourseStepProps } from '../types';

interface CourseUploadProps extends CourseStepProps {}

export default function CourseUpload({ onNext, onBack, courseData, setCourseData }: CourseUploadProps) {
  const [uploadType, setUploadType] = useState('files');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newUrl, setNewUrl] = useState('');

  const addUrl = () => {
    if (newUrl.trim() && !courseData.urls.includes(newUrl.trim())) {
      setCourseData({
        ...courseData,
        urls: [...courseData.urls, newUrl.trim()]
      });
      setNewUrl('');
    }
  };

  const removeUrl = (urlToRemove: string) => {
    setCourseData({
      ...courseData,
      urls: courseData.urls.filter(url => url !== urlToRemove)
    });
  };

  const handleUpload = async () => {
    setLoading(true);
    setError(null);
    const formData = new FormData();
    
    try {
      let hasContent = false;

      // Add files
      if (courseData.uploadedFiles.length > 0) {
        courseData.uploadedFiles.forEach(file => {
          formData.append('file', file);
        });
        hasContent = true;
      }

      // Add URLs
      if (courseData.urls.length > 0) {
        formData.append('urls', JSON.stringify(courseData.urls));
        hasContent = true;
      }

      if (!hasContent) {
        throw new Error('Please provide at least one file or URL');
      }

      // Add the user's prompt/description
      formData.append('prompt', courseData.description || '');

      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 second timeout for multiple sources
        maxContentLength: 100 * 1024 * 1024, // 100MB max file size
      });

      // Store the course ID and extracted text in courseData
      setCourseData({
        ...courseData,
        courseId: response.data.course_id,
        extractedText: response.data.extracted_text,
        generatedCourse: response.data.course,
        sourcesProcessed: response.data.sources_processed,
        sourceInfo: response.data.source_info
      });

      if (onNext) onNext();
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const errorMessage = err.response?.data?.error || err.message;
        setError(`Upload failed: ${errorMessage}`);
      } else {
        setError('Failed to process content. Please try again.');
      }
      console.error('Upload error:', err);
    } finally {
      setLoading(false);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setCourseData({
      ...courseData,
      uploadedFiles: [...courseData.uploadedFiles, ...acceptedFiles]
    });
    setError(null);
  }, [courseData, setCourseData]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/csv': ['.csv']
    }
  });

  const hasContent = courseData.uploadedFiles.length > 0 || courseData.urls.length > 0;

  return (
    <Paper elevation={0} sx={{ p: 4, maxWidth: '900px', mx: 'auto' }}>
      <Typography variant="h4" component="h1" align="center" gutterBottom>
        What course will you create?
      </Typography>
      <Typography variant="subtitle1" align="center" color="text.secondary" sx={{ mb: 4 }}>
        Upload files and/or add URLs to train AI on existing content
      </Typography>

      {/* Enhanced Prompt Input */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            <DescriptionIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Course Description/Prompt
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Describe what kind of course you want to create"
            value={courseData.description}
            onChange={(e) => setCourseData({ ...courseData, description: e.target.value })}
            placeholder="e.g., Create a beginner-friendly course on machine learning fundamentals, focusing on practical applications..."
            sx={{ mb: 2 }}
          />
          <Typography variant="caption" color="text.secondary">
            This prompt will guide the AI in creating your course structure and content
          </Typography>
        </CardContent>
      </Card>

      <Tabs
        value={uploadType}
        onChange={(_, newValue) => setUploadType(newValue)}
        centered
        sx={{ mb: 4 }}
      >
        <Tab label="Files" value="files" />
        <Tab label="URLs/Links" value="websites" />
        <Tab label="Both" value="both" />
      </Tabs>

      {/* Files Section */}
      {(uploadType === 'files' || uploadType === 'both') && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <CloudUploadIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Upload Files
            </Typography>
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.300',
                borderRadius: 2,
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                bgcolor: isDragActive ? 'action.hover' : 'background.paper',
              }}
            >
              <input {...getInputProps()} />
              <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography>
                Drag & Drop or Browse to upload files
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Supported: PDF, DOCX, PPTX, TXT, CSV
              </Typography>
            </Box>
            
            {courseData.uploadedFiles.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Selected Files:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {courseData.uploadedFiles.map((file, index) => (
                    <Chip
                      key={index}
                      label={file.name}
                      onDelete={() => {
                        const newFiles = courseData.uploadedFiles.filter((_, i) => i !== index);
                        setCourseData({ ...courseData, uploadedFiles: newFiles });
                      }}
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* URLs Section */}
      {(uploadType === 'websites' || uploadType === 'both') && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              <LinkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
              Add URLs/Links
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                fullWidth
                label="Enter URL"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                placeholder="https://example.com or https://youtube.com/watch?v=..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    addUrl();
                  }
                }}
              />
              <Button
                variant="contained"
                onClick={addUrl}
                disabled={!newUrl.trim() || courseData.urls.includes(newUrl.trim())}
                startIcon={<AddIcon />}
              >
                Add
              </Button>
            </Box>
            
            {courseData.urls.length > 0 && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Added URLs:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {courseData.urls.map((url, index) => (
                    <Chip
                      key={index}
                      label={url}
                      onDelete={() => removeUrl(url)}
                      color="secondary"
                      variant="outlined"
                      icon={<LinkIcon />}
                    />
                  ))}
                </Box>
              </Box>
            )}
            
            <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
              Supports websites, YouTube videos, and other content sources
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Summary */}
      {hasContent && (
        <Card sx={{ mb: 4, bgcolor: 'primary.50' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Content Summary
            </Typography>
            <Typography variant="body2">
              • {courseData.uploadedFiles.length} file(s) selected
            </Typography>
            <Typography variant="body2">
              • {courseData.urls.length} URL(s) added
            </Typography>
            {courseData.description && (
              <Typography variant="body2">
                • Custom prompt: "{courseData.description.substring(0, 100)}{courseData.description.length > 100 ? '...' : ''}"
              </Typography>
            )}
          </CardContent>
        </Card>
      )}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
        <Button
          variant="text"
          color="primary"
          onClick={onBack}
          disabled={loading}
        >
          Previous
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={loading || !hasContent}
          size="large"
        >
          {loading ? (
            <>
              <CircularProgress size={20} color="inherit" sx={{ mr: 1 }} />
              Processing Content...
            </>
          ) : 'Generate Course'}
        </Button>
      </Box>

      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)}>
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>
    </Paper>
  );
}