#!/usr/bin/env node
/* 把 miniapp/data/schools.json 导入 SQLite，供 API 服务查询 */
const fs = require('node:fs');
const path = require('node:path');
const { DatabaseSync } = require('node:sqlite');

const ROOT = path.resolve(__dirname, '..');
const SRC = path.join(ROOT, 'miniapp', 'data', 'schools.json');
const DB_DIR = path.join(__dirname, 'data');
const DB_PATH = path.join(DB_DIR, 'kaoyan.db');

function main() {
  if (!fs.existsSync(SRC)) {
    console.error('找不到数据文件：', SRC);
    process.exit(1);
  }

  const raw = JSON.parse(fs.readFileSync(SRC, 'utf8'));
  const schools = raw.schools || [];
  fs.mkdirSync(DB_DIR, { recursive: true });

  const db = new DatabaseSync(DB_PATH);
  db.exec('PRAGMA journal_mode = WAL');
  db.exec('DROP TABLE IF EXISTS majors');
  db.exec('DROP TABLE IF EXISTS schools');
  db.exec('DROP TABLE IF EXISTS meta');
  db.exec(`
    CREATE TABLE schools (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      province TEXT,
      city TEXT,
      region TEXT,
      types TEXT NOT NULL,
      intro TEXT,
      payload TEXT NOT NULL
    )
  `);
  db.exec(`
    CREATE TABLE majors (
      id TEXT PRIMARY KEY,
      school_id TEXT NOT NULL,
      name TEXT NOT NULL,
      code TEXT,
      category TEXT,
      degree_type TEXT,
      study_mode TEXT,
      payload TEXT NOT NULL
    )
  `);
  db.exec('CREATE INDEX idx_majors_school ON majors(school_id)');
  db.exec('CREATE INDEX idx_majors_name ON majors(name)');
  db.exec('CREATE INDEX idx_schools_name ON schools(name)');
  db.exec('CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)');

  const insertSchool = db.prepare(`
    INSERT OR REPLACE INTO schools (id, name, province, city, region, types, intro, payload)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  const insertMajor = db.prepare(`
    INSERT OR REPLACE INTO majors (id, school_id, name, code, category, degree_type, study_mode, payload)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  const setMeta = db.prepare('INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)');

  let majorCount = 0;
  db.exec('BEGIN');
  try {
    for (const s of schools) {
      const schoolId = String(s.id || s.name);
      const { majors, ...schoolPayload } = s;
      insertSchool.run(
        schoolId,
        s.name,
        s.province || '',
        s.city || '',
        s.region || '',
        JSON.stringify(s.type || []),
        s.intro || '',
        JSON.stringify(schoolPayload)
      );
      for (const m of majors || []) {
        insertMajor.run(
          String(m.id || `${schoolId}_${m.code}`),
          schoolId,
          m.name,
          m.code || '',
          m.category || '',
          m.degreeType || '',
          m.studyMode || '',
          JSON.stringify(m)
        );
        majorCount += 1;
      }
    }

    const stat = fs.statSync(SRC);
    setMeta.run('imported_at', new Date().toISOString());
    setMeta.run('schools_count', String(schools.length));
    setMeta.run('majors_count', String(majorCount));
    setMeta.run('source_mtime', stat.mtime.toISOString());
    setMeta.run('source_file', SRC);
    db.exec('COMMIT');
  } catch (err) {
    db.exec('ROLLBACK');
    throw err;
  }

  console.log(`导入完成：${schools.length} 所学校，${majorCount} 个专业 -> ${DB_PATH}`);
  db.close();
}

main();
