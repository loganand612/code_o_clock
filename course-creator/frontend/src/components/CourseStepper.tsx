import React, { useState } from 'react';
import { Stepper, Step, StepLabel, Box } from '@mui/material';
import CourseDescription from './CourseDescription';
import CourseUpload from './CourseUpload';
import CourseDetails from './CourseDetails';
import CourseOutcome from './CourseOutcome';
import { CourseData } from '../types';

const steps = ['Course', 'Upload', 'Learner', 'Outcome'];

export default function CourseStepper() {
  const [activeStep, setActiveStep] = useState(0);
  const [courseData, setCourseData] = useState<CourseData>({
    description: '',
    uploadedFiles: [],
    urls: [],
    courseId: '',
    extractedText: '',
    generatedCourse: null,
    courseDetails: {
      title: '',
      creatorName: '',
      difficulty: 'Beginner',  // Default value
      language: 'English',    // Default value
      prerequisites: '',
      targetAudience: ''
    }
  });

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return <CourseDescription 
                 onNext={handleNext} 
                 courseData={courseData} 
                 setCourseData={setCourseData} 
               />;
      case 1:
        return <CourseUpload 
                 onNext={handleNext} 
                 onBack={handleBack}
                 courseData={courseData} 
                 setCourseData={setCourseData} 
               />;
      case 2:
        return <CourseDetails 
                 onNext={handleNext} 
                 onBack={handleBack}
                 courseData={courseData} 
                 setCourseData={setCourseData} 
               />;
      case 3:
        return <CourseOutcome 
                 onBack={handleBack}
                 courseData={courseData} 
               />;
      default:
        return 'Unknown step';
    }
  };

  return (
    <Box sx={{ width: '100%', p: 4 }}>
      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      {getStepContent(activeStep)}
    </Box>
  );
}