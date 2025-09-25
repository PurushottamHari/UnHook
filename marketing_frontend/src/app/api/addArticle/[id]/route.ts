import { NextResponse } from 'next/server';
import { cacheArticle, CachedArticle } from '@/lib/cache/article-cache';
import { MongoClient } from 'mongodb';

interface AddArticleParams {
  params: Promise<{
    id: string;
  }>;
}

async function fetchArticleFromMongoDB(articleId: string): Promise<CachedArticle | null> {
  try {
    // Use the same MongoDB connection as the scrappy frontend app
    const client = new MongoClient(process.env.MONGODB_URI || 'mongodb://localhost:27017');
    await client.connect();
    const db = client.db(process.env.DATABASE_NAME || 'youtube_newspaper');
    
    // Fetch from generated_content collection
    const generatedContentCollection = db.collection('generated_content');
    
    // Try different query approaches
    let doc = await generatedContentCollection.findOne({ "_id": articleId });
    
    // If not found by _id, try by ObjectId
    if (!doc) {
      try {
        const { ObjectId } = require('mongodb');
        doc = await generatedContentCollection.findOne({ "_id": new ObjectId(articleId) });
      } catch (e) {
        // ObjectId conversion failed, continue
      }
    }
    
    // If still not found, try to find any document to see what's available
    if (!doc) {
      const sampleDoc = await generatedContentCollection.findOne({});
      console.log('Sample document structure:', sampleDoc ? Object.keys(sampleDoc) : 'No documents found');
      console.log('Looking for article ID:', articleId);
      await client.close();
      return null;
    }
    
    // Extract title from VERY_SHORT content
    let title = '';
    const generated = doc.generated || {};
    if (generated.VERY_SHORT && generated.VERY_SHORT.string) {
      title = generated.VERY_SHORT.string;
    }
    
    // If no title from VERY_SHORT, try to extract from SHORT
    if (!title && generated.SHORT && generated.SHORT.string) {
      const summary = generated.SHORT.string;
      title = summary.split('.')[0].length > 50 
        ? summary.split('.')[0].substring(0, 50) + '...'
        : summary.split('.')[0];
    }
    
    // Get content - prefer LONG, then MEDIUM, then SHORT
    let content = '';
    if (generated.LONG && generated.LONG.markdown_string) {
      content = generated.LONG.markdown_string;
    } else if (generated.LONG && generated.LONG.string) {
      content = generated.LONG.string;
    } else if (generated.MEDIUM && generated.MEDIUM.markdown_string) {
      content = generated.MEDIUM.markdown_string;
    } else if (generated.MEDIUM && generated.MEDIUM.string) {
      content = generated.MEDIUM.string;
    } else if (generated.SHORT && generated.SHORT.string) {
      content = generated.SHORT.string;
    }
    
    // Get category
    const category = doc.category?.category || 'TECHNOLOGY';
    
    // Get reading time
    const readingTimeSeconds = doc.reading_time_seconds || 0;
    const minutes = Math.ceil(readingTimeSeconds / 60);
    const time_to_read = minutes < 1 ? 'Less than 1 min read' : `${minutes} min read`;
    
    // Get published date
    let published_at = new Date().toISOString();
    if (doc.content_generated_at) {
      published_at = new Date(doc.content_generated_at * 1000).toISOString();
    } else if (doc.created_at) {
      published_at = new Date(doc.created_at * 1000).toISOString();
    }
    
    // Get external_id (YouTube video ID)
    const external_id = doc.external_id || '';
    
    // Fetch channel name from collected_content collection
    let youtube_channel = '';
    if (external_id) {
      const collectedContentCollection = db.collection('collected_content');
      const collectedDoc = await collectedContentCollection.findOne({ "external_id": external_id });
      
      if (collectedDoc && collectedDoc.data && collectedDoc.data.YOUTUBE_VIDEO) {
        const videoDetails = collectedDoc.data.YOUTUBE_VIDEO;
        if (videoDetails.channel_name) {
          youtube_channel = videoDetails.channel_name;
        }
      }
    }
    
    // Set article source and link
    const article_source = 'UnHook';
    const article_link = `https://unhook-production.up.railway.app/article/${articleId}`;
    
    await client.close();
    
    return {
      id: articleId,
      title: title || 'Article Not Found',
      content: content || '',
      category,
      time_to_read,
      article_link,
      article_source,
      external_id,
      youtube_channel,
      published_at,
      cached_at: new Date().toISOString()
    };
  } catch (error) {
    console.error('Error fetching article from MongoDB:', error);
    return null;
  }
}

export async function POST(request: Request, { params }: AddArticleParams) {
  try {
    const { id: articleId } = await params;
    
    if (!articleId) {
      return NextResponse.json(
        { error: 'Article ID is required' },
        { status: 400 }
      );
    }
    
    // Fetch article from MongoDB
    const article = await fetchArticleFromMongoDB(articleId);
    
    if (!article) {
      return NextResponse.json(
        { error: 'Article not found in database' },
        { status: 404 }
      );
    }
    
    // Cache the article
    cacheArticle(article);
    
    return NextResponse.json({
      success: true,
      message: `Article ${articleId} has been cached successfully`,
      article: {
        id: article.id,
        title: article.title,
        category: article.category,
        time_to_read: article.time_to_read,
        external_id: article.external_id,
        youtube_channel: article.youtube_channel,
        published_at: article.published_at,
        cached_at: article.cached_at
      }
    });
    
  } catch (error) {
    console.error('Error in addArticle endpoint:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(request: Request, { params }: AddArticleParams) {
  const { id: articleId } = await params;
  return POST(request, { params: Promise.resolve({ id: articleId }) });
}