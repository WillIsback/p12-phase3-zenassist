import { ALLOWED_TAGS } from '@/constants/tags';
type AllowedTag = typeof ALLOWED_TAGS[number];

interface BackendTagResponse {
  tag: string;
  confidence: number | null;
}

export interface ClassificationResult {
  tag: AllowedTag;
  confidence: number | null;
}

const env = (globalThis as { process?: { env?: Record<string, string | undefined> } }).process?.env;
const ML_BACKEND_BASE_URL = env?.ML_BACKEND_BASE_URL || 'http://127.0.0.1:8000';

function isAllowedTag(value: string): value is AllowedTag {
  return ALLOWED_TAGS.includes(value as AllowedTag);
}

export async function classifyComplaint(complaintText: string): Promise<ClassificationResult | null> {
  const trimmedComplaint = complaintText.trim();
  if (!trimmedComplaint) {
    console.warn('[classifyComplaint] empty complaint text received');
    return null;
  }

  try {
    const response = await fetch(`${ML_BACKEND_BASE_URL}/tag`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_claim: trimmedComplaint }),
      cache: 'no-store',
    });

    if (!response.ok) {
      const errorBody = await response.text();
      console.error('[classifyComplaint] backend classification failed', {
        status: response.status,
        body: errorBody,
      });
      return null;
    }

    const payload = await response.json() as BackendTagResponse;
    if (!isAllowedTag(payload.tag)) {
      console.error('[classifyComplaint] backend returned unknown tag:', payload.tag);
      return null;
    }

    return {
      tag: payload.tag,
      confidence: typeof payload.confidence === 'number' ? payload.confidence : null,
    };
  } catch (error) {
    console.error('[classifyComplaint] unable to reach backend ML API:', error);
    return null;
  }
}