from services.content_intelligence import ContentIntelligence


content = """
Cybersecurity researchers have identified a phishing campaign
targeting educational institutions.

The attackers send fraudulent emails that appear to come from
trusted organizations. The emails contain malicious links that
direct users to fake login pages.

The campaign highlights the importance of multi-factor
authentication, employee awareness training and verifying
suspicious links before entering credentials.
"""


engine = ContentIntelligence()

result = engine.analyze(
    content,
    source_files=["sample_cybersecurity_report.txt"]
)

engine.print_model(result)

engine.save(
    result,
    "sample_content_model.json"
)