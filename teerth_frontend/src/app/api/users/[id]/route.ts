import { NextRequest, NextResponse } from 'next/server';
import { UserService } from '@/lib/services/user-service';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: userId } = await params;

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    const userService = new UserService();
    const user = await userService.getUser(userId);

    if (!user) {
      return NextResponse.json(
        { error: 'User not found' },
        { status: 404 }
      );
    }

    // Return sanitized user data
    return NextResponse.json({
      success: true,
      user: {
        id: user.id,
        name: user.name,
        username: user.email.split('@')[0], // Fallback username if not available
        role: 'user', // Default role for now
        createdAt: user.created_at,
      },
    });
  } catch (error) {
    console.error('Error fetching user:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
