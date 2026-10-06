import { warm } from "./api";
import { ATTRIBUTION } from "./copy";
import { loadDemo, state, type Go } from "./state";
import { renderStart, bindStart } from "./views/start";
import { renderToday, bindToday } from "./views/today";
import { renderCourt } from "./views/court";
import { renderAway, bindAway } from "./views/away";
import { renderCheckin, bindCheckin } from "./views/checkin";
import { renderHood, bindHood } from "./views/hood";

const app = document.getElementById("app")!;

const go: Go = (route) => { location.hash = route; };
const footer = () => `<footer class="foot"><a href="#/hood">Under the hood</a><span>${ATTRIBUTION}</span></footer>`;

function draw(): void {
  const route = location.hash.replace(/^#/, "") || "/";
  const needsResult = ["/today", "/court"].includes(route) && !state.response;
  if (needsResult) return go("/");
  const views: Record<string, [() => string, (() => void) | undefined]> = {
    "/": [() => renderStart(state), () => bindStart(state, go)],
    "/today": [() => renderToday(state), () => bindToday(state, go)],
    "/court": [() => renderCourt(state), undefined],
    "/away": [() => renderAway(), () => bindAway(go)],
    "/checkin": [() => renderCheckin(), () => bindCheckin(go)],
    "/hood": [() => renderHood(state), () => bindHood()],
  };
  const [render, bind] = views[route] ?? views["/"];
  document.body.dataset.route = route.slice(1) || "start";
  app.innerHTML = render() + footer();
  bind?.();
  window.scrollTo(0, 0);
}

warm();
loadDemo().catch(() => undefined).finally(() => { window.addEventListener("hashchange", draw); draw(); });
