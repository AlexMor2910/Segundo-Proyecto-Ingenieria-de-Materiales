// Columns are selected by their original CSV headers; SAE Grade remains an identifier.
const NUMERIC_COLUMNS = new Set(['UTS (MPa)', 'YS (MPa)', 'Elongation (%)', 'Reduction (%)', 'Hardness (HB)', 'P (Max)', 'S(Max)', 'Mn Avg (%)', 'C (%)', 'Temperature (K)']);
const MECHANICAL_PROPERTIES = ['UTS (MPa)', 'YS (MPa)', 'Elongation (%)', 'Reduction (%)', 'Hardness (HB)'];
let records = [];
let columns = [];

// Parse RFC-style CSV fields, including quoted commas, escaped quotes and line breaks.
export function parseCSV(text) {
  const rows = [];
  let row = [], field = '', quoted = false, afterQuote = false;
  text = text.replace(/^\uFEFF/, '');
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') { field += '"'; i++; }
      else if (char === '"') { quoted = false; afterQuote = true; }
      else field += char;
    } else if (char === ',' ) { row.push(field); field = ''; afterQuote = false; }
    else if (char === '\n' || char === '\r') {
      if (char === '\r' && text[i + 1] === '\n') i++;
      row.push(field); rows.push(row); row = []; field = ''; afterQuote = false;
    } else if (char === '"' && field === '' && !afterQuote) quoted = true;
    else if (afterQuote) throw new Error('Formato CSV inválido después de una comilla de cierre.');
    else if (char === '"') throw new Error('Comilla inesperada en el archivo CSV.');
    else field += char;
  }
  if (quoted) throw new Error('El archivo CSV contiene un campo entre comillas sin cerrar.');
  if (field !== '' || row.length || afterQuote) { row.push(field); rows.push(row); }
  return rows;
}

export async function loadDataset() {
  // Resolve from this module so the path also works in a GitHub Pages subdirectory.
  const response = await fetch(new URL('../data/steels.csv', import.meta.url));
  if (!response.ok) throw new Error(`No se pudo cargar el archivo CSV (HTTP ${response.status}).`);
  const text = await response.text();
  if (!text.trim()) throw new Error('El archivo CSV está vacío.');
  const rows = parseCSV(text);
  const headers = rows.shift();
  if (!headers || !headers.length || headers.some(header => !header.trim()) || new Set(headers).size !== headers.length) throw new Error('El archivo CSV contiene encabezados vacíos o duplicados.');
  if (!headers.includes('SAE Grade')) throw new Error('El archivo CSV no contiene la columna SAE Grade.');
  const parsed = rows.map((row, index) => {
    if (row.length !== headers.length) throw new Error(`La fila ${index + 2} no coincide con el número de columnas.`);
    return Object.fromEntries(headers.map((header, i) => {
      const value = row[i];
      if (value.trim() === '') return [header, null];
      if (NUMERIC_COLUMNS.has(header)) {
        const number = Number(value);
        if (!Number.isFinite(number)) throw new Error(`Valor numérico inválido en la fila ${index + 2}, columna ${header}.`);
        return [header, number];
      }
      return [header, value];
    }));
  });
  columns = headers;
  records = parsed;
  return getRecords();
}
export function getRecords() { return records.slice(); }
export function getColumnNames() { return columns.slice(); }
export function getDistinctSAEGrades() { return [...new Set(records.map(record => record['SAE Grade']).filter(value => value !== null))]; }
export function getDatasetMetadata() { return { recordCount: records.length, gradeCount: getDistinctSAEGrades().length, mechanicalPropertyCount: MECHANICAL_PROPERTIES.filter(name => columns.includes(name)).length, columnCount: columns.length }; }
