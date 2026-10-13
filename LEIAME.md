# CUPIM: porta de entrada da plataforma 5L-TEP

[Read in English](README.md) · [Site](https://5ltep-cupim.github.io/?lang=pt)


O CUPIM é a porta de entrada da Pirâmide de Engenharia de Confiança de Cinco Camadas (5L-TEP, SOFTENG
2026) aplicada a dados abertos governamentais publicados em portais CKAN. Cada camada é um repositório
próprio, aplicado ao portal de dados abertos do IBAMA e, com o mesmo código, a outros portais (ANEEL e
Recife). Este repositório reúne os links de todos e mostra quando cada workflow roda, com o link para alterar.

## As camadas

| Camada | IBAMA | ANEEL | Recife |
|---|---|---|---|
| L1 Contratos estruturais | [5ltep-layer1](https://github.com/lsp3cesarschool/5ltep-layer1) | [5ltep-layer1-aneel](https://github.com/lsp3cesarschool/5ltep-layer1-aneel) | [5ltep-layer1-recife](https://github.com/lsp3cesarschool/5ltep-layer1-recife) |
| L2 Políticas semânticas | [5ltep-layer2](https://github.com/lsp3cesarschool/5ltep-layer2) | [5ltep-layer2-aneel](https://github.com/lsp3cesarschool/5ltep-layer2-aneel) | [5ltep-layer2-recife](https://github.com/lsp3cesarschool/5ltep-layer2-recife) |
| L3 Detecção de anomalias | [5ltep-layer3](https://github.com/lsp3cesarschool/5ltep-layer3) | [5ltep-layer3-aneel](https://github.com/lsp3cesarschool/5ltep-layer3-aneel) | [5ltep-layer3-recife](https://github.com/lsp3cesarschool/5ltep-layer3-recife) |
| L4 Observabilidade e proveniência | [5ltep-layer4](https://github.com/lsp3cesarschool/5ltep-layer4) | [5ltep-layer4-aneel](https://github.com/lsp3cesarschool/5ltep-layer4-aneel) | [5ltep-layer4-recife](https://github.com/lsp3cesarschool/5ltep-layer4-recife) |
| L5 Governança e publicação | [5ltep-layer5](https://github.com/lsp3cesarschool/5ltep-layer5) | [5ltep-layer5-aneel](https://github.com/lsp3cesarschool/5ltep-layer5-aneel) | [5ltep-layer5-recife](https://github.com/lsp3cesarschool/5ltep-layer5-recife) |

Benchmarks de modelos: [5ltep-layer1-modeltest](https://github.com/lsp3cesarschool/5ltep-layer1-modeltest)
e [5ltep-layer3-modeltest](https://github.com/lsp3cesarschool/5ltep-layer3-modeltest). O painel de cada
repositório tem link no [site](https://5ltep-cupim.github.io/?lang=pt). A visão agregada da evidência por
conjunto de dados (pontuação de qualidade, fichas citáveis) é a Camada 5; o CUPIM não a repete.

Rodar o mesmo código em outros portais mostra reutilização; não é ranking dos órgãos.

## Horários

[`docs/registry.json`](docs/registry.json) lista os portais, o repositório de cada camada por portal e
para que serve cada workflow com horário. Ele não guarda horário: todo dia às 06:40 UTC (e sempre que o
registro muda) o CUPIM lê o cron de cada workflow no arquivo que o repositório publica, e o site mostra o
horário em vigor, em UTC e no horário de Recife. Nenhuma camada espera outra: cada uma lê o último resumo
que as outras publicaram.

Para mudar um horário, o link **alterar** do site abre o arquivo do workflow no editor do GitHub
(`https://github.com/<dono>/<repositório>/edit/main/.github/workflows/<arquivo>`). Com permissão de
escrita no repositório, basta mudar a linha `cron` e confirmar (commit); sem ela, o GitHub oferece uma
cópia (fork) e um pull request. O CUPIM nunca escreve em outro repositório; por isso não guarda token
para eles.

O link aparece para o repositório IBAMA de cada camada, para os benchmarks de modelos e para o próprio
CUPIM. As instâncias ANEEL e Recife seguem o horário do IBAMA da mesma camada: seus repositórios são
remontados a partir do código do IBAMA a cada deploy, então uma mudança feita direto numa instância seria
desfeita no deploy seguinte (o site aponta essa diferença enquanto ela existir).

Um novo portal é uma entrada em `portals` e um repositório por camada em `instances`. Mudar os
repositórios para outra conta altera só `owner`.

## Como rodar localmente

```bash
pip install pytest
python -m pytest tests -q
python main.py --out build            # reads GitHub; GITHUB_TOKEN only raises the rate limit
```

O código usa só a biblioteca padrão do Python. Resultados são publicados só pelo GitHub Actions; execuções
locais servem para depurar. O site é estático (`docs/`), servido pelo GitHub Pages.

## Segurança

O workflow segue as mesmas regras das camadas: o job que lê o GitHub tem token só de leitura e entrega um
artefato; o job que escreve aceita só os arquivos esperados ([`src/accept.py`](src/accept.py)); nenhuma
expressão `${{ }}` dentro de `run:`.

## Citação e licença

Ver [`CITATION.cff`](CITATION.cff). Código sob a [licença MIT](LICENSE).

Luciano Santos Pinheiro, CESAR School (Recife), pesquisa de mestrado em Engenharia de Software.
