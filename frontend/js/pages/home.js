// Home: a landing page only. The header and footer come from nav.js; the
// animated week comes from hero.js.

import "../nav.js";
import { CONFIG } from "../config.js";
import { initHero } from "../hero.js";
import { $ } from "../ui.js";

$("#hero-lead").textContent = `Pick your major and see every class it requires, with the ${CONFIG.termName} sections ready to add.`;
$("#cta-text").textContent = `Ready to plan ${CONFIG.termName}?`;
initHero($("#hero-art"), $("#hero-status"), $("#hero-replay"));
