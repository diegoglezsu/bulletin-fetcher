import re

library_call = """
acts = client.get_acts(
  date="2025-01-01",
  date_end="2026-03-31",
  language="ENG",
  title_contains="science",
  category_type="ANNOUNC",
  institution_type="COM",
)
"""

sparql_query = """
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?act ?celexAct ?actNumber ?title ?date ?sectionCode ?subsectionCode ?categoryCode ?categoryUri ?categoryLabel ?institutionCode ?institutionUri ?institutionLabel
WHERE { ?c_act (cdm:official-journal-act_date_publication|
cdm:resource_legal_published_in_official-journal/cdm:publication_general_date_publication) ?date . FILTER(?date >= "2025-01-01"^^xsd:date) FILTER(?date <= "2026-03-31"^^xsd:date)
  OPTIONAL { SELECT ?c_act (MIN(STR(?eliCandidate)) AS ?eliUriStr) WHERE { ?c_act owl:sameAs ?eliCandidate . FILTER(CONTAINS(STR(?eliCandidate), "/resource/eli/")) } GROUP BY ?c_act } OPTIONAL { SELECT ?c_act (MIN(STR(?celexCandidate)) AS ?celexUriStr) WHERE { ?c_act owl:sameAs ?celexCandidate . FILTER(CONTAINS(STR(?celexCandidate), "/resource/celex/")) } GROUP BY ?c_act } OPTIONAL { SELECT ?c_act (MIN(STR(?ojCandidate)) AS ?ojUriStr) WHERE { ?c_act owl:sameAs ?ojCandidate . FILTER(CONTAINS(STR(?ojCandidate), "/resource/oj/")) } GROUP BY ?c_act }
  BIND(COALESCE(?eliUriStr, ?celexUriStr, ?ojUriStr) AS ?rawActStr) FILTER(BOUND(?rawActStr))
  BIND(IF(CONTAINS(?rawActStr, "/resource/eli/"), IRI(REPLACE(?rawActStr, "http://publications.europa.eu/resource/eli/", "https://eur-lex.europa.eu/eli/")), IRI(?rawActStr)) AS ?act) BIND(IRI(?celexUriStr) AS ?celexAct)
  { SELECT ?c_act (MIN(STR(?titleCandidate)) AS ?title) WHERE { ?expr cdm:expression_belongs_to_work ?c_act ; cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> ; cdm:expression_title ?titleCandidate . FILTER(CONTAINS(LCASE(STR(?titleCandidate)), LCASE("science"))) } GROUP BY ?c_act } OPTIONAL { SELECT ?c_act (MIN(STR(?sectionCandidate)) AS ?sectionCode) WHERE { ?c_act cdm:official-journal-act_section_oj ?sectionCandidate . } GROUP BY ?c_act } OPTIONAL { SELECT ?c_act (MIN(STR(?subsectionCandidate)) AS ?subsectionCode) WHERE { ?c_act cdm:official-journal-act_subsection_oj ?subsectionCandidate . } GROUP BY ?c_act }
  { SELECT ?c_act (MIN(STR(?categoryCandidate)) AS ?categoryUriStr) WHERE { ?c_act cdm:work_has_resource-type ?categoryCandidate . FILTER(REPLACE(STR(?categoryCandidate), ".*/", "") = "ANNOUNC") } GROUP BY ?c_act } BIND(IRI(?categoryUriStr) AS ?categoryUri) BIND(REPLACE(?categoryUriStr, ".*/", "") AS ?categoryCode)
  OPTIONAL { SELECT ?categoryUri (MIN(STR(?categoryLabelCandidate)) AS ?categoryLabel) WHERE { ?categoryUri skos:prefLabel ?categoryLabelCandidate . FILTER(LANG(?categoryLabelCandidate) = "en") } GROUP BY ?categoryUri }
  { SELECT ?c_act (MIN(STR(?institutionCandidate)) AS ?institutionUriStr) WHERE { ?c_act cdm:work_created_by_agent ?institutionCandidate . FILTER(REPLACE(STR(?institutionCandidate), ".*/", "") = "COM") } GROUP BY ?c_act } BIND(IRI(?institutionUriStr) AS ?institutionUri)
  BIND(REPLACE(?institutionUriStr, ".*/", "") AS ?institutionCode)
  OPTIONAL { SELECT ?institutionUri (MIN(STR(?institutionLabelCandidate)) AS ?institutionLabel) WHERE { ?institutionUri skos:prefLabel ?institutionLabelCandidate . FILTER(LANG(?institutionLabelCandidate) = "en") } GROUP BY ?institutionUri }
  OPTIONAL { SELECT ?c_act (MIN(STR(?officialJournalActNumberCandidate)) AS ?officialJournalActNumber) WHERE { ?c_act cdm:official-journal-act_number ?officialJournalActNumberCandidate . } GROUP BY ?c_act }
  OPTIONAL { SELECT ?c_act (MIN(STR(?resourceLegalNumberCandidate)) AS ?resourceLegalNumber) WHERE { ?c_act cdm:resource_legal_number_natural ?resourceLegalNumberCandidate . } GROUP BY ?c_act } BIND(COALESCE(?officialJournalActNumber, ?resourceLegalNumber) AS ?actNumber)} ORDER BY ?date ?act
"""

print("Library call:")
print(re.findall(r"\w+", library_call))

def metrics(text: str) -> dict:
    return {
        "chars": len(text),
        "lines": len([l for l in text.splitlines() if l.strip()]),
        "tokens": len(re.findall(r"\w+", text)) # Identificadores y literales
    }

def compare(name_a, a, name_b, b):
    ma = metrics(a)
    mb = metrics(b)

    print(f"\n{name_a}")
    print(ma)

    print(f"\n{name_b}")
    print(mb)

    print("\nReduction using library call:")
    print(
        f"Characters: {(1 - ma['chars']/mb['chars'])*100:.1f}%"
    )
    print(
        f"Lines: {(1 - ma['lines']/mb['lines'])*100:.1f}%"
    )
    print(
        f"Tokens: {(1 - ma['tokens']/mb['tokens'])*100:.1f}%"
    )
    print(f"Reduction of tokens: {mb['tokens']/ma['tokens']:.1f}x")

compare("Library", library_call, "SPARQL", sparql_query)