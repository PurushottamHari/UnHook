import { MongoClient } from 'mongodb';

let client: MongoClient | null = null;

export async function getMongoClient(): Promise<MongoClient> {
  if (!client) {
    const uri = process.env.MONGODB_URI;
    
    if (!uri) {
      throw new Error('MONGODB_URI environment variable is required');
    }
    
    client = new MongoClient(uri);
    await client.connect();
  }
  
  return client;
}

export async function getDatabase() {
  const databaseName = process.env.DATABASE_NAME;
  
  if (!databaseName) {
    throw new Error('DATABASE_NAME environment variable is required');
  }
  
  const client = await getMongoClient();
  return client.db(databaseName);
}
