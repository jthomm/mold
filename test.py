import unittest
from mold import FieldSourceError, FieldDataTypeError, FieldMold, RowMold, SQLiteField, SQLiteRow



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



class TestRowMold(unittest.TestCase):

    def test_row_mold(self):
        configs = [{'source': 'amount', 'default': 0,},
                   {'source': 'name', 'none': '-',},]
        row_mold = RowMold(configs)
        dct = {'name': '-',}
        self.assertEqual(row_mold(dct), {'amount': 0, 'name': None,})



class TestSQLiteField(unittest.TestCase):

    def test_insert_data_type_default(self):
        config = {'source': 'amount',}
        sqlite_field = SQLiteField(FieldMold(config))
        self.assertEqual(sqlite_field.declaration, 'amount TEXT')

    def test_insert_data_type_unicode(self):
        config = {'source': 'amount', 'type': 'unicode'}
        sqlite_field = SQLiteField(FieldMold(config))
        self.assertEqual(sqlite_field.declaration, 'amount TEXT')

    def test_insert_data_type_str(self):
        config = {'source': 'amount', 'type': 'str'}
        sqlite_field = SQLiteField(FieldMold(config))
        self.assertEqual(sqlite_field.declaration, 'amount TEXT')

    def test_insert_data_type_int(self):
        config = {'source': 'amount', 'type': 'int'}
        sqlite_field = SQLiteField(FieldMold(config))
        self.assertEqual(sqlite_field.declaration, 'amount INTEGER')

    def test_insert_data_type_float(self):
        config = {'source': 'amount', 'type': 'float'}
        sqlite_field = SQLiteField(FieldMold(config))
        self.assertEqual(sqlite_field.declaration, 'amount REAL')



class TestSQLiteRow(unittest.TestCase):

    def test_create_table_sql(self):
        configs = [{'source': 'First',},
                   {'source': 'Last', 'type': 'unicode',},
                   {'source': 'Age', 'type': 'int',},
                   {'source': 'Amt', 'target': 'amount', 'type': 'float',},]
        sqlite_row = SQLiteRow(RowMold(configs))
        self.assertEqual(
            sqlite_row.create_table_sql('test'),
            'CREATE TABLE test (first TEXT, last TEXT, age INTEGER, amount REAL)')

    def test_insert_into_table_sql(self):
        configs = [{'source': 'First',},
                   {'source': 'Last', 'type': 'unicode',},
                   {'source': 'Age', 'type': 'int',},
                   {'source': 'Amt', 'target': 'amount', 'type': 'float',},]
        sqlite_row = SQLiteRow(RowMold(configs))
        self.assertEqual(
            sqlite_row.insert_into_table_sql('test'),
            'INSERT INTO test (first, last, age, amount) VALUES (?, ?, ?, ?)')




if __name__ == '__main__':
    unittest.main()
