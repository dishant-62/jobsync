// Barrel export for API services.
// Simplifies imports: `import { fetchJobs } from '@/services'`
// Note: The Axios-based jobApi lives in src/api/client.ts

export { fetchJobs, fetchJobById } from './api';
export { resumeApi } from './resumeApi';
