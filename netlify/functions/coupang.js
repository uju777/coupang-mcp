const crypto = require('crypto');
const https = require('https');

const COUPANG_ACCESS_KEY = process.env.COUPANG_ACCESS_KEY;
const COUPANG_SECRET_KEY = process.env.COUPANG_SECRET_KEY;
const DOMAIN = 'api-gateway.coupang.com';

function generateHmac(method, urlPath, datetime) {
  const message = datetime + method + urlPath;
  return crypto.createHmac('sha256', COUPANG_SECRET_KEY).update(message).digest('hex');
}

function getAuthHeader(method, path, queryString = '') {
  const now = new Date();
  const datetime = now.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '').slice(2, 15) + 'Z';
  const urlPath = path + queryString;
  const signature = generateHmac(method, urlPath, datetime);
  return `CEA algorithm=HmacSHA256, access-key=${COUPANG_ACCESS_KEY}, signed-date=${datetime}, signature=${signature}`;
}

function makeRequest(method, path, queryString = '', body = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: DOMAIN,
      path: path + (queryString ? '?' + queryString : ''),
      method: method,
      headers: {
        'Authorization': getAuthHeader(method, path, queryString),
        'Content-Type': 'application/json;charset=UTF-8'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve({ error: 'Parse error', message: data });
        }
      });
    });

    req.on('error', (e) => resolve({ error: 'Request error', message: e.message }));

    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function searchProducts(keyword, limit = 10, sortType = 'SIM') {
  // sortType: SIM(관련성), SALE(판매량), LOW(낮은가격), HIGH(높은가격)
  const path = '/v2/providers/affiliate_open_api/apis/openapi/v1/products/search';
  const queryString = `keyword=${encodeURIComponent(keyword)}&limit=${Math.min(limit, 100)}&sortType=${sortType}`;
  return makeRequest('GET', path, queryString);
}

async function getBestProducts(categoryId, limit = 10) {
  const path = `/v2/providers/affiliate_open_api/apis/openapi/products/bestcategories/${categoryId}`;
  const queryString = `limit=${Math.min(limit, 100)}`;
  return makeRequest('GET', path, queryString);
}

async function getGoldbox(limit = 10) {
  const path = '/v2/providers/affiliate_open_api/apis/openapi/products/goldbox';
  const queryString = `limit=${Math.min(limit, 100)}`;
  return makeRequest('GET', path, queryString);
}

async function createDeeplink(url) {
  const path = '/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink';
  return makeRequest('POST', path, '', { coupangUrls: [url] });
}

exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  if (!COUPANG_ACCESS_KEY || !COUPANG_SECRET_KEY) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'API keys not configured' }) };
  }

  const params = event.queryStringParameters || {};
  const action = params.action || '';

  try {
    let result;

    switch (action) {
      case 'search':
        if (!params.keyword) {
          return { statusCode: 400, headers, body: JSON.stringify({ error: 'keyword required' }) };
        }
        // sortType: SIM(관련성), SALE(판매량/인기), LOW(낮은가격), HIGH(높은가격)
        result = await searchProducts(params.keyword, parseInt(params.limit) || 10, params.sort || 'SIM');
        break;

      case 'best':
        result = await getBestProducts(parseInt(params.category_id) || 1016, parseInt(params.limit) || 10);
        break;

      case 'goldbox':
        result = await getGoldbox(parseInt(params.limit) || 10);
        break;

      case 'deeplink':
        if (!params.url) {
          return { statusCode: 400, headers, body: JSON.stringify({ error: 'url required' }) };
        }
        result = await createDeeplink(params.url);
        break;

      default:
        return {
          statusCode: 400,
          headers,
          body: JSON.stringify({
            error: 'Invalid action',
            available_actions: ['search', 'best', 'goldbox', 'deeplink'],
            examples: {
              search: '?action=search&keyword=에어팟&limit=5&sort=SIM',
              search_low: '?action=search&keyword=에어팟&limit=5&sort=LOW',
              search_sale: '?action=search&keyword=에어팟&limit=5&sort=SALE',
              best: '?action=best&category_id=1016&limit=5',
              goldbox: '?action=goldbox&limit=5',
              deeplink: '?action=deeplink&url=https://www.coupang.com/...'
            },
            sort_options: ['SIM(관련성)', 'SALE(인기순)', 'LOW(낮은가격)', 'HIGH(높은가격)']
          })
        };
    }

    return { statusCode: 200, headers, body: JSON.stringify(result) };

  } catch (e) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: e.message }) };
  }
};
