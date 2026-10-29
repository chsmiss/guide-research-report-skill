"""Structural regression checks for the compact skill package; not research quality tests."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SkillStructureTests(unittest.TestCase):
    def test_metadata_and_main_entry(self):
        skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(skill.startswith('---\n'))
        self.assertIn('name: guided-research-report', skill)
        self.assertRegex(skill, r'version: "[0-9]+\.[0-9]+\.[0-9]+"')
        self.assertIn('references/editorial-design.md', skill)

    def test_local_markdown_links_resolve(self):
        broken=[]
        for p in [ROOT/'SKILL.md', ROOT/'README.md', *sorted((ROOT/'references').glob('*.md'))]:
            text=p.read_text(encoding='utf-8')
            for target in re.findall(r'\]\(([^)]+)\)',text):
                if target.startswith(('http://','https://','mailto:','#')): continue
                rel=target.split('#')[0]
                if not rel: continue
                if not (p.parent / rel).is_file(): broken.append(f'{p.relative_to(ROOT)} -> {target}')
        self.assertFalse(broken, '\n'.join(broken))

    def test_merged_editing_reference_and_legacy_scripts(self):
        self.assertTrue((ROOT/'references/editorial-design.md').exists())
        for old in ('report-writing.md','narrative-and-latex.md','delivery-quality.md'):
            self.assertFalse((ROOT/'references'/old).exists())
        for fname in ('check_research_pack.py','build_decision_brief.py','repair_gb1_unicode.py'):
            self.assertTrue((ROOT/'scripts'/fname).is_file())

    def test_story_and_visual_check_are_explicit(self):
        e=(ROOT/'references/editorial-design.md').read_text(encoding='utf-8')
        for term in ('section dependency map','Reverse-outline','Reader comprehension','Visual QA','reader','读者'):
            self.assertIn(term.lower(),e.lower())
        self.assertTrue((ROOT/'assets/research-layout.sty').exists())

if __name__ == '__main__': unittest.main()
