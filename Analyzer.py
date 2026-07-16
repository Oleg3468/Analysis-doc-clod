
#!/usr/bin/env python3
"""
Agreement Analyzer
-------------------
CLI tool that scans a user agreement (plain text, image, or screenshot) and
flags clauses that are unfavorable to the user: unilateral changes, silent
auto-renewals, third-party data sharing, hidden/non-refundable fees, waivers
of rights, and full liability limitations.
"""
import argparse
import io
import re
import sys

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import mss
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False


# ANSI colors
RED = "\033[91m"
YELLOW = "\033[93m"
PINK = "\033[95m"  # critical findings
GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

CONTEXT_CHARS = 60

# category_key -> (description, is_critical, [regex patterns])
RULES = {
    "Unilateral changes": (
        "The company can change terms or pricing without your explicit consent.",
        False,
        [
            r"(изменя(ть|ем|ются)\s+услови[яе].{0,40}(без\s+(уведомлени|согласи)))",
            r"(в\s+одностороннем\s+порядке)",
            r"(reserves?\s+the\s+right\s+to\s+change.{0,40}(at\s+any\s+time|without\s+notice))",
            r"(without\s+(prior\s+)?notice)",
        ],
    ),
    "Automatic paid renewals": (
        "Your subscription renews and charges automatically.",
        True,
        [
            r"(автоматически\s+продлевается)",
            r"(автопродлени[ея]|автосписани[ея])",
            r"(automatic(ally)?\s+renew(s|al|ed)?)",
            r"(auto[- ]renew(al)?)",
        ],
    ),
    "Third-party data sharing": (
        "Your personal data may be shared, sold, or tracked by third parties, including without consent.",
        True,
        [
            r"(передава(ть|ются|ем).{0,40}третьим\s+лицам)",
            r"(без\s+(вашего\s+)?(ведома|согласия).{0,40}(данн|отслеж|использ))",
            r"(share[sd]?.{0,40}with\s+third[- ]part(y|ies))",
            r"(sell\s+your\s+(personal\s+)?data)",
            r"(track(ing)?\s+.{0,30}(without\s+(your\s+)?(consent|knowledge)))",
        ],
    ),
    "Hidden fees / non-refundable": (
        "Fees may be non-refundable or hidden from initial disclosure.",
        False,
        [
            r"(не\s+подлежит\s+возврату)",
            r"(невозвратн\w+\s+плат)",
            r"(non[- ]refundable)",
            r"(no\s+refunds?)",
        ],
    ),
    "Waiver of rights / forced arbitration": (
        "You give up the right to join a class action or sue in court.",
        False,
        [
            r"(отказ(ываетесь)?\s+от\s+(права\s+на\s+)?(коллективн\w+\s+иск|суд))",
            r"(обязательн\w+\s+арбитраж)",
            r"(waive[sd]?\s+.{0,30}(right|class\s+action))",
            r"(mandatory\s+arbitration)",
            r"(binding\s+arbitration)",
        ],
    ),
    "Full liability limitation": (
        "The company fully disclaims responsibility for damages or data loss.",
        False,
        [
            r"(не\s+нес(е|ё)т\s+ответственност)",
            r"(снимает\s+с\s+себя\s+ответственност)",
            r"(not\s+(be\s+)?liable\s+for\s+any)",
            r"(limitation\s+of\s+liability)",
            r"(no\s+liability\s+whatsoever)",
        ],
    ),
}


def extract_text(file_path, lang="rus+eng"):
    """Load an image and run OCR on it. Requires Pillow + pytesseract."""
    if not OCR_AVAILABLE:
        raise RuntimeError(
            "OCR support is not installed. Run: pip install pillow pytesseract"
        )
    image = Image.open(file_path)
    return pytesseract.image_to_string(image, lang=lang)


def extract_text_from_screenshot(lang="rus+eng"):
    """Capture the active screen and run OCR on it. Requires mss."""
    if not SCREENSHOT_AVAILABLE:
        raise RuntimeError("Screenshot support is not installed. Run: pip install mss")
    if not OCR_AVAILABLE:
        raise RuntimeError(
            "OCR support is not installed. Run: pip install pillow pytesseract"
        )
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        shot = sct.grab(monitor)
        img = Image.frombytes("RGB", shot.size, shot.rgb)
    return pytesseract.image_to_string(img, lang=lang)


def analyze_text(text):
    """
    Scan text for unfavorable clauses.
    Returns a list of dicts: category, description, is_critical, matched, context.
    """
    findings = []
    if not text or not text.strip():
        return findings

    for category, (description, is_critical, patterns) in RULES.items():
        for pattern in patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, m.start() - CONTEXT_CHARS)
                end = min(len(text), m.end() + CONTEXT_CHARS)
                context = text[start:end].strip().replace("\n", " ")
                findings.append({
                    "category": category,
                    "description": description,
                    "is_critical": is_critical,
                    "matched": m.group(0).strip(),
                    "context": context,
                })
    return findings


def print_findings(findings):
    if not findings:
        print(f"{GREEN}{BOLD}No unfavorable clauses detected. Looks clean!{RESET}")
        return

    critical = [f for f in findings if f["is_critical"]]
    warnings = [f for f in findings if not f["is_critical"]]

    if critical:
        print(f"{PINK}{BOLD}{'=' * 60}{RESET}")
        print(f"{PINK}{BOLD}CRITICAL THREATS{RESET}")
        print(f"{PINK}{BOLD}{'=' * 60}{RESET}")
        for f in critical:
            print(f"{PINK}{BOLD}[{f['category']}]{RESET}")
            print(f"  {f['description']}")
            print(f"  Matched: {PINK}{f['matched']}{RESET}")
            print(f"  Context: ...{f['context']}...\n")

    if warnings:
        print(f"{YELLOW}{BOLD}{'=' * 60}{RESET}")
        print(f"{YELLOW}{BOLD}RIGHTS-LIMITING CLAUSES{RESET}")
        print(f"{YELLOW}{BOLD}{'=' * 60}{RESET}")
        for f in warnings:
            print(f"{YELLOW}{BOLD}[{f['category']}]{RESET}")
            print(f"  {f['description']}")
            print(f"  Matched: {YELLOW}{f['matched']}{RESET}")
            print(f"  Context: ...{f['context']}...\n")

    print(f"{RED}{BOLD}Total findings: {len(findings)} "
          f"({len(critical)} critical, {len(warnings)} warnings){RESET}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="analyzer.py",
        description="Scan a user agreement for clauses that are unfavorable to you.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--text", help="Path to a plain text file containing the agreement.")
    group.add_argument("-i", "--image", help="Path to an image/screenshot of the agreement (OCR).")
    group.add_argument("-s", "--screenshot", action="store_true",
                        help="Capture the active screen and scan it (OCR).")
    parser.add_argument("--lang", default="rus+eng", help="OCR language(s), default: rus+eng")
    parser.add_argument("--json", action="store_true", help="Output findings as JSON instead of colored text.")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.text:
            with open(args.text, "r", encoding="utf-8") as f:
                text = f.read()
        elif args.image:
            text = extract_text(args.image, lang=args.lang)
        else:
            text = extract_text_from_screenshot(lang=args.lang)
    except Exception as e:
        print(f"{RED}Error reading input: {e}{RESET}", file=sys.stderr)
        sys.exit(2)

    findings = analyze_text(text)

    if args.json:
        import json
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        print("=" * 60)
        print("Agreement Analyzer")
        print("=" * 60)
        print_findings(findings)

    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
