import { NextRequest, NextResponse } from 'next/server';

const NEWSPAPER_SERVICE_URL = 'https://unhook-production-b172.up.railway.app';

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function GET(
  request: NextRequest,
  { params }: RouteParams
) {
  try {
    const { id } = await params;
    const userId = request.headers.get('X-User-ID') || request.nextUrl.searchParams.get('userId');

    if (!id) {
      return NextResponse.json(
        { error: 'Article ID is required' },
        { status: 400 }
      );
    }

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    // Fetch interactions from backend
    const backendUrl = `${NEWSPAPER_SERVICE_URL}/list_user_interactions_for_content/${id}`;
    const backendResponse = await fetch(backendUrl, {
      method: 'GET',
      headers: {
        'X-User-ID': userId,
      },
    });

    if (!backendResponse.ok) {
      // If 404, return empty interactions (no interactions yet)
      if (backendResponse.status === 404) {
        return NextResponse.json({
          success: true,
          interactions: [],
        });
      }
      
      const errorData = await backendResponse.json().catch(() => ({}));
      return NextResponse.json(
        {
          error: errorData.detail || 'Failed to fetch interactions',
          message: backendResponse.statusText,
        },
        { status: backendResponse.status }
      );
    }

    const data = await backendResponse.json();
    const interactions = data?.data?.list_response || [];

    return NextResponse.json({
      success: true,
      interactions,
    });
  } catch (error) {
    console.error('Error fetching interactions:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? errorMessage : undefined,
      },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: RouteParams
) {
  try {
    const { id } = await params;
    const body = await request.json();
    const { userId, interactionType, metadata } = body;

    if (!id) {
      return NextResponse.json(
        { error: 'Article ID is required' },
        { status: 400 }
      );
    }

    if (!userId) {
      return NextResponse.json(
        { error: 'User ID is required' },
        { status: 400 }
      );
    }

    if (!interactionType) {
      return NextResponse.json(
        { error: 'Interaction type is required' },
        { status: 400 }
      );
    }

    // Forward request to backend
    const backendUrl = `${NEWSPAPER_SERVICE_URL}/generated_content/${id}/user_interaction`;
    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        interaction_type: interactionType,
        metadata: metadata || {},
      }),
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json().catch(() => ({}));
      return NextResponse.json(
        {
          error: errorData.detail || 'Failed to create interaction',
          message: backendResponse.statusText,
        },
        { status: backendResponse.status }
      );
    }

    const interactionData = await backendResponse.json();

    return NextResponse.json({
      success: true,
      interaction: interactionData,
    });
  } catch (error) {
    console.error('Error creating interaction:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? errorMessage : undefined,
      },
      { status: 500 }
    );
  }
}
