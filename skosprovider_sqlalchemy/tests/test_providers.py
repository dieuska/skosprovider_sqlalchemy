# -*- coding: utf-8 -*-

try:
    import unittest2 as unittest
except ImportError:  # pragma NO COVER
    import unittest  # noqa

from skosprovider_sqlalchemy.providers import (
    SQLAlchemyProvider
)

from skosprovider.skos import (
    Concept,
    Collection
)

from . import engine
from sqlalchemy.orm import sessionmaker

class SQLAlchemyProviderTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = engine

    def setUp(self):
        connection = self.engine.connect()
        self.trans = connection.begin()

        # Setting up SQLAlchemy
        from skosprovider_sqlalchemy.models import Base
        Base.metadata.bind = engine
        sm = sessionmaker(bind=engine)
        self.session= sm()

        # Set up testdata
        self._create_test_data()

        # Set up provider
        self.provider = SQLAlchemyProvider(
            {'id': 'SOORTEN', 'conceptscheme_id': 1},
            self.session
        )

    def tearDown(self):
        self.session.close()
        self.trans.rollback()

    def _create_test_data(self):
        from ..models import (
            Concept, 
            ConceptScheme, 
            Collection,
            Label,
            Note,
            Language
        )
        cs = ConceptScheme(
            id = 1
        )
        self.session.add(cs)
        con = Concept(
            id = 1,
            conceptscheme=cs
        )
        self.session.add(con)
        l = Label('prefLabel','en','Churches')
        con.labels.append(l)
        l = Label('prefLabel','nl','kerken')
        con.labels.append(l)
        col = Collection(
            id = 2,
            conceptscheme=cs
        )
        l = Label('prefLabel','en','Churches by function')
        col.labels.append(l)
        self.session.add(col)
        self.session.flush()

    def test_get_vocabulary_id(self):
        self.assertEquals('SOORTEN', self.provider.get_vocabulary_id())

    def test_get_concept_by_id(self):
        con = self.provider.get_by_id(1)
        self.assertIsInstance(con, Concept)
        self.assertEquals(1, con.id)

    def test_get_collection_by_id(self):
        col = self.provider.get_by_id(2)
        self.assertIsInstance(col, Collection)
        self.assertEquals(2, col.id)

    def test_get_all(self):
        all = self.provider.get_all()
        self.assertEquals(2, len(all))
        self.assertIn({'id': 1, 'label': 'Churches'}, all)
        self.assertIn({'id': 2, 'label': 'Churches by function'}, all)

    def test_find_all(self):
        all = self.provider.find({})
        self.assertEquals(2, len(all))
        self.assertIn({'id': 1, 'label': 'Churches'}, all)
        self.assertIn({'id': 2, 'label': 'Churches by function'}, all)

    def test_find_type_all(self):
        all = self.provider.find({'type': 'all'})
        self.assertEquals(2, len(all))
        self.assertIn({'id': 1, 'label': 'Churches'}, all)
        self.assertIn({'id': 2, 'label': 'Churches by function'}, all)

    def test_find_type_concept(self):
        all = self.provider.find({'type': 'concept'})
        self.assertEquals(1, len(all))
        self.assertIn({'id': 1, 'label': 'Churches'}, all)

    def test_find_type_collection(self):
        all = self.provider.find({'type': 'collection'})
        self.assertEquals(1, len(all))
        self.assertIn({'id': 2, 'label': 'Churches by function'}, all)

    def test_find_label_kerken(self):
        all = self.provider.find({'label': 'kerken'})
        self.assertEquals(1, len(all))
        self.assertIn({'id': 1, 'label': 'Churches'}, all)

    def test_find_label_churches_type_concept(self):
        all = self.provider.find({'label': 'churches', 'type': 'concept'})
        self.assertEquals(1, len(all))
        self.assertIn({'id': 1, 'label': 'Churches'}, all)

    def test_expand_concept(self):
        ids = self.provider.expand_concept(1)
        self.assertEquals([1], ids)
