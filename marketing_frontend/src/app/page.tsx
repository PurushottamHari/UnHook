import { redirect } from 'next/navigation';

export default function Home() {
  // Redirect to about page by default
  redirect('/about');
}
