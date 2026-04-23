function setActiveTab(tabButtons, tabPanels, targetId) {
  for (const button of tabButtons) {
    const isActive = button.dataset.tabTarget === targetId;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-selected", String(isActive));
  }

  for (const panel of tabPanels) {
    panel.classList.toggle("is-active", panel.id === targetId);
  }

  document.dispatchEvent(
    new CustomEvent("layout:tabchange", {
      detail: { targetId },
    })
  );
}

document.addEventListener("DOMContentLoaded", () => {
  const tabShells = document.querySelectorAll(".tab-shell");
  for (const shell of tabShells) {
    const tabButtons = shell.querySelectorAll(".page-tab[data-tab-target]");
    const tabPanels = shell.querySelectorAll("[data-tab-panel]");
    if (!tabButtons.length || !tabPanels.length) {
      continue;
    }

    const defaultTarget = shell.querySelector(".page-tab.is-active")?.dataset.tabTarget || tabButtons[0].dataset.tabTarget;
    setActiveTab(tabButtons, tabPanels, defaultTarget);

    for (const button of tabButtons) {
      button.addEventListener("click", () => {
        const targetId = button.dataset.tabTarget;
        if (targetId) {
          setActiveTab(tabButtons, tabPanels, targetId);
        }
      });
    }
  }
});