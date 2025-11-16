/**
 * Share utility functions
 * Handles sharing to various platforms and copy-to-clipboard functionality
 */

export interface ShareData {
  url: string;
  title: string;
  text?: string;
}

/**
 * Check if Web Share API is available (mobile browsers)
 */
export function isWebShareAvailable(): boolean {
  return typeof navigator !== 'undefined' && 'share' in navigator;
}

/**
 * Use native Web Share API (mobile)
 */
export async function shareViaWebAPI(data: ShareData): Promise<boolean> {
  if (!isWebShareAvailable()) {
    return false;
  }

  try {
    await navigator.share({
      title: data.title,
      text: data.text || `Check out this article: ${data.title}`,
      url: data.url,
    });
    return true;
  } catch (error) {
    // User cancelled or error occurred
    if ((error as Error).name === 'AbortError') {
      return false; // User cancelled, not an error
    }
    console.error('Error sharing via Web API:', error);
    return false;
  }
}

/**
 * Share to Twitter/X
 */
export function shareToTwitter(data: ShareData): void {
  const text = encodeURIComponent(data.text || data.title);
  const url = encodeURIComponent(data.url);
  const twitterUrl = `https://twitter.com/intent/tweet?text=${text}&url=${url}`;
  window.open(twitterUrl, '_blank', 'width=550,height=420');
}

/**
 * Share to Facebook
 */
export function shareToFacebook(data: ShareData): void {
  const url = encodeURIComponent(data.url);
  const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
  window.open(facebookUrl, '_blank', 'width=550,height=420');
}

/**
 * Share to LinkedIn
 */
export function shareToLinkedIn(data: ShareData): void {
  const url = encodeURIComponent(data.url);
  const title = encodeURIComponent(data.title);
  const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}&title=${title}`;
  window.open(linkedInUrl, '_blank', 'width=550,height=420');
}

/**
 * Share to WhatsApp
 * Detects if on mobile to use WhatsApp protocol or web version
 */
export function shareToWhatsApp(data: ShareData): void {
  const text = encodeURIComponent(
    `${data.text || data.title}\n\n${data.url}`
  );
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  
  if (isMobile) {
    // Use WhatsApp protocol for mobile
    window.location.href = `whatsapp://send?text=${text}`;
  } else {
    // Use web version for desktop
    const whatsappUrl = `https://web.whatsapp.com/send?text=${text}`;
    window.open(whatsappUrl, '_blank');
  }
}

/**
 * Share to Instagram
 * Note: Instagram doesn't have a direct web share URL, so we use the Instagram app protocol on mobile
 * or guide users to share via Instagram Stories/DM manually
 */
export function shareToInstagram(data: ShareData): void {
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  const text = encodeURIComponent(
    `${data.text || data.title}\n\n${data.url}`
  );
  
  if (isMobile) {
    // Try to open Instagram app (may not work if app not installed)
    // Instagram doesn't support direct URL sharing, so we'll use a workaround
    // For iOS, we can try instagram://share?text=...
    // For Android, we can try intent://...
    const userAgent = navigator.userAgent;
    if (/iPhone|iPad|iPod/i.test(userAgent)) {
      // iOS - try Instagram app
      window.location.href = `instagram://share?text=${text}`;
    } else {
      // Android - try Instagram intent
      window.location.href = `intent://share?text=${text}#Intent;package=com.instagram.android;scheme=https;end`;
    }
  } else {
    // Desktop - open Instagram web in new tab
    // Since Instagram web doesn't support direct sharing, we'll open the main page
    // Users can manually share from there
    window.open('https://www.instagram.com', '_blank');
  }
}

/**
 * Share via Email
 */
export function shareViaEmail(data: ShareData): void {
  const subject = encodeURIComponent(data.title);
  const body = encodeURIComponent(
    `${data.text || `Check out this article: ${data.title}`}\n\n${data.url}`
  );
  const emailUrl = `mailto:?subject=${subject}&body=${body}`;
  window.location.href = emailUrl;
}

/**
 * Copy link to clipboard
 */
export async function copyToClipboard(url: string): Promise<boolean> {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(url);
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = url;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.select();
      const success = document.execCommand('copy');
      document.body.removeChild(textArea);
      return success;
    }
  } catch (error) {
    console.error('Failed to copy to clipboard:', error);
    return false;
  }
}

/**
 * Get share URL for a platform
 */
export function getShareUrl(platform: string, data: ShareData): string {
  const encodedUrl = encodeURIComponent(data.url);
  const encodedTitle = encodeURIComponent(data.title);
  const encodedText = encodeURIComponent(data.text || data.title);

  switch (platform) {
    case 'twitter':
      return `https://twitter.com/intent/tweet?text=${encodedText}&url=${encodedUrl}`;
    case 'facebook':
      return `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`;
    case 'linkedin':
      return `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}&title=${encodedTitle}`;
    case 'whatsapp':
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
      const whatsappText = encodeURIComponent(
        `${data.text || data.title}\n\n${data.url}`
      );
      return isMobile
        ? `whatsapp://send?text=${whatsappText}`
        : `https://web.whatsapp.com/send?text=${whatsappText}`;
    case 'email':
      const emailBody = encodeURIComponent(
        `${data.text || `Check out this article: ${data.title}`}\n\n${data.url}`
      );
      return `mailto:?subject=${encodedTitle}&body=${emailBody}`;
    default:
      return data.url;
  }
}

