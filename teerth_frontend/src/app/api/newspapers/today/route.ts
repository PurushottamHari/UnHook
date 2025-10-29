import { NextResponse } from 'next/server';
import { NewspaperService } from '@/lib/services/newspaper-service';

export async function GET() {
  try {
    const newspaperService = new NewspaperService();
    const newspaper = await newspaperService.getTodayNewspaper();

    if (!newspaper) {
      return NextResponse.json(
        { error: 'No newspaper found for today' },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      newspaper,
    });
  } catch (error) {
    console.error('Error fetching today\'s newspaper:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
