#!/usr/bin/env python3
"""
Verification script for Writing Letters with AI project.
Checks: LICENSE copyright, README credit, HTML validity, links, file existence.
"""
import os
import sys
import re
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).parent

class LinkChecker(HTMLParser):
    def __init__(self, base_path):
        super().__init__()
        self.base_path = base_path
        self.links = []
        self.errors = []
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href':
                    self.links.append((self.getpos(), value))
        elif tag == 'link':
            for attr, value in attrs:
                if attr == 'href':
                    self.links.append((self.getpos(), value))

def check_license():
    """Verify LICENSE has exact copyright line."""
    license_path = ROOT / 'LICENSE'
    if not license_path.exists():
        return False, "LICENSE file missing"
    content = license_path.read_text()
    expected = "Copyright (c) 2026 Asdale Dynamics, LLC"
    if expected not in content:
        return False, f"LICENSE missing exact copyright line: '{expected}'"
    return True, "LICENSE copyright line verified"

def check_readme():
    """Verify README credits Asdale Dynamics, LLC."""
    readme_path = ROOT / 'README.md'
    if not readme_path.exists():
        return False, "README.md missing"
    content = readme_path.read_text()
    if "Asdale Dynamics, LLC" not in content:
        return False, "README.md does not credit Asdale Dynamics, LLC"
    return True, "README credits Asdale Dynamics, LLC"

def check_html_files():
    """Check all HTML files for basic validity and link resolution."""
    html_files = list(ROOT.rglob('*.html'))
    if not html_files:
        return False, "No HTML files found"
    
    errors = []
    checked = 0
    
    for html_file in html_files:
        checked += 1
        try:
            content = html_file.read_text(encoding='utf-8')
        except Exception as e:
            errors.append(f"{html_file}: failed to read - {e}")
            continue
        
        # Basic HTML structure checks
        if not content.strip().startswith('<!DOCTYPE html>'):
            errors.append(f"{html_file}: missing DOCTYPE declaration")
        if '<html' not in content.lower():
            errors.append(f"{html_file}: missing <html> tag")
        if '<head>' not in content.lower():
            errors.append(f"{html_file}: missing <head> tag")
        if '<body>' not in content.lower():
            errors.append(f"{html_file}: missing <body> tag")
        
        # Check links
        parser = LinkChecker(html_file.parent)
        parser.feed(content)
        for (line, col), href in parser.links:
            if href.startswith(('http://', 'https://', 'mailto:')):
                continue  # external links
            if href.startswith('#'):
                continue  # fragment
            # Resolve relative to file
            target = (html_file.parent / href).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{html_file}:{line}: link '{href}' escapes project root")
                continue
            if not target.exists():
                errors.append(f"{html_file}:{line}: broken link '{href}' -> {target}")
    
    if errors:
        return False, f"HTML checks failed ({len(errors)} errors):\n" + "\n".join(errors[:20])
    return True, f"All {checked} HTML files valid and links resolve"

def check_referenced_files():
    """Check that all files referenced in markdown/HTML exist."""
    errors = []
    
    # Check markdown files for references
    md_files = list((ROOT / 'docs').rglob('*.md'))
    for md_file in md_files:
        content = md_file.read_text()
        # Find relative paths in markdown links and code references
        refs = re.findall(r'[`"\'](\.\.[/`\w\-\.]+)[`"\']', content)
        refs += re.findall(r'\]\((\.\.[^)]+)\)', content)
        for ref in refs:
            target = (md_file.parent / ref).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                continue
            if not target.exists():
                errors.append(f"{md_file}: referenced file not found: {ref}")
    
    # Check templates referenced in manual
    expected_templates = [
        'templates/complaint-template.md',
        'templates/appeal-template.md',
        'templates/thank-you-template.md',
        'templates/request-template.md',
    ]
    for t in expected_templates:
        if not (ROOT / t).exists():
            errors.append(f"Missing template: {t}")
    
    # Check printable templates
    expected_printable = [
        'templates/printable/printable-complaint.html',
        'templates/printable/printable-appeal.html',
        'templates/printable/printable-thank-you.html',
        'templates/printable/printable-request.html',
    ]
    for t in expected_printable:
        if not (ROOT / t).exists():
            errors.append(f"Missing printable template: {t}")
    
    if errors:
        return False, "Referenced files missing:\n" + "\n".join(errors)
    return True, "All referenced files exist"

def check_print_css():
    """Verify print.css exists and has @page rule."""
    css_path = ROOT / 'site' / 'css' / 'print.css'
    if not css_path.exists():
        return False, "site/css/print.css missing"
    content = css_path.read_text()
    if '@page' not in content:
        return False, "print.css missing @page rule"
    return True, "print.css has @page rule"

def check_structure():
    """Verify expected directory structure."""
    required_dirs = [
        'docs/manual',
        'templates/printable',
        'site/css',
    ]
    errors = []
    for d in required_dirs:
        if not (ROOT / d).exists():
            errors.append(f"Missing directory: {d}")
    if errors:
        return False, "Structure issues:\n" + "\n".join(errors)
    return True, "Directory structure verified"

def check_manual_completeness():
    """Verify all manual chapters exist."""
    expected_chapters = [
        'docs/manual/index.md',
        'docs/manual/intro.md',
        'docs/manual/tone-guidance.md',
        'docs/manual/what-never-to-include.md',
        'docs/manual/complaints.md',
        'docs/manual/appeals.md',
        'docs/manual/thank-you-notes.md',
        'docs/manual/requests.md',
        'docs/manual/ai-prompts.md',
    ]
    errors = []
    for chap in expected_chapters:
        if not (ROOT / chap).exists():
            errors.append(f"Missing chapter: {chap}")
    if errors:
        return False, "Manual incomplete:\n" + "\n".join(errors)
    return True, "All 9 manual chapters present"

def main():
    print("=" * 60)
    print("Writing Letters with AI — Verification")
    print("=" * 60)
    
    checks = [
        ("LICENSE copyright", check_license),
        ("README credit", check_readme),
        ("Directory structure", check_structure),
        ("Manual completeness", check_manual_completeness),
        ("Referenced files", check_referenced_files),
        ("Print CSS", check_print_css),
        ("HTML files & links", check_html_files),
    ]
    
    passed = 0
    failed = 0
    
    for name, check_fn in checks:
        print(f"\n[{name}]")
        ok, msg = check_fn()
        if ok:
            print(f"  ✓ PASS: {msg}")
            passed += 1
        else:
            print(f"  ✗ FAIL: {msg}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())