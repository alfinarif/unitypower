(() => {
  document.documentElement.classList.add("has-page-loader");

  const loader = () => document.getElementById("load_screen");

  const hideLoader = () => {
    const element = loader();
    if (!element) return;

    element.classList.add("is-hidden");
    element.setAttribute("aria-hidden", "true");
  };

  const showLoader = (message) => {
    const element = loader();
    if (!element) return;

    const messageElement = element.querySelector("[data-loader-message]");
    if (messageElement && message) messageElement.textContent = message;

    element.classList.remove("is-hidden");
    element.classList.add("is-visible");
    element.setAttribute("aria-hidden", "false");
  };

  window.addEventListener("load", hideLoader);
  window.addEventListener("pageshow", (event) => {
    if (event.persisted) hideLoader();
  });

  document.addEventListener("submit", (event) => {
    const form = event.target;
    if (event.defaultPrevented) return;
    if (!(form instanceof HTMLFormElement) || form.hasAttribute("data-no-page-loader")) return;
    if (form.method.toLowerCase() === "dialog") return;

    const submitter = event.submitter;
    const target = (submitter && submitter.getAttribute("formtarget")) || form.target;
    if (target && target.toLowerCase() !== "_self") return;

    const action = new URL(form.action, window.location.href);
    if (action.origin !== window.location.origin || action.pathname.includes("/export/")) return;

    const element = loader();
    if (element) showLoader(element.getAttribute("data-loader-submitting"));
  });

  document.addEventListener("click", (event) => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (!(event.target instanceof Element)) return;

    const link = event.target.closest("a[href]");
    if (!link || link.hasAttribute("download") || link.hasAttribute("data-no-page-loader")) return;
    if (link.target && link.target.toLowerCase() !== "_self") return;
    if (link.closest(".btn-download")) return;

    const destination = new URL(link.href, window.location.href);
    if (destination.origin !== window.location.origin) return;
    if (destination.pathname.includes("/export/") || destination.pathname.endsWith("/pdf/")) return;
    if (destination.pathname === window.location.pathname
      && destination.search === window.location.search
      && destination.hash) return;

    const element = loader();
    if (element) showLoader(element.getAttribute("data-loader-loading"));
  });
})();
