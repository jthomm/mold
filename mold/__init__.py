from collections import OrderedDict



"""Mapping between valid values configured under `type` and data type."""
DATA_TYPE = {
    'unicode': unicode,
    'str': str,
    'int': int,
    'float': float,
}

"""Type to be used if `type` is not configured."""
DEFAULT_DATA_TYPE_NAME = 'unicode'



class FieldSourceError(Exception):
    """Raise this when `source` is not configured for a field."""
    pass

class FieldDataTypeError(Exception):
    """Raise this when the data type is not configured for a field."""
    pass


"""Singleton value to signify that an attribute was not configured.  Used in 
place of the less specific `None`."""
NotConfigured = object()



class FieldMold(object):
    """This class operates on a single field in the data."""

    def __init__(self, config):
        """`config` is expected to behave like a dictionary."""
        self.config = config

    @property
    def source(self):
        """Name of the key from the source dictionary."""
        try:
            return self.config['source']
        except KeyError:
            raise FieldSourceError(
                'Field config does not specify a `source` key.')

    @property
    def target(self):
        """By default, `FieldMold` will use the lowercase of the source key 
        as the key in the target dictionary (or the column name in the 
        database table).  The user can specify a different name by setting a 
        value for 'target' in the config."""
        return self.config.get('target', self.source.lower())

    @property
    def none(self):
        """Default behavior is to replace empty strings in the source with 
        `None` in the target.  The user can override this behavior by setting 
        a value for `none` in the config."""
        return self.config.get('none', '')

    @property
    def default(self):
        """If the target key is not found in the target dictionary, use 
        the value specified in the config (or `None` if `default` is not 
        specified)."""
        return self.config.get('default', None)

    @property
    def rstrip(self):
        """Value to be stripped off of the right side of the source string.  
        (This occurs before type conversion.)"""
        return self.config.get('rstrip', NotConfigured)

    @property
    def lstrip(self):
        """Value to be stripped off of the left side of the source string.  
        (This occurs before type conversion.)"""
        return self.config.get('lstrip', NotConfigured)

    @property
    def data_type_name(self):
        """Shorthand for the data type into which the source value should 
        be converted.  This library must define a mapping between valid 
        values and Python data types (or SQLite data types, etc.)."""
        return self.config.get('type', DEFAULT_DATA_TYPE_NAME)

    @property
    def data_type(self):
        """The Python data type mapped to the data type name specified in 
        the config."""
        try:
            return DATA_TYPE[self.data_type_name]
        except KeyError:
            raise FieldDataTypeError(
                'Field config contains an invalid value for `type`')

    def target_value(self, dct):
        """Produces the target value from the source dictionary based on the 
        config properties provided during instantiation."""
        try:
            value = dct[self.source]
        except KeyError:
            # First condition occurs if the configured source key is not in 
            # the dictionary; no further manipulation/conversion takes place.
            return self.default
        else:
            # Second condition occurs if the value matches the one configured 
            # as `none`; no further manipulation/conversion necessary.
            if value == self.none:
                return None
            # Majority of cases should find their way here.  Source key is 
            # in the dictionary and the value does not match `none`.  All 
            # further manipulation/conversion occurs.
            else:
                if self.rstrip is not NotConfigured:
                    value = value.rstrip(self.rstrip)
                if self.lstrip is not NotConfigured:
                    value = value.lstrip(self.lstrip)
                # Finally, after string manipulation (currently just strip), 
                # data type conversion:
                value = self.data_type(value)
                return value

    def __call__(self, dct):
        """Produces a key/value tuple which, among others, will eventually 
        constitute an entire dictionary."""
        return (self.target, self.target_value(dct),)



class RowMold(tuple):
    """This class operates on a single row (multiple fields) in the data."""

    def __new__(cls, configs):
        """`configs` is expected to behave like a list of dictionaries."""
        return super(RowMold, cls).__new__(cls, map(FieldMold, configs))

    def __call__(self, dct):
        """Produces a dictionary that includes all and only fields listed in 
        the configuration passed to this class.  Values are transformed 
        according to the config for each field."""
        return OrderedDict(field_mold(dct) for field_mold in self)



class DatabaseFieldABC(object):
    """Abstract base class for supporting database operations on a single 
    field."""

    def __init__(self, field_mold):
        self.field_mold = field_mold

    @property
    def column(self):
        """Reuse the `target` method from `FieldMold` class."""
        return self.field_mold.target

    @property
    def data_type(self):
        raise NotImplementedError(
            '`data_type` method not implemented for this class')

    @property
    def declaration(self):
        """E.g. "amount INT" in SQLite..."""
        return '{column} {data_type}'.format(
            column=self.column, data_type=self.data_type)



class DatabaseRowABC(object):
    """Abstract base class for supporting database operations on an entire 
    row (multiple fields)."""

    def __init__(self, row_mold):
        """An implementation of `DatabaseFieldABC` must be declared as 
        `FIELD_CLASS` before this class can be instantiated."""
        self.row_mold = row_mold
        self.database_fields = [self.FIELD_CLASS(field_mold) \
            for field_mold in row_mold]

    @property
    def column_list(self):
        return ', '.join(
            [database_field.column \
                for database_field in self.database_fields])

    @property
    def declaration_list(self):
        return ', '.join(
            [database_field.declaration \
                for database_field in self.database_fields])

    @property
    def question_marks(self):
        return ', '.join(['?']*len(self.database_fields))

    def create_table_sql(self, table_name):
        raise NotImplementedError(
            '`create_table_sql` method not implemented for this class')

    def create_table(self, cursor, table_name):
        return cursor.execute(self.create_table_sql(table_name))

    def insert_into_table_sql(self, table_name):
        raise NotImplementedError(
            '`insert_into_table_sql` method not implemented for this class')

    def insert_into_table(self, cursor, table_name, dct):
        values = self.row_mold(dct).values()
        return cursor.execute(self.insert_into_table_sql(table_name), values)



class SQLiteField(DatabaseFieldABC):

    SQLITE_DATA_TYPE = {
        'unicode': 'TEXT',
        'str': 'TEXT',
        'int': 'INTEGER',
        'float': 'REAL',
    }

    @property
    def data_type(self):
        return self.SQLITE_DATA_TYPE[self.field_mold.data_type_name]



class SQLiteRow(DatabaseRowABC):

    FIELD_CLASS = SQLiteField

    def create_table_sql(self, table_name):
        return 'CREATE TABLE {table_name} ({declaration_list})'.format(
            table_name=table_name,
            declaration_list=self.declaration_list)

    def insert_into_table_sql(self, table_name):
        return 'INSERT INTO {table_name} ({column_list}) VALUES ({question_marks})'.format(
            table_name=table_name,
            column_list=self.column_list,
            question_marks=self.question_marks)
