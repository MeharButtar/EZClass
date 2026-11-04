// Home: a landing page only. The header and footer come from nav.js; the
// animated week comes from hero.js.

import "../nav.js";
import { CONFIG } from "../config.js";
import { initHero } from "../hero.js";
import { $ } from "../ui.js";

// The first version was one page with #search and #ge views. Send old links
// and bookmarks to the pages that replaced them.
const OLD_VIEWS = { "#search": "search.html", "#ge": "ge.html" };
if (OLD_VIEWS[location.hash]) {
  document.documentElement.dataset.leaving = "1";   // track.js skips the page view
  location.replace(OLD_VIEWS[location.hash]);
}

$("#hero-lead").textContent = `Pick your major and see every class it requires, with the ${CONFIG.termName} sections ready to add.`;
$("#cta-text").textContent = `Ready to plan ${CONFIG.termName}?`;
initHero($("#hero-art"), $("#hero-status"), $("#hero-replay"));
