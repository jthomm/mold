import unittest
from mold import FieldSourceError, FieldDataTypeError, FieldMold

class TestFieldMold(unittest.TestCase):

    def test_missing_source(self):
        config = {}
        field_mold = FieldMold(config)
        dct = {}
        self.assertRaises(FieldSourceError, lambda: field_mold(dct))

    def test_target(self):
        config = {'source': 'amount', 'target': 'amt',}
        field_mold = FieldMold(config)
        dct = {}
        self.assertEqual(field_mold(dct)[0], 'amt')

    def test_target_defaults_to_lower_source(self):
        config = {'source': 'Amount',}
        field_mold = FieldMold(config)
        dct = {}
        self.assertEqual(field_mold(dct)[0], 'amount')

    def test_none(self):
        config = {'source': 'amount', 'none': '-',}
        field_mold = FieldMold(config)
        dct = {'amount': '-',}
        self.assertIsNone(field_mold(dct)[1])

    def test_none_defaults_to_empty_string(self):
        config = {'source': 'amount',}
        field_mold = FieldMold(config)
        dct = {'amount': '',}
        self.assertIsNone(field_mold(dct)[1])

    def test_default(self):
        config = {'source': 'amount', 'default': 0,}
        field_mold = FieldMold(config)
        dct = {}
        self.assertEqual(field_mold(dct)[1], 0)

    def test_rstrip(self):
        config = {'source': 'amount', 'rstrip': ' dollars',}
        field_mold = FieldMold(config)
        dct = {'amount': '100 dollars',}
        self.assertEqual(field_mold(dct)[1], '100')

    def test_lstrip(self):
        config = {'source': 'amount', 'lstrip': '$',}
        field_mold = FieldMold(config)
        dct = {'amount': '$100',}
        self.assertEqual(field_mold(dct)[1], '100')

    def test_invalid_data_type(self):
        config = {'source': 'amount','type': int,}
        field_mold = FieldMold(config)
        dct = {'amount': 100,}
        self.assertRaises(FieldDataTypeError, lambda: field_mold(dct))

    def test_data_type_defaults_to_unicode(self):
        config = {'source': 'amount',}
        field_mold = FieldMold(config)
        dct = {'amount': 100,}
        self.assertEqual(field_mold(dct)[1], u'100')

    def test_data_type(self):
        config = {'source': 'amount', 'type': 'int'}
        field_mold = FieldMold(config)
        dct = {'amount': '100',}
        self.assertEqual(field_mold(dct)[1], 100)

    def test_precedence_default(self):
        config = {'source': 'amount', 'none': '-', 'default': 0,}
        field_mold = FieldMold(config)
        dct = {}
        self.assertEqual(field_mold(dct)[1], 0)

    def test_precedence_none(self):
        config = {'source': 'amount', 'none': '-', 'default': 0,}
        field_mold = FieldMold(config)
        dct = {'amount': '-'}
        self.assertIsNone(field_mold(dct)[1])

if __name__ == '__main__':
    unittest.main()
