// MongoDB waitlist integration
// This file handles all waitlist operations using MongoDB and keeps business logic separate from components

export interface WaitlistFormData {
  email: string;
  message?: string;
  source?: string; // Track where the form was submitted from
}

export interface WaitlistSubmissionResult {
  success: boolean;
  message: string;
  error?: string;
}

export interface WaitlistDocument {
  email: string;
  message?: string;
  source: string;
  timestamp: number; // Epoch timestamp
}

// MongoDB configuration
const MONGODB_CONFIG = {
  // Note: MongoDB URI is only available on server side
  // Client-side validation is not needed since API handles it
  database: process.env.DATABASE_NAME || 'youtube_newspaper',
  collection: 'waitlist'
};


/**
 * Submit form data to MongoDB waitlist collection
 */
export async function submitToWaitlist(formData: WaitlistFormData): Promise<WaitlistSubmissionResult> {
  try {
    // Prepare the document for MongoDB
    const waitlistDocument: WaitlistDocument = {
      email: formData.email.toLowerCase().trim(),
      message: formData.message?.trim() || '',
      source: formData.source || 'website',
      timestamp: Math.floor(Date.now() / 1000) // Epoch timestamp
    };

    // Submit to MongoDB via API endpoint
    console.log('Submitting waitlist data:', waitlistDocument);
    const response = await fetch('/api/waitlist', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(waitlistDocument)
    });
    
    console.log('Response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    
    if (result.success) {
      return {
        success: true,
        message: 'Thank you for joining our waitlist! We\'ll notify you when Teerth is ready.'
      };
    } else {
      throw new Error(result.error || 'Unknown error from database');
    }

  } catch (error) {
    console.error('Error submitting to waitlist:', error);
    
    return {
      success: false,
      message: 'There was an error submitting your information. Please try again.',
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Get MongoDB configuration status
 * Note: This always returns true since validation happens on server side
 */
export function isMongoDBConfigured(): boolean {
  return true;
}

