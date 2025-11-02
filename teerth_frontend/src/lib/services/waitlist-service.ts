import { getDatabase } from '@/lib/db/connection';

// Shared types for waitlist operations
export interface WaitlistDocument {
  email: string;
  message?: string;
  source: string;
  timestamp: number;
}

export interface WaitlistFormData {
  email: string;
  message?: string;
  source?: string;
}

export interface WaitlistSubmissionResult {
  success: boolean;
  message: string;
  id?: string;
  error?: string;
}

export interface AddToWaitlistResult {
  success: boolean;
  message: string;
  id?: string;
  error?: string;
}

export class WaitlistService {
  /**
   * Validate email format
   */
  static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  async addToWaitlist(
    email: string,
    message: string,
    source: string
  ): Promise<AddToWaitlistResult> {
    try {
      const db = await getDatabase();
      const collection = db.collection('waitlist');

      const normalizedEmail = email.toLowerCase().trim();

      // Check if email already exists
      const existingEntry = await collection.findOne({
        email: normalizedEmail,
      });

      if (existingEntry) {
        return {
          success: false,
          message: 'Email already exists in waitlist',
          error: 'Email already exists in waitlist',
        };
      }

      // Prepare waitlist entry
      const waitlistEntry: WaitlistDocument = {
        email: normalizedEmail,
        message: message?.trim() || '',
        source: source || 'website',
        timestamp: Math.floor(Date.now() / 1000), // Epoch timestamp
      };

      // Insert new waitlist entry
      const result = await collection.insertOne(waitlistEntry);

      return {
        success: true,
        message: 'Successfully added to waitlist',
        id: result.insertedId.toString(),
      };
    } catch (error) {
      console.error('Error adding to waitlist:', error);
      return {
        success: false,
        message:
          error instanceof Error ? error.message : 'Unknown error occurred',
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }
}
