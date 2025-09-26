import React from 'react';
import { Box, Button, Typography, Paper, CircularProgress } from '@mui/material';

import { CourseStepProps, Module, Lesson } from '../types';

interface CourseOutcomeProps extends Omit<CourseStepProps, 'setCourseData'> {
  onBack: () => void; // Make onBack required for this component
}

export default function CourseOutcome({ onBack, courseData }: CourseOutcomeProps) {
  return (
    <Paper elevation={0} sx={{ p: 4, maxWidth: '800px', mx: 'auto' }}>
      <Typography variant="h4" component="h1" align="center" gutterBottom>
        Generated Course
      </Typography>
      
      {courseData.generatedCourse ? (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h5" gutterBottom>
            {courseData.generatedCourse.course}
          </Typography>
          
          {courseData.generatedCourse.modules.map((module: Module, moduleIndex: number) => (
            <Box key={moduleIndex} sx={{ mb: 4 }}>
              <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
                Module {moduleIndex + 1}: {module.title}
              </Typography>
              
              {module.lessons.map((lesson: Lesson, lessonIndex: number) => (
                <Box key={lessonIndex} sx={{ ml: 2, mb: 2 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                    Lesson {lessonIndex + 1}: {lesson.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {lesson.summary}
                  </Typography>
                  <Typography variant="body1">
                    {lesson.detail}
                  </Typography>
                </Box>
              ))}
            </Box>
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
      </Box>
    </Paper>
  );
}