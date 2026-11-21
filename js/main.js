import { loadDataset, getColumnNames, getDatasetMetadata } from './data.js';

function initializeNavigation() {
  const button = document.querySelector('.menu-toggle');
  const navigation = document.querySelector('#navigation');
  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') !== 'true';
    button.setAttribute('aria-expanded', String(open));
    navigation.classList.toggle('is-open', open);
  });
  navigation.addEventListener('click', event => {
    if (event.target.closest('a')) {
      button.setAttribute('aria-expanded', 'false');
      navigation.classList.remove('is-open');
    }
  });
}
function renderPreview(records, columns) {
  const table = document.querySelector('#data-table');
  const headerRow = document.createElement('tr');
  columns.forEach(column => {
    const cell = document.createElement('th');
    cell.scope = 'col';
    cell.textContent = column;
    headerRow.append(cell);
  });
  table.tHead.replaceChildren(headerRow);
  const rows = records.slice(0, 10).map(record => {
    const row = document.createElement('tr');
    columns.forEach(column => {
      const cell = document.createElement('td');
      cell.textContent = record[column] === null ? '—' : String(record[column]);
      if (record[column] === null) cell.setAttribute('aria-label', 'Valor ausente');
      row.append(cell);
    });
    return row;
  });
  table.tBodies[0].replaceChildren(...rows);
  table.hidden = false;
}
async function initialize() {
  initializeNavigation();
  try {
    const records = await loadDataset();
    const metadata = getDatasetMetadata();
    document.querySelector('#record-count').textContent = metadata.recordCount;
    document.querySelector('#grade-count').textContent = metadata.gradeCount;
    document.querySelector('#property-count').textContent = metadata.mechanicalPropertyCount;
    document.querySelector('#dataset-status').textContent = 'Datos cargados correctamente.';
    renderPreview(records, getColumnNames());
    document.querySelector('#table-status').textContent = records.length ? '' : 'El archivo no contiene registros.';
  } catch (error) {
    const message = `No fue posible cargar los datos. ${error.message} Comprueba que data/steels.csv exista y que el sitio se abra mediante un servidor HTTP.`;
    for (const id of ['dataset-status', 'table-status']) {
      const element = document.getElementById(id);
      element.textContent = message;
      element.classList.add('error');
    }
  }
}
initialize();
