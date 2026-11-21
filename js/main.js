import { loadDataset, getColumnNames, getDatasetMetadata } from './data.js';
import { initializeCarbonChart } from './charts-point2.js';
import { initializeProcessingChart } from './charts-processing.js';
import { initializePoint3 } from './charts-point3.js';
import { initializeTables } from './tables.js';
import { loadVerifiedInference, initializeInference } from './inference.js';
import { initializeMeanInference } from './charts-anova.js';

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
async function initialize() {
  initializeNavigation();
  try {
    const records = await loadDataset();
    const metadata = getDatasetMetadata();
    document.querySelector('#record-count').textContent = metadata.recordCount;
    document.querySelector('#grade-count').textContent = metadata.gradeCount;
    document.querySelector('#property-count').textContent = metadata.mechanicalPropertyCount;
    document.querySelector('#dataset-status').textContent = 'Datos cargados correctamente.';
    initializeCarbonChart(records);
    initializeProcessingChart(records);
    initializePoint3(records);
    const inference = await loadVerifiedInference();
    initializeInference(inference);
    await initializeMeanInference(inference);
    await initializeTables(records, getColumnNames(), inference);
  } catch (error) {
    document.querySelector('#chart-scope').textContent = 'No se pudo cargar la visualización.';
    document.querySelector('#processing-scope').textContent = 'No se pudo cargar la comparación.';
    document.querySelector('#p3-population').textContent = 'No se pudo cargar la población analítica.';
    const message = `No fue posible cargar los datos. ${error.message} Comprueba que data/steels.csv exista y que el sitio se abra mediante un servidor HTTP.`;
    for (const id of ['dataset-status', 'tables-explorer']) {
      const element = document.getElementById(id);
      element.textContent = message;
      element.classList.add('error');
    }
  }
}
initialize();
