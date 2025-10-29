import { MongoClient } from 'mongodb';

let client: MongoClient | null = null;

export async function getMongoClient(): Promise<MongoClient> {
  if (!client) {
    const uri = process.env.MONGODB_URI || 'mongodb://localhost:27017';
    const dbName = process.env.DATABASE_NAME || 'youtube_newspaper';
    
    client = new MongoClient(uri);
    await client.connect();
  }
  
  return client;
}

export async function getDatabase() {
  const client = await getMongoClient();
  return client.db(process.env.DATABASE_NAME || 'youtube_newspaper');
}
