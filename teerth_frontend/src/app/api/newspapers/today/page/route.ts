import { NextRequest, NextResponse } from 'next/server';
import { NewspaperService } from '@/lib/services/newspaper-service';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const userId = searchParams.get('userId');
    const date = searchParams.get('date'); // Optional date parameter (YYYY-MM-DD format)
    const startingAfter = searchParams.get('startingAfter');
    const pageLimit = parseInt(searchParams.get('pageLimit') || '10');

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    const newspaperService = new NewspaperService();
    
    // Use provided date or default to today
    const targetDate = date || new Date().toISOString().split('T')[0];
    
    // Fetch single page of articles using date (V2)
    const pageData = await newspaperService.getNewspaperArticlesPage(
      targetDate,
      userId,
      startingAfter || null
    );
    
    if (pageData.articles.length === 0 && !startingAfter) {
      return NextResponse.json(
        { error: 'No digest available for this date' },
        { status: 404 }
      );
    }
    
    return NextResponse.json({
      success: true,
      articles: pageData.articles,
      hasNext: pageData.hasNext,
      nextCursor: pageData.nextCursor,
      newspaperId: pageData.newspaperId,
    });
  } catch (error) {
    console.error('Error fetching newspaper page:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    const errorStack = error instanceof Error ? error.stack : undefined;
    
    // Log full error details
    console.error('Error details:', {
      message: errorMessage,
      stack: errorStack,
    });

    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? errorMessage : undefined,
      },
      { status: 500 }
    );
  }
}
