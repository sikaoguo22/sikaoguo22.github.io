"""Offline regression tests. Run after scripts/build.py; no packages required."""
from __future__ import annotations
import json
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
    def test_page_count_and_legacy_routes(self):
        self.assertEqual(len(self.files),12)
        for route in ('research','projects','software','publications','about','cv',
                      'projects/cross-platform-gui-generation','projects/inverse-kinematics-backbone-sampling',
                      'projects/nerdss-ionerdss-infrastructure','projects/mechanistic-assembly-models'):
            self.assertTrue((SITE/route/'index.html').is_file(),route)
        for fragment in ('current-research','biomolecular-assembly','research-infrastructure','research-software'):
            self.assertIn(fragment,self.docs[SITE/'projects/index.html'].ids)
        projects=json.loads((ROOT/'content/projects.json').read_text())
        for project in projects:
            ids=self.docs[SITE/'projects'/project['slug']/'index.html'].ids
            for fragment in ('context','approach','contribution','outcomes'):
                self.assertIn(fragment,ids,project['slug'])
            if project['links']:self.assertIn('resources',ids,project['slug'])
            if project['relatedPublications']:self.assertIn('publications',ids,project['slug'])
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
    def test_project_illustrations(self):
        cases={
            'inverse-kinematics-backbone-sampling':'protein-sampling',
            'mechanistic-assembly-models':'assembly',
            'nerdss-ionerdss-infrastructure':'nerdss',
            'cross-platform-gui-generation':'gui-generator',
        }
        expected={
            'index.html':['gui-generator','nerdss','nerdss'],
            'research/index.html':['protein-sampling','assembly'],
            'software/index.html':['gui-generator','nerdss','nerdss'],
            'projects/index.html':['protein-sampling','nerdss','gui-generator','assembly'],
            **{f'projects/{slug}/index.html':[name] for slug,name in cases.items()},
        }
        for route,names in expected.items():
            images=[image for image in self.docs[SITE/route].images if '/images/' in image['src']]
            with self.subTest(page=route):
                self.assertEqual([Path(image['src']).name for image in images],[f'{name}-800.webp' for name in names])
                for image,name in zip(images,names):
                    self.assertIn(f'{name}-1448.webp 1448w',image['srcset'])
                    self.assertEqual((image['width'],image['height']),('1448','1086'))
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
    def test_ongoing_work_and_benchmark_scope(self):
        home=(SITE/'index.html').read_text()
        self.assertIn('20,000-particle benchmark',home)
        self.assertIn('96 CPUs',home)
        ongoing=(SITE/'projects/inverse-kinematics-backbone-sampling/index.html').read_text()
        self.assertIn('evaluated systems',ongoing)
        self.assertIn('Ongoing research',ongoing)
        self.assertNotIn('healthier tomorrow',home.lower())

if __name__=='__main__':unittest.main()
