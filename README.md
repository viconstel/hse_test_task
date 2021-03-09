# XLSX/CSV files processing service
## Description

The service accepts files in `.xlsx` or `.csv` 
formats as input, parse them into the Pandas DataFrame 
structure (when reading, it is possible to specify 
the index of the row with table headers), preprocess 
the table, if required (recognizing dates, 
renaming table columns, setting column data types). 
The next step is to load the table into the `PostgreSQL` 
database. During the initial insertion, the primary key 
of the table is set up; during the repeated insertion 
into an existing table, data is added to the end of the
table, assuming that the table names, column names 
and column data types match. Optionally, you can set 
the index on the specified columns.

## Launch
1. Clone this repository: `https://github.com/viconstel/hse_test_task.git`
2. Open bash and run commands:
```
- cd `path-to-project-directory`
- python3 -m venv `environment-name`
- source  `environment-name`/bin/activate
- pip install -r requirements.txt
- FLASK_APP=bin/app.py flask run
```

## Methods
Endpoint: `/upload/`

**GET** - method that renders home page and 
returns a HTML-file.<br> Responses: <br>
`200 - Success` <br><br>
**POST** - method to upload file and put it 
into the database. <br> Parameters: <br>
```
--file - file (.csv or .xlsx) to upload. Required parameter.
--col - list of new column names in correct order as a comma-separated string. The number of names must match the number of columns in the existing file.
--head - row number to use as the column names (header), integer.
--index - list of column names to set index on it (as a comma-separated string).
--type - set data type to the column(s). Argument is a dictionary {’column name’: 'type’}. Available types: int, float, str, datetime.
```
Responses:
```
200 - Success (HTML home page redirect)
422 - Error while processing data
500 - Internal Server Error
```
## Project structure
+ bin - source files
    + templates
        + home_page.html - home page HTML-file
    + app.py - main module with app definition
    + database.py - module for interacting with the database
    + parser.py - setup parser for request arguments
    + utils.py - utility functions
+ config
    + config.yml - database configuration file
+ tests
    + test_app.py - app tests
+ README.md - this file
+ requirements.txt - project requirements
+ specification.yml - OpenAPI specification file

## Database Settings
For the successful service work a PostgreSQL 9.6+ 
database must be deployed.
Setting up the file `config.yml`:
```
postgres_db:
  # Database name
  database_name: db_name
  # Username  
  user: admin
  # Password
  password: *****
  # Database host
  host: localhost
  # Database port
  port: 5432
```