import { NextResponse } from 'next/server';
import { MongoClient } from 'mongodb';

export async function GET() {
  try {
    const client = new MongoClient(process.env.MONGODB_URI || 'mongodb://localhost:27017');
    await client.connect();
    const db = client.db(process.env.DATABASE_NAME || 'youtube_newspaper');
    
    // Check what collections exist
    const collections = await db.listCollections().toArray();
    
    // Get a sample document from generated_content
    const generatedContentCollection = db.collection('generated_content');
    const sampleDoc = await generatedContentCollection.findOne({});
    
    // Get count of documents
    const count = await generatedContentCollection.countDocuments();
    
    await client.close();
    
    return NextResponse.json({
      collections: collections.map(c => c.name),
      documentCount: count,
      sampleDocument: sampleDoc ? {
        _id: sampleDoc._id,
        status: sampleDoc.status,
        hasGenerated: !!sampleDoc.generated,
        generatedKeys: sampleDoc.generated ? Object.keys(sampleDoc.generated) : [],
        hasCategory: !!sampleDoc.category,
        hasExternalId: !!sampleDoc.external_id
      } : null
    });
    
  } catch (error) {
    console.error('Error testing database:', error);
    return NextResponse.json(
      { error: 'Database connection failed', details: error.message },
      { status: 500 }
    );
  }
}
