// CUPIM entry page: the pyramid, every layer per portal, and the schedule in force of every workflow,
// with a link to change it. Reads registry.json (always there) and data/schedules.json (written by
// the daily reading; absent before the first run). Every text from data is inserted with textContent.
"use strict";

(() => {
  const params = new URLSearchParams(location.search);
  const lang = params.get("lang") || ((navigator.language || "").toLowerCase().startsWith("pt") ? "pt" : "en");
  document.documentElement.lang = lang === "pt" ? "pt-BR" : "en";

  const T = {
    en: {
      repo: "Repository", eyebrow: "5L-TEP · Five-Layer Trust Engineering Pyramid",
      intro: "CUPIM is the entry point of the Five-Layer Trust Engineering Pyramid (5L-TEP, SOFTENG 2026) applied to open government data on CKAN portals. Each layer is a repository of its own, applied to the IBAMA portal and, with the same code, to other portals. This page links them all and shows when each workflow runs, with a link to change it.",
      overview_h: "The pyramid", instances_h: "Layers and portals",
      instances_note: "One repository per layer and portal; the same code, three settings files per instance. The comparison between portals is reuse of the same code, not a ranking of the agencies.",
      aux_h: "Model benchmarks", schedules_h: "Schedules",
      schedules_note: "When each workflow runs, as written in the workflow file of its repository today. No layer waits for another: each one reads the last summary the others published.",
      edit_note: "To change a schedule, \"change\" opens the workflow file in the GitHub editor: with write access, edit the cron line and commit. Without it, GitHub offers a copy (fork) and a pull request. The ANEEL and Recife instances follow the IBAMA schedule of the same layer.",
      principles_h: "How this platform works",
      principles: [
        "Zero cost end to end: public repositories, free GitHub Actions runners and GitHub Pages; no server, no domain.",
        "Pull without tokens: every page reads the public files of the others over HTTPS; CUPIM never writes to another repository.",
        "Results only from GitHub Actions; local trials are for debugging.",
        "It informs; it never decides. A signal is something to check; a gap is missing evidence, never a low score.",
        "A new portal: one entry in the registry and one repository per layer with its settings files.",
      ],
      footer: "Luciano Santos Pinheiro · CESAR School, Recife · code under the MIT license.",
      layer: "Layer", workflow: "Workflow", when: "When ({tz})", cron: "Cron (UTC)", reads: "Reads", links: "Links",
      repository: "repository", dashboard: "dashboard", platform: "This platform", no_pages: "no dashboard",
      edit: "change ↗", runs: "runs ↗", read_now: "read now ↗",
      loading_failed: "Could not load the registry of this page.",
      not_read: "Schedules not read yet: the first reading runs on GitHub Actions after publication.",
      read_at: "Read from the repositories on {d}; updated every day.",
      follows: "{p}: follow IBAMA", own: "own schedule, changed in the instance repository (the next deploy of the layer brings back the IBAMA schedule)",
      no_schedule: "no schedule", unlisted_h: "Scheduled workflows not in the registry",
      s_missing_repository: "repository not found", s_missing_workflow: "workflow not found", s_unreachable: "not read now",
      daily: "daily at {t}", weekly: "{d} at {t}", monthly: "day {n} of each month at {t}", hourly: "every {n} h, at {t}",
      days: ["Sundays", "Mondays", "Tuesdays", "Wednesdays", "Thursdays", "Fridays", "Saturdays"],
    },
    pt: {
      repo: "Repositório", eyebrow: "5L-TEP · Pirâmide de Engenharia de Confiança de Cinco Camadas",
      intro: "O CUPIM é a porta de entrada da Pirâmide de Engenharia de Confiança de Cinco Camadas (5L-TEP, SOFTENG 2026) aplicada a dados abertos governamentais em portais CKAN. Cada camada é um repositório próprio, aplicado ao portal do IBAMA e, com o mesmo código, a outros portais. Esta página reúne os links de todos e mostra quando cada workflow roda, com o link para alterar.",
      overview_h: "A pirâmide", instances_h: "Camadas e portais",
      instances_note: "Um repositório por camada e portal; o mesmo código, três arquivos de configuração por instância. A comparação entre portais é reutilização do mesmo código, não ranking dos órgãos.",
      aux_h: "Benchmarks de modelos", schedules_h: "Horários",
      schedules_note: "Quando cada workflow roda, como está hoje no arquivo de workflow do seu repositório. Nenhuma camada espera outra: cada uma lê o último resumo que as outras publicaram.",
      edit_note: "Para mudar um horário, \"alterar\" abre o arquivo do workflow no editor do GitHub: com permissão de escrita, basta mudar a linha cron e confirmar (commit). Sem permissão, o GitHub oferece uma cópia (fork) e um pull request. As instâncias ANEEL e Recife seguem o horário do IBAMA da mesma camada.",
      principles_h: "Como esta plataforma funciona",
      principles: [
        "Custo zero de ponta a ponta: repositórios públicos, runners gratuitos do GitHub Actions e GitHub Pages; sem servidor, sem domínio.",
        "Leitura sem token: cada página lê por HTTPS os arquivos públicos das outras; o CUPIM nunca escreve em outro repositório.",
        "Resultados só do GitHub Actions; ensaios locais servem para depurar.",
        "Informa; não decide. Sinal é item a conferir; lacuna é evidência ausente, nunca nota baixa.",
        "Novo portal: uma entrada no registro e um repositório por camada com seus arquivos de configuração.",
      ],
      footer: "Luciano Santos Pinheiro · CESAR School, Recife · código sob a licença MIT.",
      layer: "Camada", workflow: "Workflow", when: "Quando ({tz})", cron: "Cron (UTC)", reads: "Lê", links: "Links",
      repository: "repositório", dashboard: "painel", platform: "Esta plataforma", no_pages: "sem painel",
      edit: "alterar ↗", runs: "execuções ↗", read_now: "ler agora ↗",
      loading_failed: "Não foi possível carregar o registro desta página.",
      not_read: "Horários ainda não lidos: a primeira leitura roda no GitHub Actions depois da publicação.",
      read_at: "Lidos dos repositórios em {d}; atualizados todo dia.",
      follows: "{p}: seguem o IBAMA", own: "horário próprio, alterado no repositório da instância (o próximo deploy da camada volta ao horário do IBAMA)",
      no_schedule: "sem horário", unlisted_h: "Workflows com horário fora do registro",
      s_missing_repository: "repositório não encontrado", s_missing_workflow: "workflow não encontrado", s_unreachable: "não lido agora",
      daily: "todo dia às {t}", weekly: "{d} às {t}", monthly: "dia {n} de cada mês às {t}", hourly: "a cada {n} h, às {t}",
      days: ["domingos", "segundas", "terças", "quartas", "quintas", "sextas", "sábados"],
    },
  };
  const t = (key, vars) => {
    let s = (T[lang] && T[lang][key]) || T.en[key] || key;
    for (const [k, v] of Object.entries(vars || {})) s = s.replace(`{${k}}`, v);
    return s;
  };
  const tx = (obj) => (obj && (obj[lang] || obj.en)) || "";

  const SVG = "http://www.w3.org/2000/svg";
  function el(tag, attrs, ...children) {
    const node = tag.startsWith("svg:") ? document.createElementNS(SVG, tag.slice(4)) : document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) {
      if (v === null || v === undefined) continue;
      if (k === "class") node.setAttribute("class", v);
      else if (k === "href") { if (/^(https?:|#|\?)/.test(v)) node.setAttribute("href", v); }
      else node.setAttribute(k, v);
    }
    for (const c of children.flat(2)) if (c !== null && c !== undefined && c !== false)
      node.append(c instanceof Node ? c : document.createTextNode(String(c)));
    return node;
  }
  const link = (href, text) => el("a", { href, target: "_blank", rel: "noopener" }, text);

  // ---- cron in words, in the display time zone (simple patterns; anything else shows the cron only)
  const pad = (n) => String(n).padStart(2, "0");
  function describe(expr, offsetHours) {
    const [mi, ho, dom, mon, dow] = expr.trim().split(/\s+/);
    const num = (s) => /^\d+$/.test(s);
    if (mon !== "*" || !num(mi)) return null;
    const shift = (h) => {
      const total = h * 60 + Number(mi) + offsetHours * 60;
      const day = Math.floor(total / 1440);
      const local = ((total % 1440) + 1440) % 1440;
      return { day, time: `${pad(Math.floor(local / 60))}:${pad(local % 60)}` };
    };
    const every = /^\*\/(\d+)$/.exec(ho);
    if (every && dom === "*" && dow === "*") {
      const n = Number(every[1]);
      const times = [];
      for (let h = 0; h < 24; h += n) times.push(shift(h).time);
      return t("hourly", { n, t: times.sort().join(", ") });
    }
    if (!num(ho)) return null;
    const { day, time } = shift(Number(ho));
    if (dom === "*" && dow === "*") return t("daily", { t: time });
    if (dom === "*" && num(dow)) return t("weekly", { d: T[lang].days[(((Number(dow) + day) % 7) + 7) % 7], t: time });
    if (num(dom) && dow === "*") {
      const n = Number(dom) + day;
      return n >= 1 && n <= 28 ? t("monthly", { n, t: time }) : null;
    }
    return null;
  }

  function render(reg, data) {
    const owner = reg.owner;
    const tzName = (reg.timezone && reg.timezone.name || "UTC").split("/").pop().replace(/_/g, " ");
    const offset = (reg.timezone && reg.timezone.utc_offset_hours) || 0;
    const repoUrl = (o, r) => `https://github.com/${o}/${r}`;
    const pagesUrl = (o, r) => (r === `${o}.github.io` ? `https://${r}/` : `https://${o}.github.io/${r}/`);
    const editUrl = (o, r, f) => `${repoUrl(o, r)}/edit/main/.github/workflows/${f}`;
    const runsUrl = (o, r, f) => `${repoUrl(o, r)}/actions/workflows/${f}`;
    const items = new Map(((data && data.items) || []).map((i) => [`${i.repository}::${i.file}`, i]));
    const itemFor = (o, r, file) => items.get(`${o}/${r}::${file}`);
    const p = reg.platform;
    const portals = reg.portals;
    const main = portals.find((x) => x.main);

    // texts and links of the frame
    document.querySelectorAll("[data-i18n]").forEach((node) => { const v = T[lang][node.dataset.i18n]; if (typeof v === "string") node.textContent = v; });
    document.getElementById("repo-link").href = repoUrl(p.owner, p.repository);
    document.getElementById("readme-link").href = `${repoUrl(p.owner, p.repository)}#readme`;
    document.getElementById("leiame-link").href = `${repoUrl(p.owner, p.repository)}/blob/main/LEIAME.md`;
    document.getElementById(`lang-${lang}`).classList.add("current");

    // pyramid: L1 at the base, L5 at the top
    const W = 420, H = 300, n = reg.layers.length, band = H / n, gap = 3;
    const svg = el("svg:svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": t("overview_h") });
    reg.layers.forEach((layer, idx) => {
      const level = n - 1 - idx;                         // 0 = top band
      const y0 = level * band + gap / 2, y1 = (level + 1) * band - gap / 2;
      const half = (y) => (W / 2) * (y / H) * 0.98 + 6;
      const pts = [[W / 2 - half(y0), y0], [W / 2 + half(y0), y0], [W / 2 + half(y1), y1], [W / 2 - half(y1), y1]];
      const a = el("svg:a", { href: `#layer-${layer.id}` });
      a.append(el("svg:polygon", { points: pts.map((q) => q.join(",")).join(" "), style: `fill: var(--level-${idx})` }));
      const cy = (y0 + y1) / 2;
      a.append(el("svg:text", { x: W / 2, y: level === 0 ? cy + 14 : cy + 5, "text-anchor": "middle", style: `fill: var(--ink-${idx})` }, layer.id));
      a.append(el("svg:title", {}, `${layer.id} · ${tx(layer.name)}`));
      svg.append(a);
    });
    document.getElementById("pyramid").replaceChildren(svg);
    document.getElementById("layer-list").replaceChildren(...[...reg.layers].reverse().map((layer, i) => {
      const repo = layer.instances[main.id];
      return el("li", { id: `layer-${layer.id}`, style: `border-left-color: var(--level-${n - 1 - i})` },
        el("strong", {}, `${layer.id} · ${tx(layer.name)}`),
        link(layer.pages ? pagesUrl(owner, repo) : repoUrl(owner, repo), layer.pages ? t("dashboard") : t("repository")),
        el("div", { class: "muted small" }, tx(layer.summary)));
    }));

    // layers × portals
    const head = el("thead", {}, el("tr", {}, el("th", {}, t("layer")),
      ...portals.map((pt) => el("th", {}, link(pt.url, pt.name)))));
    const body = el("tbody", {}, ...reg.layers.map((layer) => el("tr", {},
      el("td", {}, el("strong", {}, layer.id), " ", tx(layer.name)),
      ...portals.map((pt) => {
        const repo = layer.instances[pt.id];
        if (!repo) return el("td", { class: "muted" }, "—");
        return el("td", {}, el("div", { class: "links" },
          link(repoUrl(owner, repo), t("repository")),
          layer.pages ? link(pagesUrl(owner, repo), t("dashboard")) : el("span", { class: "muted" }, t("no_pages"))));
      }))));
    document.getElementById("instances-table").replaceChildren(head, body);
    document.getElementById("aux-list").replaceChildren(...(reg.auxiliary || []).map((aux) => el("li", {},
      link(repoUrl(owner, aux.repository), aux.repository), ` (${aux.layer}): `, tx(aux.summary))));

    // schedules: the cron in force, read from the published workflow
    const same = (a, b) => JSON.stringify([...(a || [])].sort()) === JSON.stringify([...(b || [])].sort());
    const whenCell = (item) => {
      if (!item) return [el("td", { class: "muted" }, "—"), el("td", { class: "muted" }, "—")];
      if (item.status !== "read" && item.status !== "unlisted")
        return [el("td", { colspan: 2 }, el("span", { class: "status neutral" }, t(`s_${item.status}`)))];
      if (!item.cron.length) return [el("td", { class: "muted" }, t("no_schedule")), el("td", {}, "—")];
      return [
        el("td", { class: "when" }, item.cron.map((c, i) => [i ? el("br") : null, describe(c, offset) || "—"])),
        el("td", { class: "when" }, item.cron.map((c, i) => [i ? el("br") : null, el("span", { class: "mono" }, c)])),
      ];
    };
    const linksCell = (o, r, f, editable) => el("td", {}, el("div", { class: "links" },
      editable ? link(editUrl(o, r, f), t("edit")) : null, link(runsUrl(o, r, f), t("runs"))));
    const purpose = (w) => [el("span", { class: "mono" }, w.file), el("div", { class: "muted small" }, tx(w.purpose))];

    const rows = [];
    for (const layer of reg.layers) {
      for (const w of layer.workflows) {
        const mainRepo = layer.instances[main.id];
        const mainItem = itemFor(owner, mainRepo, w.file);
        rows.push(el("tr", {}, el("td", {}, el("strong", {}, layer.id)), el("td", {}, purpose(w)),
          whenCell(mainItem), el("td", { class: "small" }, (w.reads || []).join(", ") || "—"),
          linksCell(owner, mainRepo, w.file, true)));
        const others = portals.filter((pt) => !pt.main && layer.instances[pt.id]);
        const followers = [], own = [];
        for (const pt of others) {
          const it = itemFor(owner, layer.instances[pt.id], w.file);
          (!it || !mainItem || (it.status === mainItem.status && same(it.cron, mainItem.cron)) ? followers : own).push([pt, it]);
        }
        if (followers.length)
          rows.push(el("tr", { class: "sub" }, el("td", {}), el("td", { colspan: 4, class: "muted small" },
            t("follows", { p: followers.map(([pt]) => pt.name).join(", ") })),
            el("td", { class: "small" }, el("div", { class: "links" },
              followers.map(([pt]) => link(runsUrl(owner, layer.instances[pt.id], w.file), `${pt.name} ${t("runs")}`))))));
        for (const [pt, it] of own)
          rows.push(el("tr", { class: "sub" }, el("td", {}),
            el("td", { class: "small" }, el("span", { class: "status warning" }, pt.name), el("div", { class: "muted small" }, t("own"))),
            whenCell(it), el("td", {}), linksCell(owner, layer.instances[pt.id], w.file, false)));
      }
    }
    for (const aux of reg.auxiliary || []) for (const w of aux.workflows)
      rows.push(el("tr", {}, el("td", {}, el("strong", {}, aux.layer), " · ", aux.repository.replace(/^5ltep-layer\d-/, "")),
        el("td", {}, purpose(w)), whenCell(itemFor(owner, aux.repository, w.file)), el("td", {}, "—"),
        linksCell(owner, aux.repository, w.file, true)));
    for (const w of p.workflows)
      rows.push(el("tr", {}, el("td", {}, t("platform")), el("td", {}, purpose(w)),
        whenCell(itemFor(p.owner, p.repository, w.file)), el("td", {}, "—"), linksCell(p.owner, p.repository, w.file, true)));
    document.getElementById("schedule-table").replaceChildren(
      el("thead", {}, el("tr", {}, [t("layer"), t("workflow"), t("when", { tz: tzName }), t("cron"), t("reads"), t("links")].map((h) => el("th", {}, h)))),
      el("tbody", {}, rows));

    const status = document.getElementById("schedule-status");
    const fmt = new Intl.DateTimeFormat(lang === "pt" ? "pt-BR" : "en", { dateStyle: "medium", timeStyle: "short", timeZone: (reg.timezone && reg.timezone.name) || "UTC" });
    status.replaceChildren(data ? t("read_at", { d: fmt.format(new Date(data.generated_at)) }) : t("not_read"), " ",
      p.workflows.length ? link(runsUrl(p.owner, p.repository, p.workflows[0].file), t("read_now")) : null);
    const unlisted = ((data && data.items) || []).filter((i) => i.status === "unlisted");
    document.getElementById("unlisted").replaceChildren(...(unlisted.length ? [
      el("h3", { style: "margin-top:14px" }, t("unlisted_h")),
      el("ul", { class: "plain" }, unlisted.map((i) => el("li", {},
        link(`https://github.com/${i.repository}/blob/HEAD/.github/workflows/${i.file}`, `${i.repository} · ${i.file}`),
        el("span", { class: "muted small" }, ` — ${i.cron.map((c) => describe(c, offset) || c).join("; ")}`)))),
    ] : []));

    document.getElementById("principles-list").replaceChildren(...T[lang].principles.map((s) => el("li", {}, s)));
  }

  async function load(url, optional) {
    try {
      const res = await fetch(url, { cache: "no-cache" });
      if (!res.ok) throw new Error(res.status);
      return await res.json();
    } catch (err) {
      if (optional) return null;
      throw err;
    }
  }

  Promise.all([load("registry.json"), load("data/schedules.json", true)])
    .then(([reg, data]) => render(reg, data))
    .catch(() => {
      const notice = document.getElementById("notice");
      notice.textContent = t("loading_failed");
      notice.hidden = false;
    });
})();
