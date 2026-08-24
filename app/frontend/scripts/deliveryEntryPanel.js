const recordPanel = document.getElementById('record-delivery-panel');
const entryPanel  = document.getElementById('entry-panel');
const closeBtn    = document.getElementById('entry-close');

export function renderDeliveryEntryPanel(){
  recordPanel.addEventListener('click', (event) => {
    const tile = event.target.closest('.tile');
    if (!tile || tile.classList.contains('tile--add')) return;

    openEntryPanel(tile.dataset.supplierId);
  });
}

closeBtn.addEventListener('click', closeEntryPanel);

function openEntryPanel(supplierId) {
  console.log('opening for supplier', supplierId);   // fill the panel here later

  recordPanel.hidden = true;
  entryPanel.hidden = false;
}

function closeEntryPanel() {
  entryPanel.hidden = true;
  recordPanel.hidden = false;
}