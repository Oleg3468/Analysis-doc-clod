
#!/usr/bin/env python3
"""
Developer utility: run the analyzer on a text file and print findings as
structured JSON, for integration with other tools/APIs.

Usage: python3 run_analyzer_json.py path/to/agreement.txt
"""
import json
import sys

from analyzer import analyze_text


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 run_analyzer_json.py <path_to_text_file>", file=sys.stderr)
        sys.exit(2)

    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    findings = analyze_text(text)
    print(json.dumps({"findings": findings, "count": len(findings)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
