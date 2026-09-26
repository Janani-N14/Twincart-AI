/**
 * TwinCart-AI — centralised API service layer
 * All calls go through this module so the base URL is configured in one place.
 * Base URL is read from VITE_API_BASE_URL (default: http://localhost:8000)
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/* ─── helpers ───────────────────────────────────────────── */

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(`${BASE_URL}${path}`, opts);

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const err = await res.json();
      detail = err.detail || JSON.stringify(err);
    } catch (_) {}
    throw new Error(detail);
  }

  return res.json();
}

const get  = (path)       => request('GET',  path);
const post = (path, body) => request('POST', path, body);

/* ─── Health ────────────────────────────────────────────── */

export const healthCheck = () => get('/health');

/* ─── Digital Twins ─────────────────────────────────────── */

export const getRegionalTwins  = ()          => get('/api/twins/regions');
export const getRegionalTwin   = (regionId)  => get(`/api/twins/regions/${regionId}`);
export const getSegmentTwins   = ()          => get('/api/twins/segments');
export const getSegmentTwin    = (segmentId) => get(`/api/twins/segments/${segmentId}`);

/* ─── Campaign Generation ───────────────────────────────── */

/**
 * @param {string} regionId   - e.g. "TN-01"
 * @param {string|null} segmentId - e.g. "students" or null
 */
export const generateCampaign = (regionId, segmentId = null) =>
  post('/api/campaigns/generate', { region_id: regionId, segment_id: segmentId });

/**
 * @param {string[]} regionIds - up to 15 region IDs
 */
export const batchGenerateCampaigns = (regionIds) =>
  post('/api/campaigns/batch', regionIds);

/* ─── Simulation Engine ─────────────────────────────────── */

/**
 * @param {object} params
 * @param {string}  params.region_id
 * @param {boolean} params.festival_next_week
 * @param {number}  params.temperature_delta_c
 * @param {number}  params.budget_multiplier        (0.1 – 10.0)
 * @param {number}  params.inventory_shortfall_pct  (0.0 – 1.0)
 */
export const runSimulation = (params) => post('/api/simulation/run', params);

/* ─── Seller Intelligence ───────────────────────────────── */

/**
 * @param {string}      question
 * @param {string|null} regionId
 * @param {string|null} segmentId
 */
export const askSellerIntelligence = (question, regionId = null, segmentId = null) =>
  post('/api/sellers/ask', {
    question,
    region_id: regionId,
    segment_id: segmentId,
  });

/* ─── ML Training & Image Generation ───────────────────── */

export const getMlStatus       = ()       => get('/api/training/ml-status');
export const trainDemandModel  = (params) => post('/api/training/train-demand-forecast', params);
export const generatePoster    = (params) => post('/api/training/generate-poster', params);
