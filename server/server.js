#!/usr/bin/env node
/* 考研院校通 API 服务：零依赖，Node 内置 http + sqlite */
const http = require('node:http');
const zlib = require('node:zlib');
const fs = require('node:fs');
const path = require('node:path');
const { DatabaseSync } = require('node:sqlite');

const PORT = Number(process.env.PORT || 8010);
const DB_PATH = path.join(__dirname, 'data', 'kaoyan.db');
const CACHE_TTL = Number(process.env.CACHE_TTL || 30) * 1000;
const PROGRESS_FILE = path.join(__dirname, '..', 'data', 'collect_985.progress');
const PAGE_FILE = path.join(__dirname, 'progress.html');

if (!require('node:fs').existsSync(DB_PATH)) {
  console.error(`数据库不存在：${DB_PATH}`);
  console.error('请先运行：node server/import_data.js');
  process.exit(1);
}

const db = new DatabaseSync(DB_PATH);
const cache = new Map();

class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

function multiParam(p, name) {
  return p.getAll(name)
    .flatMap((v) => v.split(',').map((s) => s.trim()).filter(Boolean));
}

function intParam(p, name, def, min, max) {
  const raw = p.get(name);
  const n = raw === null ? def : Number(raw);
  if (!Number.isFinite(n)) return def;
  return Math.min(max, Math.max(min, Math.floor(n)));
}

function getMeta() {
  const rows = db.prepare('SELECT key, value FROM meta').all();
  const m = Object.fromEntries(rows.map((r) => [r.key, r.value]));
  const verified = db.prepare(`
    SELECT COUNT(*) AS c FROM majors
    WHERE json_array_length(payload, '$.admissionData') > 0
  `).get().c;
  return {
    dataVersion: m.source_mtime || m.imported_at || '',
    importedAt: m.imported_at || '',
    schoolsCount: Number(m.schools_count || 0),
    majorsCount: Number(m.majors_count || 0),
    verifiedCount: verified,
    dataStatus: verified > 0 ? 'verified-partial' : 'no-verified-data',
    notice: '当前未内置分数线数据；admissionData 为空，接入权威来源并补充 source/updatedAt 后才会展示'
  };
}

function rowToSchoolLight(r) {
  return {
    id: r.id,
    name: r.name,
    province: r.province,
    city: r.city,
    region: r.region,
    type: JSON.parse(r.types || '[]'),
    intro: (r.intro || '').slice(0, 120),
    majorsCount: r.majors_count
  };
}

function searchSchools(p) {
  const q = (p.get('q') || '').trim();
  const types = multiParam(p, 'type');
  const regions = multiParam(p, 'region');
  const provinces = multiParam(p, 'province');
  const page = intParam(p, 'page', 1, 1, 100000);
  const pageSize = intParam(p, 'pageSize', 20, 1, 100);

  const where = [];
  const params = [];
  if (q) {
    where.push('(s.name LIKE ? OR s.province LIKE ? OR s.city LIKE ?)');
    const like = `%${q}%`;
    params.push(like, like, like);
  }
  if (types.length) {
    where.push(`EXISTS (SELECT 1 FROM json_each(s.types) je WHERE je.value IN (${types.map(() => '?').join(',')}))`);
    params.push(...types);
  }
  if (regions.length) {
    where.push(`s.region IN (${regions.map(() => '?').join(',')})`);
    params.push(...regions);
  }
  if (provinces.length) {
    where.push(`s.province IN (${provinces.map(() => '?').join(',')})`);
    params.push(...provinces);
  }

  const whereSql = where.length ? `WHERE ${where.join(' AND ')}` : '';
  const total = db.prepare(`SELECT COUNT(*) AS c FROM schools s ${whereSql}`).get(...params).c;
  const rows = db.prepare(`
    SELECT s.id, s.name, s.province, s.city, s.region, s.types, s.intro,
      (SELECT COUNT(*) FROM majors m WHERE m.school_id = s.id) AS majors_count
    FROM schools s ${whereSql}
    ORDER BY s.name
    LIMIT ? OFFSET ?
  `).all(...params, pageSize, (page - 1) * pageSize);

  return {
    items: rows.map(rowToSchoolLight),
    total,
    page,
    pageSize,
    hasMore: page * pageSize < total
  };
}

function getHotSchools(p) {
  const limit = intParam(p, 'limit', 6, 1, 50);
  const rows = db.prepare(`
    SELECT s.id, s.name, s.province, s.city, s.region, s.types, s.intro,
      (SELECT COUNT(*) FROM majors m WHERE m.school_id = s.id) AS majors_count
    FROM schools s
    ORDER BY s.name
    LIMIT ?
  `).all(limit);
  return { items: rows.map(rowToSchoolLight) };
}

function getSchoolById(id) {
  const s = db.prepare('SELECT * FROM schools WHERE id = ?').get(id);
  if (!s) throw new HttpError(404, '学校不存在');
  const majors = db.prepare('SELECT payload FROM majors WHERE school_id = ? ORDER BY name').all(id)
    .map((r) => JSON.parse(r.payload));
  const school = JSON.parse(s.payload);
  school.majors = majors;
  school.majorsCount = majors.length;
  school.type = JSON.parse(s.types);
  return school;
}

function searchMajors(p) {
  const q = (p.get('q') || '').trim();
  const schoolId = (p.get('schoolId') || '').trim();
  const page = intParam(p, 'page', 1, 1, 100000);
  const pageSize = intParam(p, 'pageSize', 20, 1, 100);

  const where = [];
  const params = [];
  if (q) {
    where.push('(m.name LIKE ? OR m.code LIKE ? OR m.category LIKE ?)');
    const like = `%${q}%`;
    params.push(like, like, like);
  }
  if (schoolId) {
    where.push('m.school_id = ?');
    params.push(schoolId);
  }
  const whereSql = where.length ? `WHERE ${where.join(' AND ')}` : '';
  const total = db.prepare(`SELECT COUNT(*) AS c FROM majors m ${whereSql}`).get(...params).c;
  const rows = db.prepare(`
    SELECT m.*, s.name AS school_name, s.province AS school_province, s.city AS school_city
    FROM majors m
    JOIN schools s ON s.id = m.school_id
    ${whereSql}
    ORDER BY s.name, m.name
    LIMIT ? OFFSET ?
  `).all(...params, pageSize, (page - 1) * pageSize);

  const items = rows.map((r) => ({
    ...JSON.parse(r.payload),
    schoolId: r.school_id,
    schoolName: r.school_name,
    schoolProvince: r.school_province,
    schoolCity: r.school_city
  }));
  return { items, total, page, pageSize, hasMore: page * pageSize < total };
}

function getMajorById(schoolId, majorId) {
  const m = db.prepare('SELECT payload FROM majors WHERE id = ? AND school_id = ?').get(majorId, schoolId);
  if (!m) throw new HttpError(404, '专业不存在');
  const s = db.prepare('SELECT id, name, province, city, region, types FROM schools WHERE id = ?').get(schoolId);
  return {
    major: JSON.parse(m.payload),
    school: {
      id: s.id,
      name: s.name,
      province: s.province,
      city: s.city,
      region: s.region,
      type: JSON.parse(s.types)
    }
  };
}

function getFilters() {
  const types = db.prepare(`
    SELECT je.value AS label, COUNT(*) AS count
    FROM schools s, json_each(s.types) je
    GROUP BY je.value
    ORDER BY count DESC
  `).all();
  const regions = db.prepare(`
    SELECT region AS label, COUNT(*) AS count
    FROM schools
    WHERE region <> ''
    GROUP BY region
    ORDER BY count DESC
  `).all();
  const provinces = db.prepare(`
    SELECT province AS name, COUNT(*) AS count
    FROM schools
    WHERE province <> ''
    GROUP BY province
    ORDER BY count DESC
  `).all();
  const meta = getMeta();
  return {
    types,
    regions,
    provinces,
    totalSchools: meta.schoolsCount,
    totalMajors: meta.majorsCount
  };
}

function sendJson(res, status, code, message, data, meta, cached) {
  const payload = JSON.stringify({ code, message, data, meta });
  const headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'X-Cache': cached ? 'HIT' : 'MISS'
  };
  if (!cached) {
    headers['Cache-Control'] = `public, max-age=${Math.round(CACHE_TTL / 1000)}`;
  }
  const body = Buffer.from(payload, 'utf8');
  const accept = res.req ? res.req.headers['accept-encoding'] || '' : '';
  if (accept.includes('gzip')) {
    headers['Content-Encoding'] = 'gzip';
    res.writeHead(status, headers);
    res.end(zlib.gzipSync(body));
  } else {
    headers['Content-Length'] = body.length;
    res.writeHead(status, headers);
    res.end(body);
  }
}

function sendProgress(res) {
  let data = {
    running: false,
    done: 0,
    total: 0,
    processed: 0,
    percent: 0,
    school: '',
    programs: 0,
    skipped: [],
    failed: [],
    elapsedSec: 0,
    error: null
  };
  try {
    if (fs.existsSync(PROGRESS_FILE)) {
      data = { ...data, ...JSON.parse(fs.readFileSync(PROGRESS_FILE, 'utf8')) };
    }
  } catch (err) {
    data.error = err.message;
  }
  const payload = JSON.stringify({ code: 0, message: 'ok', data });
  const headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    'Access-Control-Allow-Origin': '*'
  };
  const body = Buffer.from(payload, 'utf8');
  headers['Content-Length'] = body.length;
  res.writeHead(200, headers);
  res.end(body);
}

function servePage(res) {
  if (!fs.existsSync(PAGE_FILE)) {
    sendJson(res, 404, 40400, 'progress page not found', null, null, false);
    return;
  }
  const body = fs.readFileSync(PAGE_FILE);
  res.writeHead(200, {
    'Content-Type': 'text/html; charset=utf-8',
    'Cache-Control': 'no-store'
  });
  res.end(body);
}

function respond(req, res, handler) {
  const key = req.url;
  const hit = cache.get(key);
  if (hit && Date.now() < hit.expires) {
    sendJson(res, 200, 0, 'ok', hit.data, hit.meta, true);
    return;
  }
  try {
    const data = handler();
    const meta = { serverTime: Date.now(), ...getMeta() };
    cache.set(key, { expires: Date.now() + CACHE_TTL, data, meta });
    sendJson(res, 200, 0, 'ok', data, meta, false);
  } catch (err) {
    const status = err.status || 500;
    sendJson(res, status, status * 100, err.message || '服务器错误', null, null, false);
  }
}

function handle(req, res) {
  res.req = req;
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  const pathname = url.pathname.replace(/\/+$/, '') || '/';

  if (req.method === 'OPTIONS') {
    res.writeHead(204, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
    return;
  }
  if (req.method !== 'GET') {
    sendJson(res, 405, 40500, 'Method Not Allowed', null, null, false);
    return;
  }

  const p = url.searchParams;
  let m;
  if (pathname === '/api/collect/progress') return sendProgress(res);
  if (pathname === '/progress' || pathname === '/progress.html') return servePage(res);
  if (pathname === '/api/health') return respond(req, res, () => ({ status: 'ok', service: 'kaoyan-api', uptime: Math.round(process.uptime()), port: PORT }));
  if (pathname === '/api/meta') return respond(req, res, () => getMeta());
  if (pathname === '/api/filters') return respond(req, res, () => getFilters());
  if (pathname === '/api/schools/search') return respond(req, res, () => searchSchools(p));
  if (pathname === '/api/schools/hot') return respond(req, res, () => getHotSchools(p));
  if ((m = pathname.match(/^\/api\/schools\/([^/]+)$/))) return respond(req, res, () => getSchoolById(decodeURIComponent(m[1])));
  if (pathname === '/api/majors/search') return respond(req, res, () => searchMajors(p));
  if ((m = pathname.match(/^\/api\/majors\/([^/]+)\/([^/]+)$/))) {
    return respond(req, res, () => getMajorById(decodeURIComponent(m[1]), decodeURIComponent(m[2])));
  }
  return sendJson(res, 404, 40400, 'Not Found', null, null, false);
}

const server = http.createServer(handle);
server.listen(PORT, '0.0.0.0', () => {
  console.log(`kaoyan-api listening on http://127.0.0.1:${PORT}`);
  console.log(`data: ${DB_PATH}`);
});
