/**
 * Client for interacting with the user service.
 * Follows the same pattern as data_processing_service/external/user_service/client.py
 */

export type Weekday = 'MONDAY' | 'TUESDAY' | 'WEDNESDAY' | 'THURSDAY' | 'FRIDAY' | 'SATURDAY' | 'SUNDAY';

export type CategoryName =
  | 'TECHNOLOGY'
  | 'SCIENCE'
  | 'BUSINESS'
  | 'HEALTH'
  | 'COMEDY'
  | 'SPORTS'
  | 'NEWS'
  | 'EDUCATION'
  | 'ENVIRONMENT'
  | 'CULTURE'
  | 'SPIRITUALITY'
  | 'MOVIES'
  | 'PERSPECTIVES'
  | 'GAMING'
  | 'MUSIC';

export type OutputType = 'VERY_SHORT' | 'SHORT' | 'MEDIUM' | 'LONG';

export const WEEKDAY_MAP: Record<number, Weekday> = {
  0: 'MONDAY',
  1: 'TUESDAY',
  2: 'WEDNESDAY',
  3: 'THURSDAY',
  4: 'FRIDAY',
  5: 'SATURDAY',
  6: 'SUNDAY',
};

export interface Interest {
  category_name: CategoryName;
  category_definition: string;
  weekdays: Weekday[];
  output_type: OutputType;
}

export interface NotInterested {
  category_definition: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  max_reading_time_per_day_mins: number;
  interested: Interest[];
  not_interested: NotInterested[];
  manual_configs?: Record<string, unknown>;
}

export class UserService {
  private baseUrl: string;
  private timeout: number;

  constructor() {
    // Require user service URL from environment variable
    const userServiceUrl = process.env.USER_SERVICE_URL || process.env.NEXT_PUBLIC_USER_SERVICE_URL;
    
    if (!userServiceUrl) {
      throw new Error(
        'USER_SERVICE_URL or NEXT_PUBLIC_USER_SERVICE_URL environment variable is required'
      );
    }
    
    this.baseUrl = userServiceUrl;
    this.timeout = 120000; // 2 minutes in milliseconds
  }

  /**
   * Get the full user service URL
   */
  private getServiceUrl(): string {
    return this.baseUrl;
  }

  /**
   * Get today's weekday in Asia/Kolkata timezone
   * Returns weekday as string: MONDAY, TUESDAY, etc.
   * Matches Python's weekday() logic: 0=Monday, 6=Sunday
   */
  private getTodayWeekday(): Weekday {
    // Convert to Asia/Kolkata timezone
    const now = new Date();
    const istDate = new Date(now.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
    // JavaScript getDay(): 0=Sunday, 1=Monday, ..., 6=Saturday
    // Python weekday(): 0=Monday, 1=Tuesday, ..., 6=Sunday
    // Convert JS to Python format: (getDay() + 6) % 7
    const jsWeekday = istDate.getDay();
    const pythonWeekday = (jsWeekday + 6) % 7; // Convert to Python weekday format
    
    return WEEKDAY_MAP[pythonWeekday];
  }

  /**
   * Get weekday for a specific date in Asia/Kolkata timezone
   * @param date - Date string in YYYY-MM-DD format
   * @returns Weekday as string: MONDAY, TUESDAY, etc.
   */
  private getWeekdayForDate(date: string): Weekday {
    // Parse the date and convert to Asia/Kolkata timezone
    const dateObj = new Date(date + 'T00:00:00');
    const istDate = new Date(dateObj.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
    // JavaScript getDay(): 0=Sunday, 1=Monday, ..., 6=Saturday
    // Python weekday(): 0=Monday, 1=Tuesday, ..., 6=Sunday
    // Convert JS to Python format: (getDay() + 6) % 7
    const jsWeekday = istDate.getDay();
    const pythonWeekday = (jsWeekday + 6) % 7; // Convert to Python weekday format
    
    return WEEKDAY_MAP[pythonWeekday];
  }

  /**
   * Fetch user data from the user service.
   *
   * @param user_id - The unique identifier of the user
   * @returns User object if found, null otherwise
   */
  async getUser(userId: string): Promise<User | null> {
    try {
      const url = `${this.getServiceUrl()}/users/${userId}`;
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          accept: 'application/json',
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.status === 404) {
        return null;
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data as User;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.error('Request timeout:', error);
      } else {
        console.error('Error fetching user from user service:', error);
      }
      return null;
    }
  }

  /**
   * Get user's selected categories for today's weekday
   *
   * @param userId - The unique identifier of the user
   * @returns Array of category names that the user has selected for today's weekday
   */
  async getUserCategoriesForToday(userId: string): Promise<string[]> {
    try {
      const user = await this.getUser(userId);
      
      if (!user || !user.interested) {
        return [];
      }
      
      const todayWeekday = this.getTodayWeekday();
      const categories: string[] = [];
      
      // Filter interests that include today's weekday
      for (const interest of user.interested) {
        if (interest.weekdays && interest.weekdays.includes(todayWeekday)) {
          if (interest.category_name) {
            categories.push(interest.category_name);
          }
        }
      }
      
      return categories;
    } catch (error) {
      console.error('Error fetching user categories:', error);
      return [];
    }
  }

  /**
   * Get user's selected categories for a specific date's weekday
   *
   * @param userId - The unique identifier of the user
   * @param date - Date string in YYYY-MM-DD format
   * @returns Array of category names that the user has selected for the date's weekday
   */
  async getUserCategoriesForDate(userId: string, date: string): Promise<string[]> {
    try {
      const user = await this.getUser(userId);
      
      if (!user || !user.interested) {
        return [];
      }
      
      const dateWeekday = this.getWeekdayForDate(date);
      const categories: string[] = [];
      
      // Filter interests that include the date's weekday
      for (const interest of user.interested) {
        if (interest.weekdays && interest.weekdays.includes(dateWeekday)) {
          if (interest.category_name) {
            categories.push(interest.category_name);
          }
        }
      }
      
      return categories;
    } catch (error) {
      console.error('Error fetching user categories for date:', error);
      return [];
    }
  }
}

