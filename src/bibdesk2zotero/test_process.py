import bibtexparser
import pytest

from . import process as m


def test_is_text_field():
    assert m.is_text_field('title')
    assert m.is_text_field('Title')
    assert m.is_text_field('author')
    assert m.is_text_field('shorttitle')
    assert m.is_text_field('abstract')
    assert not m.is_text_field('bdsk-file-1')
    assert not m.is_text_field('bdsk-url-2')
    assert not m.is_text_field('url')
    assert not m.is_text_field('Url')
    assert not m.is_text_field('ID')
    assert not m.is_text_field('ENTRYTYPE')


@pytest.fixture
def bibtex_with_existing_file():
    return r'''\
@article{Perez-Escudero2014,
    author = "P{\'{e}}rez-Escudero, Alfonso and Vicente-Page, Juli{\'{a}}n and Hinz, Robert C and Arganda, Sara and de Polavieja, Gonzalo G",
    date-modified = "2023-12-10 17:54:18 +0800",
    file = ":/Library/Application Support/Mendeley Desktop/Downloaded/P{\'{e}}rez-Escudero et al. - 2014 - idTracker tracking individuals in a group by automatic identification of unmarked animals.pdf:pdf",
    journal = "Nature Methods",
    month = "jun",
    pages = "743",
    publisher = "Nature Publishing Group, a division of Macmillan Publishers Limited. All Rights Reserved.",
    title = "idTracker: tracking individuals in a group by automatic identification of unmarked animals",
    url = "http://dx.doi.org/10.1038/nmeth.2994 http://10.0.4.14/nmeth.2994 https://www.nature.com/articles/nmeth.2994{\\#}supplementary-information",
    volume = "11",
    year = "2014",
    bdsk-url-1 = "http://dx.doi.org/10.1038/nmeth.2994\%20http://10.0.4.14/nmeth.2994\%20https://www.nature.com/articles/nmeth.2994\%7B\%5C\#\%7Dsupplementary-information",
}'''


@pytest.fixture
def bibtex_with_messy_text_field():
    return r'''\
@article{besold_neural-symbolic_2017,
    author = "Besold, Tarek R and d'Avila Garcez, Artur and Bader, Sebastian and Bowman, Howard and Domingos, Pedro and Hitzler, Pascal and Kuehnberger, Kai-Uwe and Lamb, Luis C and Lowd, Daniel and Lima, Priscila Machado Vieira and de Penning, Leo and Pinkas, Gadi and Poon, Hoifung and Zaverucha, Gerson",
    annote = "arXiv: 1711.03902",
    date-modified = "2023-12-10 16:51:09 +0800",
    journal = "arXiv:1711.03902 [cs]",
    keywords = "Computer Science - Artificial Intelligence",
    month = "nov",
    shorttitle = "Neural-{\{}Symbolic{\}} {\{}Learning{\}} and {\{}Reasoning{\}}",
    title = "Neural-Symbolic Learning and Reasoning: A Survey and Interpretation",
    year = "2017",
    bdsk-url-1 = "http://arxiv.org/abs/1711.03902"
}'''


class TestProcessor:
    def test_without_do_strip_existing_file(self, bibtex_with_existing_file):
        parser = bibtexparser.bparser.BibTexParser()
        db = bibtexparser.loads(bibtex_with_existing_file, parser)
        assert len(db.entries) == 1
        assert set(db.entries[0]).issuperset([
            'author', 'date-modified', 'file', 'journal', 'month', 'pages',
            'publisher', 'title', 'url', 'volume', 'year', 'bdsk-url-1'
        ])

    def test_with_do_strip_existing_file1(self, bibtex_with_existing_file):
        parser = bibtexparser.bparser.BibTexParser()
        proc = m.Processor(basedir='/path/to/papers', strip_existing_file=True)
        parser.customization = proc.do_strip_existing_file
        assert not proc.modified
        db = bibtexparser.loads(bibtex_with_existing_file, parser)
        assert proc.modified
        assert len(db.entries) == 1
        assert set(db.entries[0]).issuperset([
            'author', 'date-modified', 'journal', 'month', 'pages',
            'publisher', 'title', 'url', 'volume', 'year', 'bdsk-url-1'
        ])
        assert 'file' not in set(db.entries[0])

    def test_with_do_strip_existing_file2(self, bibtex_with_messy_text_field):
        parser = bibtexparser.bparser.BibTexParser()
        proc = m.Processor(basedir='/path/to/papers', strip_existing_file=True)
        parser.customization = proc.do_strip_existing_file
        assert not proc.modified
        db = bibtexparser.loads(bibtex_with_messy_text_field, parser)
        assert not proc.modified
        assert len(db.entries) == 1
        assert set(db.entries[0]).issuperset([
            'author', 'annote', 'date-modified', 'journal', 'keywords',
            'month', 'shorttitle', 'title', 'year', 'bdsk-url-1'
        ])

    def test_without_do_cleanup_messy_brackets(
        self,
        bibtex_with_messy_text_field,
    ):
        parser = bibtexparser.bparser.BibTexParser()
        db = bibtexparser.loads(bibtex_with_messy_text_field, parser)
        assert len(db.entries) == 1
        assert (
            db.entries[0]['shorttitle'] ==
            r'Neural-{\{}Symbolic{\}} {\{}Learning{\}} and {\{}Reasoning{\}}')

    def test_with_do_cleanup_messy_brackets1(
        self,
        bibtex_with_messy_text_field,
    ):
        parser = bibtexparser.bparser.BibTexParser()
        proc = m.Processor(basedir='/path/to/papers', strip_existing_file=True)
        parser.customization = proc.do_cleanup_messy_brackets
        assert not proc.modified
        db = bibtexparser.loads(bibtex_with_messy_text_field, parser)
        assert proc.modified
        assert len(db.entries) == 1
        assert (db.entries[0]['shorttitle'] ==
                'Neural-Symbolic Learning and Reasoning')

    def test_with_do_cleanup_messy_brackets2(self, bibtex_with_existing_file):
        parser = bibtexparser.bparser.BibTexParser()
        proc = m.Processor(basedir='/path/to/papers', strip_existing_file=True)
        parser.customization = proc.do_cleanup_messy_brackets
        assert not proc.modified
        db = bibtexparser.loads(bibtex_with_existing_file, parser)
        assert not proc.modified
        assert len(db.entries) == 1
        assert (
            db.entries[0]['author'] ==
            r'P{\'{e}}rez-Escudero, Alfonso and Vicente-Page, Juli{\'{a}}n and Hinz, Robert C and Arganda, Sara and de Polavieja, Gonzalo G'
        )
