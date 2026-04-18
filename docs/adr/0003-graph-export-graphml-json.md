# ADR-0003: Export do grafo de investigação em JSON (node-link) e GraphML

## Estado

Aceite

## Contexto

Analistas usam ferramentas externas (Gephi, Python, notebooks) e precisam de formatos interoperáveis além do JSON já exposto na API de análise de rede.

## Decisão

- Endpoint dedicado `GET /api/v1/investigations/{id}/network/export?export_format=json|graphml`.
- **JSON:** `networkx.readwrite.json_graph.node_link_data` (chaves `nodes`, `edges`).
- **GraphML:** `networkx.write_graphml` sobre um grafo com atributos serializáveis (strings/números).

## Consequências

- **Positivo:** integração com ecossistema de grafos; ficheiros descarregáveis com `Content-Disposition`.
- **Negativo:** grafos muito grandes aumentam tempo de serialização; atributos complexos são convertidos a string.
