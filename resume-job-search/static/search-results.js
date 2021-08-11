const sidebarMenu = document.getElementById('sidebar-menu');
const activeListingInfo = document.getElementById('active-listing-info');
const instruction = document.getElementById('view-job-details-instruction');
const activeListingTitle = document.getElementById('active-listing-title');
const activeListingDesc = document.getElementById('active-listing-desc');
const activeListingUrl = document.getElementById('active-listing-url');

// Update active listing
function displayResult(element) {
  // Remove the active class from the previously-clicked item, and add it to the new one
  let currentActiveItem = sidebarMenu.querySelector('.active');
  if (currentActiveItem !== null) {
    currentActiveItem.classList.remove('active');
    currentActiveItem.getElementsByTagName('small')[0].classList.add('text-muted');
  } else {
    activeListingInfo.classList.remove('d-flex', 'flex-column', 'justify-content-center', 'align-items-center', 'bg-light');
    instruction.classList.remove('d-block');
    instruction.classList.add('d-none');
    activeListingTitle.classList.remove('d-none');
    activeListingTitle.classList.add('d-block');
    activeListingDesc.classList.remove('d-none');
    activeListingDesc.classList.add('d-block');
    activeListingUrl.classList.remove('d-none');
    activeListingUrl.classList.add('d-block');
  }
  element.classList.add('active');
  element.getElementsByTagName('small')[0].classList.remove('text-muted');

  // Update the information in the active-listing-info div
  let activeListingId = element.id;
  activeListingTitle.innerHTML = searchResults[activeListingId]['result id'];
  activeListingDesc.innerHTML = searchResults[activeListingId]['description'];
  activeListingUrl.innerHTML = searchResults[activeListingId]['url'];
}

// Reset page to its original state upon hitting ESC
window.addEventListener('keydown', function (event) {
  if (event.key === 'Escape') {
    let currentActiveItem = sidebarMenu.querySelector('.active');
    if (currentActiveItem !== null) {
      // Reset sidebar menu
      currentActiveItem.classList.remove('active');
      currentActiveItem.getElementsByTagName('small')[0].classList.add('text-muted');

      // Reset active-listing-info div
      activeListingInfo.classList.add('d-flex', 'flex-column', 'justify-content-center', 'align-items-center', 'bg-light');
      instruction.classList.remove('d-none');
      instruction.classList.add('d-block');
      activeListingTitle.classList.remove('d-block');
      activeListingTitle.classList.add('d-none');
      activeListingDesc.classList.remove('d-block');
      activeListingDesc.classList.add('d-none');
      activeListingUrl.classList.remove('d-block');
      activeListingUrl.classList.add('d-none');
      activeListingTitle.innerHTML = '';
      activeListingDesc.innerHTML = '';
      activeListingUrl.innerHTML = '';
    }
  }
});
