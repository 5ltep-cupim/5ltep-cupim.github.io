# CUPIM: entry point of the 5L-TEP platform

[Leia em português](LEIAME.md) · [Site](https://5ltep-cupim.github.io/)


CUPIM is the entry point of the Five-Layer Trust Engineering Pyramid (5L-TEP, SOFTENG 2026) applied
to open government data published on CKAN portals. Each layer is a repository of its own, applied to
the IBAMA open data portal and, with the same code, to other portals (ANEEL and Recife). This
repository links them all and shows when each workflow runs, with a link to change it.

## The layers

| Layer | IBAMA | ANEEL | Recife |
|---|---|---|---|
| L1 Structural contracts | [5ltep-layer1](https://github.com/lsp3cesarschool/5ltep-layer1) | [5ltep-layer1-aneel](https://github.com/lsp3cesarschool/5ltep-layer1-aneel) | [5ltep-layer1-recife](https://github.com/lsp3cesarschool/5ltep-layer1-recife) |
| L2 Semantic policies | [5ltep-layer2](https://github.com/lsp3cesarschool/5ltep-layer2) | [5ltep-layer2-aneel](https://github.com/lsp3cesarschool/5ltep-layer2-aneel) | [5ltep-layer2-recife](https://github.com/lsp3cesarschool/5ltep-layer2-recife) |
| L3 Anomaly detection | [5ltep-layer3](https://github.com/lsp3cesarschool/5ltep-layer3) | [5ltep-layer3-aneel](https://github.com/lsp3cesarschool/5ltep-layer3-aneel) | [5ltep-layer3-recife](https://github.com/lsp3cesarschool/5ltep-layer3-recife) |
| L4 Observability and provenance | [5ltep-layer4](https://github.com/lsp3cesarschool/5ltep-layer4) | [5ltep-layer4-aneel](https://github.com/lsp3cesarschool/5ltep-layer4-aneel) | [5ltep-layer4-recife](https://github.com/lsp3cesarschool/5ltep-layer4-recife) |
| L5 Governance and publication | [5ltep-layer5](https://github.com/lsp3cesarschool/5ltep-layer5) | [5ltep-layer5-aneel](https://github.com/lsp3cesarschool/5ltep-layer5-aneel) | [5ltep-layer5-recife](https://github.com/lsp3cesarschool/5ltep-layer5-recife) |

Model benchmarks: [5ltep-layer1-modeltest](https://github.com/lsp3cesarschool/5ltep-layer1-modeltest)
and [5ltep-layer3-modeltest](https://github.com/lsp3cesarschool/5ltep-layer3-modeltest). The dashboard
of each repository is linked from the [site](https://5ltep-cupim.github.io/). The aggregated view of the
evidence per dataset (quality score, citable records) is Layer 5; CUPIM does not repeat it.

Running the same code on other portals shows reuse; it is not a ranking of the agencies.

## Schedules

[`docs/registry.json`](docs/registry.json) lists the portals, the repository of each layer per portal
and what each scheduled workflow is for. It holds no schedule: every day at 06:40 UTC (and whenever the
registry changes) CUPIM reads the cron of each workflow from the file its repository publishes, and the
site shows the schedule in force, in UTC and in Recife time. No layer waits for another: each one reads
the last summary the others published.

To change a schedule, the site's **change** link opens the workflow file in the GitHub editor
(`https://github.com/<owner>/<repository>/edit/main/.github/workflows/<file>`). With write access to the
repository, edit the `cron` line and commit; without it, GitHub offers a copy (fork) and a pull request.
CUPIM never writes to another repository, so it holds no token for them.

The link is offered for the IBAMA repository of each layer, the model benchmarks and CUPIM itself. The
ANEEL and Recife instances follow the IBAMA schedule of the same layer: their repositories are rebuilt
from the IBAMA code at each deploy, so a change made directly in an instance would be undone by the next
deploy (the site points out such a difference while it lasts).

A new portal is one entry in `portals` and one repository per layer in `instances`. Moving the
repositories to another account changes only `owner`.

## Running locally

```bash
pip install pytest
python -m pytest tests -q
python main.py --out build            # reads GitHub; GITHUB_TOKEN only raises the rate limit
```

The code uses only the Python standard library. Results are published only by GitHub Actions; local runs
are for debugging. The site is static (`docs/`), served by GitHub Pages.

## Security

The workflow follows the same rules as the layers: the job that reads GitHub has a read-only token and
hands over an artifact; the job that writes accepts only the expected files
([`src/accept.py`](src/accept.py)); no `${{ }}` expression inside `run:`.

## Citation and license

See [`CITATION.cff`](CITATION.cff). Code under the [MIT license](LICENSE).

Luciano Santos Pinheiro, CESAR School (Recife, Brazil), master's research in Software Engineering.
