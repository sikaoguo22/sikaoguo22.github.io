"""Offline regression tests. Run after scripts/build.py; no packages required."""
from __future__ import annotations
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'

class Document(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.ids=set();self.duplicate_ids=[];self.links=[];self.images=[]
        self.h1=0;self.title=0;self.descriptions=0;self.canonicals=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):
            if a['id'] in self.ids:self.duplicate_ids.append(a['id'])
            self.ids.add(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='title':self.title+=1
        if tag=='meta' and a.get('name')=='description':self.descriptions+=1
        if tag=='link' and a.get('rel')=='canonical':self.canonicals.append(a['href'])
        if tag=='img':self.images.append(a)
        if tag=='img' and a.get('srcset'):
            for candidate in a['srcset'].split(','):
                self.links.append((tag,'srcset',candidate.strip().split()[0]))
        for key in ('href','src'):
            if a.get(key):self.links.append((tag,key,a[key]))

class WebsiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files=sorted(SITE.rglob('*.html'))
        if not cls.files:raise AssertionError('Build the website first: python3 scripts/build.py')
        cls.docs={p:Document(p.read_text()) for p in cls.files}
        cls.prefix=urlsplit(cls.docs[SITE/'index.html'].canonicals[0]).path.rstrip('/')
    def test_heading_metadata_and_unique_ids(self):
        for path,doc in self.docs.items():
            with self.subTest(page=str(path)):
                self.assertEqual(doc.h1,1);self.assertEqual(doc.title,1)
                self.assertEqual(doc.descriptions,1);self.assertEqual(len(doc.canonicals),1)
                self.assertFalse(doc.duplicate_ids)
    def test_local_links_and_fragments(self):
        for path,doc in self.docs.items():
            for tag,key,value in doc.links:
                url=urlsplit(value)
                if url.scheme or url.netloc:continue
                target=unquote(url.path)
                if not target:dest=path
                elif target.startswith('/'):
                    if self.prefix:
                        self.assertTrue(target.startswith(self.prefix+'/'),value)
                        target=target[len(self.prefix):]
                    dest=SITE/target.lstrip('/')
                else:dest=path.parent/target
                if dest.is_dir():dest=dest/'index.html'
                with self.subTest(page=str(path.relative_to(SITE)),link=value):
                    self.assertTrue(dest.is_file(),f'Broken local link: {value}')
                    if url.fragment and dest.suffix=='.html':
                        self.assertIn(unquote(url.fragment),self.docs.get(dest,Document(dest.read_text())).ids)
    def test_images_have_alt_and_dimensions(self):
        for path,doc in self.docs.items():
            for image in doc.images:
                with self.subTest(page=str(path)):
                    self.assertTrue(image.get('alt'));self.assertTrue(image.get('width'));self.assertTrue(image.get('height'))
    def test_assets_and_cv_without_downloads(self):
        self.assertFalse(list((ROOT/'src/assets').glob('*.pdf')))
        self.assertFalse(list((SITE/'assets').glob('*.pdf')))
        self.assertNotIn(' download',(SITE/'cv/index.html').read_text())
        self.assertTrue((SITE/'assets/social-card.png').is_file())
        self.assertLess((SITE/'assets/sikao-guo-480.webp').stat().st_size,70000)
    def test_publication_fidelity(self):
        pubs=json.loads((ROOT/'content/publications.json').read_text())
        html=(SITE/'publications/index.html').read_text()
        self.assertEqual(sum(p['type']=='Preprint' for p in pubs),2)
        self.assertFalse(next(p for p in pubs if p['id']=='ionerdss-2026')['firstAuthor'])
        self.assertEqual(html.count('data-publication data-type='),len(pubs))
        for pub in pubs:self.assertTrue((SITE/'citations'/f'{pub["id"]}.bib').is_file())
    def test_no_external_runtime_dependencies(self):
        for path,doc in self.docs.items():
            for tag,key,value in doc.links:
                if tag in ('script','img') and key=='src':
                    self.assertFalse(urlsplit(value).scheme,f'External runtime dependency in {path}: {value}')
    def test_self_hosted_font(self):
        font=SITE/'assets/fonts/ibm-plex-mono-latin-400-normal.woff2'
        self.assertTrue(font.is_file())
        self.assertEqual(font.read_bytes()[:4],b'wOF2')
        self.assertIn('SIL OPEN FONT LICENSE',(SITE/'assets/fonts/OFL.txt').read_text().upper())
        css=(SITE/'assets/styles.css').read_text()
        self.assertIn('@font-face',css)
        self.assertIn('"IBM Plex Mono"',css)
        self.assertNotRegex(css,r'url\(\s*["\']?(https?:)?//')
        self.assertIn('rel="preload"',(SITE/'index.html').read_text())
    def test_single_weight_and_token_contrast(self):
        css=(SITE/'assets/styles.css').read_text()
        self.assertEqual(set(re.findall(r'font-weight:\s*([^;}]+)',css)),{'400'})
        block=re.search(r':root\s*\{([^}]*)\}',css).group(1)
        theme=dict(re.findall(r'--([\w-]+):\s*(#[0-9a-fA-F]{6})',block))
        def luminance(hex_):
            channels=[int(hex_[i:i+2],16)/255 for i in (1,3,5)]
            channels=[c/12.92 if c<=.03928 else ((c+.055)/1.055)**2.4 for c in channels]
            return .2126*channels[0]+.7152*channels[1]+.0722*channels[2]
        def contrast(a,b):
            hi,lo=sorted((luminance(a),luminance(b)),reverse=True)
            return (hi+.05)/(lo+.05)
        for fg in ('ink','muted','accent','warm'):
            for bg in ('bg','surface'):
                with self.subTest(token=fg,background=bg):
                    self.assertGreaterEqual(contrast(theme[fg],theme[bg]),4.5)
    def test_cv_matches_source(self):
        cv=(SITE/'cv/index.html').read_text()
        pubs=json.loads((ROOT/'content/publications.json').read_text())
        self.assertEqual(len(pubs),20)
        self.assertEqual(cv.count('<li><span>'),21)
        for text in ('Frédéric Cazals','Margaret E. Johnson','Ping Xie','Gordon Research Conference'):
            self.assertIn(text,cv)
        self.assertNotIn('443',cv)
        self.assertTrue((SITE/'citations/publications.bib').is_file())
        self.assertEqual((SITE/'citations/publications.bib').read_text().count('@'),20)
    def test_pages_and_navigation(self):
        self.assertEqual(sorted(str(p.relative_to(SITE)) for p in self.files),['404.html','cv/index.html','index.html','publications/index.html'])
        home=(SITE/'index.html').read_text()
        nav=re.search(r'<nav class="primary-nav".*?</nav>',home,re.S).group(0)
        self.assertEqual(re.findall(r'>([^<]+)</a>',nav),['Home','Publications','CV'])
    def test_homepage_sections(self):
        home=(SITE/'index.html').read_text()
        self.assertEqual(re.findall(r'<span class="section-number">\d+</span><h2>([^<]+)</h2>',home),['Short Bio','Selected Publications','Contact'])
        self.assertIn('Algorithms–Biology–Structure (ABS) team',home)
        self.assertNotIn('team.inria.fr/abs',home)
    def test_cv_and_publications_sections(self):
        cv=(SITE/'cv/index.html').read_text()
        self.assertNotIn('Teaching, Mentoring',cv)
        self.assertNotIn('My name is underlined',(SITE/'publications/index.html').read_text())


if __name__=='__main__':unittest.main()
