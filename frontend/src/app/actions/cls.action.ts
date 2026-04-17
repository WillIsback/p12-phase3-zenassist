'use server'
import { classifyComplaint, type ClassificationResult } from "@/services/ml_cls.service"
import { setClaimTag } from "@/database/queries"

let lastCallTime = 0;
const DEFAULT_MIN_INTERVAL_MS = 1000;

function getMinIntervalMs(): number {
  const rawValue = process.env.ML_AUTOTAG_MIN_INTERVAL_MS;
  if (!rawValue) return DEFAULT_MIN_INTERVAL_MS;

  const parsedValue = Number.parseInt(rawValue, 10);
  if (Number.isNaN(parsedValue) || parsedValue < 0) {
    console.warn('[mlAutoTag] invalid ML_AUTOTAG_MIN_INTERVAL_MS, fallback to default:', rawValue);
    return DEFAULT_MIN_INTERVAL_MS;
  }

  return parsedValue;
}

export async function mlAutoTag(claimId: number, complaint: string): Promise<ClassificationResult | null> {
  const minIntervalMs = getMinIntervalMs();
  const now = Date.now();
  if (now - lastCallTime < minIntervalMs) {
    console.log('[mlAutoTag] rate limited');
    return null;
  }
  lastCallTime = now;

  console.log('[mlAutoTag] called with claimId:', claimId, 'complaint length:', complaint.length);
  const result = await classifyComplaint(complaint)
  console.log('[mlAutoTag] classifyComplaint returned:', result);
  if (!result) return null;
  await setClaimTag(claimId, result.tag);
  console.log('[mlAutoTag] tag saved to DB');
  return result;
}