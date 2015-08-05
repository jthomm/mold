# mold
A utility for typecasting and transforming text data sources in Python

## Purpose
Convert a text data source like this (.csv)
```csv
Name,K%,PA
Mike Trout,22.5 %,378
```
into this
```py
OrderedDict([('year', 2015), ('name', u'Mike Trout'), ('pa', 378), ('k_pct', 22.5)])
```
by defining a configuration like this (.yaml)
```yaml
---
- source: Year
  default: 2015
- source: Name
- source: PA
  type: int
- source: K%
  target: k_pct
  type: float
  rstrip: ' %'
```

## Usage
Following the above example, assume the data source file is named "players.csv" and the configuration file is named "config.yaml":
```py
>>> import csv
>>> rows = list(csv.DictReader(open('players.csv', 'rb')))
>>> rows[0]
{'PA': '378', 'Name': 'Mike Trout', 'K%': '22.5 %'}
>>>
>>> import yaml
>>> config = yaml.load(open('config.yaml', 'rb').read())
>>> config
[{'default': 2015, 'source': 'Year'}, {'source': 'Name'}, {'source': 'PA', 'type': 'int'}, {'source': 'K%', 'type': 'float', 'target': 'k_pct', 'rstrip': ' %'}]
>>>
>>> from mold import Mold
>>> m = Mold(config)
>>> m(rows[0])
OrderedDict([('year', 2015), ('name', u'Mike Trout'), ('pa', 378), ('k_pct', 22.5)])
```
It's just. that. easy.
