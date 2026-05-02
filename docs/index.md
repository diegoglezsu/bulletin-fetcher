# bulletin-fetcher

bulletin-fetcher is a Python library for searching and managing official bulletins,
currently focused on the Official Journal of the European Union via EUR-Lex.

<div style="text-align: center; margin: 20px 0;">
    <img src="assets/logo.jpg" alt="Bulletin Fetcher Logo" width="200" />
</div>

## Why bulletin-fetcher?

EU legal acts can be queried through public semantic web infrastructure, but using the underlying SPARQL endpoint requires knowledge of RDF vocabularies, query structure and EUR-Lex metadata conventions and ontologies.

`bulletin-fetcher` abstracts this complexity behind a simple Python interface. Users can retrieve legal acts by publication date, date ranges, act type, publishing institution and textual content, while receiving Python objects, JSON-compatible dictionaries or CSV outputs suitable for further analysis.

## Main features

- Search EU legal acts from the Official Journal of the European Union.
- Filter acts by date or date range, act type, publishing institution, text contained in the act title, language.
- Retrieve available act types and publishing institutions.
- Return act search results as Python objects, JSON-compatible dictionaries or CSV.
- Work with Python instead of raw SPARQL queries.
- Integrate easily with notebooks, data pipelines and legal analytics workflows.

## Use Cases

bulletin-fetcher can be used for:

- Legal analytics
- Public policy research
- Regulatory monitoring
- Reproducible studies based on legal acts
- Data collection pipelines
