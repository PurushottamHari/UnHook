import { NextRequest, NextResponse } from 'next/server';
import { WaitlistService } from '@/lib/services/waitlist-service';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, message, source } = body;

    // Validate required fields
    if (!email) {
      return NextResponse.json(
        { success: false, error: 'Email is required' },
        { status: 400 }
      );
    }

    // Validate email format using service method
    if (!WaitlistService.isValidEmail(email)) {
      return NextResponse.json(
        { success: false, error: 'Invalid email format' },
        { status: 400 }
      );
    }

    const waitlistService = new WaitlistService();
    const result = await waitlistService.addToWaitlist(
      email,
      message || '',
      source || 'website'
    );

    if (!result.success) {
      const statusCode = result.error?.includes('already exists') ? 409 : 500;
      return NextResponse.json(
        {
          success: false,
          error: result.error || 'Failed to add to waitlist',
        },
        { status: statusCode }
      );
    }

    return NextResponse.json({
      success: true,
      message: result.message,
      id: result.id,
    });
  } catch (error) {
    console.error('Error in waitlist API route:', error);
    return NextResponse.json(
      {
        success: false,
        error:
          error instanceof Error ? error.message : 'Unknown error occurred',
      },
      { status: 500 }
    );
  }
}
