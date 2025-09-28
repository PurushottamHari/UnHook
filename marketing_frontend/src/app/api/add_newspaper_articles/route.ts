import { NextResponse } from 'next/server';
import {
  cacheNewspaper,
  CachedNewspaper,
  CachedNewspaperArticle,
} from '@/lib/cache/newspaper-cache';
import { MongoClient } from 'mongodb';

async function fetchNewspaperFromMongoDB(
  date: string
): Promise<CachedNewspaper | null> {
  try {
    const client = new MongoClient(
      process.env.MONGODB_URI || 'mongodb://localhost:27017'
    );
    await client.connect();
    const db = client.db(process.env.DATABASE_NAME || 'youtube_newspaper');

    // Fetch from newspapers collection
    const newspapersCollection = db.collection('newspapers');

    // Convert date to epoch timestamp range (start and end of day) - matching scrappy frontend logic
    const dateObj = new Date(date);
    const startOfDay = new Date(
      dateObj.getFullYear(),
      dateObj.getMonth(),
      dateObj.getDate(),
      0,
      0,
      0
    );
    const endOfDay = new Date(
      dateObj.getFullYear(),
      dateObj.getMonth(),
      dateObj.getDate(),
      23,
      59,
      59
    );

    // Convert to epoch timestamps (seconds since epoch, as float)
    const startOfDayTimestamp = Math.floor(startOfDay.getTime() / 1000);
    const endOfDayTimestamp = Math.floor(endOfDay.getTime() / 1000);

    // Find newspaper for the specific date using created_at field (epoch timestamp)
    const newspaper = await newspapersCollection.findOne({
      created_at: {
        $gte: startOfDayTimestamp,
        $lte: endOfDayTimestamp,
      },
    });

    if (!newspaper) {
      console.log(`No newspaper found for date: ${date}`);
      console.log(
        `Searching for created_at between: ${startOfDayTimestamp} and ${endOfDayTimestamp}`
      );
      console.log(
        `Date range: ${startOfDay.toISOString()} to ${endOfDay.toISOString()}`
      );

      // Debug: Show what newspapers are available
      const allNewspapers = await newspapersCollection
        .find({})
        .limit(5)
        .toArray();
      console.log(
        'Available newspapers:',
        allNewspapers.map(n => ({
          id: n._id,
          created_at: n.created_at,
          createdDate: n.created_at
            ? new Date(n.created_at * 1000).toISOString().split('T')[0]
            : 'No created_at field',
        }))
      );

      await client.close();
      return null;
    }

    // Get the articles for this newspaper using the same logic as scrappy frontend
    const consideredContentList = newspaper.considered_content_list || [];

    // Extract user_collected_content_ids from considered_content_list
    const consideredContentIds = [];
    for (const item of consideredContentList) {
      if (item.user_collected_content_id) {
        consideredContentIds.push(item.user_collected_content_id);
      }
    }

    if (consideredContentIds.length === 0) {
      console.log('No considered content IDs found in newspaper');
      await client.close();
      return {
        date: date,
        topics: [],
        total_time_to_read: '0m read',
        articles: [],
        cached_at: new Date().toISOString(),
      };
    }

    // Get external_ids from the collected_content collection
    const collectedContentCollection = db.collection('collected_content');
    const externalIds = [];

    for (const contentId of consideredContentIds) {
      const collectedDoc = await collectedContentCollection.findOne({
        _id: contentId,
      });
      if (collectedDoc && collectedDoc.external_id) {
        externalIds.push(collectedDoc.external_id);
      }
    }

    if (externalIds.length === 0) {
      console.log('No external IDs found in collected content');
      await client.close();
      return {
        date: date,
        topics: [],
        total_time_to_read: '0m read',
        articles: [],
        cached_at: new Date().toISOString(),
      };
    }

    // Fetch the generated articles using external_ids
    const generatedContentCollection = db.collection('generated_content');
    const articles = await generatedContentCollection
      .find({
        status: 'ARTICLE_GENERATED',
        external_id: { $in: externalIds },
      })
      .toArray();

    // Transform articles to cached format using same logic as scrappy frontend
    const cachedArticles: CachedNewspaperArticle[] = articles.map(article => {
      // Get title from VERY_SHORT or SHORT content (same as scrappy frontend)
      let title = '';
      let summary = '';

      const generated = article.generated || {};

      // Try to get title from VERY_SHORT
      if (generated.VERY_SHORT && generated.VERY_SHORT.string) {
        title = generated.VERY_SHORT.string;
      }

      // Get summary from SHORT
      if (generated.SHORT && generated.SHORT.string) {
        summary = generated.SHORT.string;
      }

      // If no title from VERY_SHORT, try to extract from SHORT
      if (!title && summary) {
        const firstSentence = summary.split('.')[0];
        title =
          firstSentence.length > 50
            ? firstSentence.substring(0, 50) + '...'
            : firstSentence;
      }

      // Get category
      let category = 'Uncategorized';
      if (article.category && article.category.category) {
        category = article.category.category;
      }

      // Get reading time
      const readingTimeSeconds = article.reading_time_seconds || 0;
      const timeToRead =
        readingTimeSeconds > 0
          ? `${Math.ceil(readingTimeSeconds / 60)}m read`
          : '5 min read';

      return {
        id: article._id.toString(),
        title: title || 'Untitled Article',
        category: category,
        time_to_read: timeToRead,
        cached_at: new Date().toISOString(),
      };
    });

    // Calculate total time to read
    const totalMinutes = cachedArticles.reduce((total, article) => {
      const timeMatch = article.time_to_read.match(/(\d+)/);
      return total + (timeMatch ? parseInt(timeMatch[1]) : 5);
    }, 0);

    const totalTimeToRead =
      totalMinutes > 60
        ? `${Math.floor(totalMinutes / 60)}h ${totalMinutes % 60}m read`
        : `${totalMinutes}m read`;

    // Extract unique topics/categories
    const topics = [
      ...new Set(cachedArticles.map(article => article.category)),
    ];

    const cachedNewspaper: CachedNewspaper = {
      date: date,
      articles: cachedArticles,
      total_time_to_read: totalTimeToRead,
      topics: topics,
      cached_at: new Date().toISOString(),
    };

    await client.close();
    return cachedNewspaper;
  } catch (error) {
    console.error('Error fetching newspaper from MongoDB:', error);
    return null;
  }
}

export async function POST(request: Request) {
  try {
    const { date } = await request.json();

    if (!date) {
      return NextResponse.json({ error: 'Date is required' }, { status: 400 });
    }

    // Fetch newspaper from MongoDB
    const newspaper = await fetchNewspaperFromMongoDB(date);

    if (!newspaper) {
      return NextResponse.json(
        { error: `No newspaper found for date: ${date}` },
        { status: 404 }
      );
    }

    // Cache the newspaper
    cacheNewspaper(newspaper);

    return NextResponse.json({
      success: true,
      message: `Newspaper for ${date} has been cached successfully`,
      newspaper: {
        date: newspaper.date,
        articles_count: newspaper.articles.length,
        total_time_to_read: newspaper.total_time_to_read,
        topics: newspaper.topics,
        cached_at: newspaper.cached_at,
      },
    });
  } catch (error) {
    console.error('Error in add_newspaper_articles endpoint:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const date = searchParams.get('date');

    if (!date) {
      return NextResponse.json(
        { error: 'Date parameter is required' },
        { status: 400 }
      );
    }

    // Fetch newspaper from MongoDB
    const newspaper = await fetchNewspaperFromMongoDB(date);

    if (!newspaper) {
      return NextResponse.json(
        { error: `No newspaper found for date: ${date}` },
        { status: 404 }
      );
    }

    // Cache the newspaper
    cacheNewspaper(newspaper);

    return NextResponse.json({
      success: true,
      message: `Newspaper for ${date} has been cached successfully`,
      newspaper: {
        date: newspaper.date,
        articles_count: newspaper.articles.length,
        total_time_to_read: newspaper.total_time_to_read,
        topics: newspaper.topics,
        cached_at: newspaper.cached_at,
      },
    });
  } catch (error) {
    console.error('Error in add_newspaper_articles endpoint:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
