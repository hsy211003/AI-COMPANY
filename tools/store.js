/* ── SY COMPANY 공용 저장소 ─────────────────────────────────────
   사무실 시뮬레이터와 자료실 사이트가 같은 브라우저 저장소를 함께 쓴다.
   저장소를 쓸 수 없는 환경(사생활 보호 모드 등)에서는 메모리로만 동작하고,
   그 사실을 화면에 알린다. */
const STORE_KEY = "sy-company-v2";
const STORE_EMPTY = () => ({
  v: 2, savedAt: Date.now(),
  sim: null,                 // 시뮬레이터 진행 상태
  archive: [],               // 직원들이 쌓은 자료 (팀 > 직원 > 업무 제목)
  inbox: {},                 // 팀별 업무 지시(텍스트)와 파일
  naming: null,              // 네이밍팀이 학습한 구분자
  patterns: null             // 성과리뷰팀에 전달된 패턴 자료
});

let STORE_OK = true;
try {
  localStorage.setItem(STORE_KEY + "-probe", "1");
  localStorage.removeItem(STORE_KEY + "-probe");
} catch (e) { STORE_OK = false; }

let memStore = null;

function storeLoad(){
  if (!STORE_OK) return memStore || (memStore = STORE_EMPTY());
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (!raw) return STORE_EMPTY();
    const o = JSON.parse(raw);
    return (o && o.v === 2) ? o : STORE_EMPTY();
  } catch (e) { return STORE_EMPTY(); }
}

function storeSave(o){
  o.savedAt = Date.now();
  if (!STORE_OK){ memStore = o; return false; }
  try { localStorage.setItem(STORE_KEY, JSON.stringify(o)); return true; }
  catch (e) { return false; }          // 용량 초과 등
}

function storePatch(fn){
  const o = storeLoad();
  fn(o);
  storeSave(o);
  return o;
}

/* 다른 탭에서 바뀌면 알려준다 (같은 브라우저에서 두 페이지를 함께 열 때) */
function storeOnChange(fn){
  addEventListener("storage", e => { if (e.key === STORE_KEY) fn(storeLoad()); });
}

const fmtWhen = ms => {
  const d = new Date(ms), p = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
};
const fmtAgo = ms => {
  const s = Math.max(0, (Date.now() - ms) / 1000);
  if (s < 60) return "방금";
  if (s < 3600) return `${Math.floor(s/60)}분 전`;
  if (s < 86400) return `${Math.floor(s/3600)}시간 전`;
  return `${Math.floor(s/86400)}일 전`;
};

/* ── 엑셀(.xlsx) 최소 판독기 ────────────────────────────────────
   외부 라이브러리를 못 쓰는 환경이라, xlsx(=zip)를 직접 푼다.
   중앙 디렉터리를 읽어 필요한 XML 두 개만 꺼내 쓴다. */
async function readXlsx(file){
  const buf = new Uint8Array(await file.arrayBuffer());
  const dv = new DataView(buf.buffer);
  // End of Central Directory 찾기
  let eocd = -1;
  for (let i = buf.length - 22; i >= 0 && i > buf.length - 66000; i--){
    if (dv.getUint32(i, true) === 0x06054b50){ eocd = i; break; }
  }
  if (eocd < 0) throw new Error("엑셀 파일 형식이 아닙니다.");
  const count = dv.getUint16(eocd + 10, true);
  let ptr = dv.getUint32(eocd + 16, true);
  const files = {};
  for (let n = 0; n < count; n++){
    if (dv.getUint32(ptr, true) !== 0x02014b50) break;
    const method = dv.getUint16(ptr + 10, true);
    const csize = dv.getUint32(ptr + 20, true);
    const nameLen = dv.getUint16(ptr + 28, true);
    const extraLen = dv.getUint16(ptr + 30, true);
    const cmtLen = dv.getUint16(ptr + 32, true);
    const lho = dv.getUint32(ptr + 42, true);
    const name = new TextDecoder().decode(buf.subarray(ptr + 46, ptr + 46 + nameLen));
    files[name] = { method, csize, lho };
    ptr += 46 + nameLen + extraLen + cmtLen;
  }
  async function extract(name){
    const f = files[name];
    if (!f) return null;
    const ln = dv.getUint16(f.lho + 26, true), le = dv.getUint16(f.lho + 28, true);
    const start = f.lho + 30 + ln + le;
    const raw = buf.subarray(start, start + f.csize);
    if (f.method === 0) return new TextDecoder().decode(raw);
    const ds = new DecompressionStream("deflate-raw");
    const stream = new Blob([raw]).stream().pipeThrough(ds);
    return new TextDecoder().decode(new Uint8Array(await new Response(stream).arrayBuffer()));
  }
  const sharedXml = await extract("xl/sharedStrings.xml");
  const shared = [];
  if (sharedXml){
    const doc = new DOMParser().parseFromString(sharedXml, "application/xml");
    doc.querySelectorAll("si").forEach(si => {
      shared.push([...si.querySelectorAll("t")].map(t => t.textContent).join(""));
    });
  }
  let sheetName = Object.keys(files).find(n => /^xl\/worksheets\/sheet1\.xml$/.test(n))
               || Object.keys(files).find(n => /^xl\/worksheets\/.*\.xml$/.test(n));
  const sheetXml = sheetName ? await extract(sheetName) : null;
  if (!sheetXml) throw new Error("시트를 찾지 못했습니다.");
  const doc = new DOMParser().parseFromString(sheetXml, "application/xml");
  const rows = [];
  doc.querySelectorAll("row").forEach(r => {
    const cells = [];
    r.querySelectorAll("c").forEach(c => {
      const ref = (c.getAttribute("r") || "").replace(/[0-9]/g, "");
      let col = 0;
      for (const ch of ref) col = col * 26 + (ch.charCodeAt(0) - 64);
      col = Math.max(1, col) - 1;
      const t = c.getAttribute("t");
      let v = "";
      if (t === "inlineStr") v = c.querySelector("is t")?.textContent ?? "";
      else {
        const raw = c.querySelector("v")?.textContent ?? "";
        v = (t === "s") ? (shared[+raw] ?? "") : raw;
      }
      while (cells.length < col) cells.push("");
      cells[col] = v;
    });
    rows.push(cells);
  });
  return rows.filter(r => r.some(c => String(c).trim() !== ""));
}

/* CSV/TSV도 같은 모양으로 읽는다 */
async function readDelimited(file){
  const text = await file.text();
  const sep = text.includes("\t") ? "\t" : ",";
  return text.split(/\r?\n/).map(l => l.split(sep).map(c => c.replace(/^"|"$/g, "").trim()))
             .filter(r => r.some(c => c !== ""));
}

async function readTable(file){
  if (/\.xlsx$/i.test(file.name)) return readXlsx(file);
  if (/\.(csv|tsv|txt)$/i.test(file.name)) return readDelimited(file);
  throw new Error("xlsx · csv · tsv 파일만 읽을 수 있어요.");
}

/* ── 구분자 학습 ────────────────────────────────────────────────
   표에서 이름 열을 찾아, 토큰을 나누는 데 실제로 쓰인 구분 문자를 센다.
   가장 많이 쓰인 문자를 구분자로 삼고, 자리별 토큰 사전을 만든다. */
function learnNaming(rows){
  const CAND = ["_", "-", "|", "/", "·", ".", "+", "@", "#", "~", ":", ";"];
  const flat = rows.flat().map(v => String(v).trim()).filter(v => v.length > 3);
  const score = {};
  CAND.forEach(c => { score[c] = 0; });
  for (const v of flat){
    for (const c of CAND){
      const n = v.split(c).length - 1;
      if (n >= 2) score[c] += n;          // 2번 이상 나와야 구분자로 본다
    }
  }
  const sep = Object.keys(score).sort((a, b) => score[b] - score[a])[0];
  if (!sep || score[sep] === 0) return null;

  const samples = flat.filter(v => v.split(sep).length >= 3);
  if (!samples.length) return null;
  const width = Math.round(samples.reduce((s, v) => s + v.split(sep).length, 0) / samples.length);
  const slots = [];
  for (let i = 0; i < width; i++){
    const vals = [...new Set(samples.map(v => v.split(sep)[i]).filter(Boolean))];
    slots.push(vals.slice(0, 40));
  }
  return { sep, width, slots, samples: samples.slice(0, 5), learnedAt: Date.now() };
}

/* 학습한 규칙으로 이름을 만든다 */
function makeName(naming, seedParts){
  if (!naming) return null;
  const out = [];
  for (let i = 0; i < naming.width; i++){
    const given = seedParts && seedParts[i];
    const pool = naming.slots[i] || [];
    out.push(given || pool[Math.floor(Math.random() * pool.length)] || "");
  }
  return out.filter(Boolean).join(naming.sep);
}
