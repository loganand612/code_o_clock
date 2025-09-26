export interface Lesson {
  title: string;
  summary: string;
  detail: string;
}

export interface Module {
  title: string;
  lessons: Lesson[];
}

export interface GeneratedCourse {
  course: string;
  modules: Module[];
}

export const difficultyLevels = [
  'Beginner',
  'Intermediate',
  'Advanced',
  'Expert'
] as const;

export const languages = [
  'English',
  'Spanish',
  'French',
  'German',
  'Chinese',
  'Japanese'
] as const;

export type DifficultyLevel = typeof difficultyLevels[number];
export type Language = typeof languages[number];

export interface CourseDetails {
  title: string;
  creatorName: string;
  difficulty: DifficultyLevel;
  language: Language;
  prerequisites: string;
  targetAudience: string;
}

export interface CourseData {
  description: string;
  uploadedFiles: File[];
  urls: string[];
  courseId: string;
  extractedText: string;
  generatedCourse: GeneratedCourse | null;
  courseDetails: CourseDetails;
  sourcesProcessed?: number;
  sourceInfo?: any;
}

export interface CourseStepProps {
  onNext?: () => void;
  onBack?: () => void;
  courseData: CourseData;
  setCourseData: (data: CourseData) => void;
}