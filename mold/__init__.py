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
