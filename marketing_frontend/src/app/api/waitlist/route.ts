import { NextRequest, NextResponse } from 'next/server';
import { MongoClient } from 'mongodb';

// MongoDB configuration
const MONGODB_URI = process.env.MONGODB_URI;
const DATABASE_NAME = process.env.DATABASE_NAME || 'youtube_newspaper';
const COLLECTION_NAME = 'waitlist';

interface WaitlistDocument {
  email: string;
  message?: string;
  source: string;
  timestamp: number;
}

export async function POST(request: NextRequest) {
  if (!MONGODB_URI) {
    return NextResponse.json(
      { success: false, error: 'MongoDB URI is not configured' },
      { status: 500 }
    );
  }

  try {
    const body = await request.json();
    const { email, message, source, timestamp }: WaitlistDocument = body;

    // Validate required fields
    if (!email || !timestamp) {
      return NextResponse.json(
        { success: false, error: 'Email and timestamp are required' },
        { status: 400 }
      );
    }

    // Connect to MongoDB
    const client = new MongoClient(MONGODB_URI);
    await client.connect();

    try {
      const db = client.db(DATABASE_NAME);
      const collection = db.collection(COLLECTION_NAME);

      // Check if email already exists
      const existingEntry = await collection.findOne({
        email: email.toLowerCase(),
      });

      if (existingEntry) {
        return NextResponse.json(
          { success: false, error: 'Email already exists in waitlist' },
          { status: 409 }
        );
      }

      // Insert new waitlist entry
      const waitlistEntry: WaitlistDocument = {
        email: email.toLowerCase(),
        message: message || '',
        source: source || 'website',
        timestamp,
      };

      const result = await collection.insertOne(waitlistEntry);

      return NextResponse.json({
        success: true,
        message: 'Successfully added to waitlist',
        id: result.insertedId,
      });
    } finally {
      await client.close();
    }
  } catch (error) {
    console.error('Error adding to waitlist:', error);

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
