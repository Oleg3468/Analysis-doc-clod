import os
import analyzer


def test_files_exist():
    assert os.path.exists("analyzer.py")
    assert os.path.exists("README.md")


def test_analyzer_import():
    assert hasattr(analyzer, "main")
    assert hasattr(analyzer, "analyze_text")


def test_clean_text_has_no_findings():
    text = "This is a normal agreement with no unusual clauses. Have a nice day."
    findings = analyzer.analyze_text(text)
    assert findings == []


def test_english_auto_renewal_detected():
    text = "Your plan automatically renews every month unless cancelled."
    findings = analyzer.analyze_text(text)
    categories = [f["category"] for f in findings]
    assert "Automatic paid renewals" in categories
    critical = [f for f in findings if f["category"] == "Automatic paid renewals"]
    assert all(f["is_critical"] for f in critical)


def test_russian_auto_renewal_detected():
    text = "Ваша подписка автоматически продлевается каждый месяц."
    findings = analyzer.analyze_text(text)
    categories = [f["category"] for f in findings]
    assert "Automatic paid renewals" in categories


def test_third_party_data_sharing_detected():
    text = "We may share your data with third-parties for marketing purposes."
    findings = analyzer.analyze_text(text)
    categories = [f["category"] for f in findings]
    assert "Third-party data sharing" in categories


def test_non_refundable_detected():
    text = "All payments are non-refundable once processed."
    findings = analyzer.analyze_text(text)
    categories = [f["category"] for f in findings]
    assert "Hidden fees / non-refundable" in categories


def test_arbitration_waiver_detected():
    text = "You agree to mandatory arbitration and waive your right to a class action."
    findings = analyzer.analyze_text(text)
    categories = [f["category"] for f in findings]
    assert "Waiver of rights / forced arbitration" in categories


def test_liability_limitation_detected():
    text = "The company shall not be liable for any damages whatsoever."
    findings = analyzer.analyze_text(text)
    categories = [f["category"] for f in findings]
    assert "Full liability limitation" in categories


def test_findings_have_context_and_match():
    text = "Your plan automatically renews every month."
    findings = analyzer.analyze_text(text)
    assert len(findings) > 0
    for f in findings:
        assert f["matched"]
        assert f["context"]
        assert "category" in f
        assert "description" in f
        assert "is_critical" in f


def test_empty_text_returns_no_findings():
    assert analyzer.analyze_text("") == []
    assert analyzer.analyze_text(None) == []
  
