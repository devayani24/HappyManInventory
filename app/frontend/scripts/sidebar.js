const sidebar = document.querySelector('.sidebar');

export function renderSideBarPanel() {
  if (!sidebar) {
    console.error('Sidebar not found');
    return;
  }

  sidebar.addEventListener('click', (event) => {
    const navItem = event.target.closest('.nav');
    if (!navItem) return;

    showView(navItem.dataset.view);
  });
}

function showView(viewName) {
  const selectedView = document.querySelector(`.view[data-view="${viewName}"]`);
  if (!selectedView) {
    console.warn(`No view found for: ${viewName}`);
    return;                       // leave the current view alone
  }

  document.querySelectorAll('.view').forEach(view => {
    view.hidden = view !== selectedView;
  });

  document.querySelectorAll('.nav').forEach(nav => {
    const isActive = nav.dataset.view === viewName;
    nav.classList.toggle('is-active', isActive);
    if (isActive) nav.setAttribute('aria-current', 'page');
    else nav.removeAttribute('aria-current');
  });
}