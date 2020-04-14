# Division of labor:
The transfer and acquisition of information with the front end are carried out under the various api.py files. These files will call some of the functions in SqlUtils which has some database opertions.

The SqlUtils file encapsulate the details of the database operation.
# parameters & return values：
The parameter type routes.py passes to SqlUtils is string. SqlUtils use josn.loads() exchange it into dictionary and afterwards deal with it.

For storage, modify, delete operations, a dict object which contain searching information and the name of the target table is required, SqlUtils will return a integer. Return 1 for success and 0 for failure

For query operations, a dict object which contain searching information and the name of the target table is required, SqlUtils will return a list, in which each value is a dictionary

