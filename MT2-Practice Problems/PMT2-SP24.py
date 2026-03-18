
# coding: utf-8

# # `Midterm 2`: `Spring 2024`
# _Version 1.0.0_
# 
# *All of the header information is important. Please read it..*
# 
# **Topics number of exercises:** This problem builds on your knowledge of `Working with relational data (SQL/Pandas), Working with Numpy Arrays`. It has **7** exercises numbered 0 to **6**. There are **13** available points. However to earn 100% the threshold is **11** points. (Therefore once you hit **11** points you can stop. There is no extra credit for exceeding this threshold.)
# 
# **Exercise ordering:** Each exercise builds logically on previous exercises but you may solve them in any order. That is if you can't solve an exercise you can still move on and try the next one. Use this to your advantage as the exercises are **not** necessarily ordered in terms of difficulty. Higher point values generally indicate more difficult exercises. 
# 
# **Demo cells:** Code cells starting with the comment `### define demo inputs` load results from prior exercises applied to the entire data set and use those to build demo inputs. These must be run for subsequent demos to work properly but they do not affect the test cells. The data loaded in these cells may be rather large (at least in terms of human readability). You are free to print or otherwise use Python to explore them but we may not print them in the starter code.
# 
# **Debugging you code:** Right before each exercise test cell there is a block of text explaining the variables available to you for debugging. You may use these to test your code and can print/display them as needed (careful when printing large objects you may want to print the head or chunks of rows at a time).
# 
# **Exercise point breakdown:**
# 
# 
# - Exercise 0 - : **2** point(s)
# 
# - Exercise 1 - : **1** point(s)
# 
# - Exercise 2 - : **2** point(s)
# 
# - Exercise 3 - : **2** point(s)
# 
# - Exercise 4 - : **2** point(s)
# 
# - Exercise 5 - : **1** point(s)
# 
# - Exercise 6 - : **3** point(s)
# 
# 
# **Final reminders:** 
# 
# - Submit after **every exercise**
# - Review the generated grade report after you submit to see what errors were returned
# - Stay calm, skip problems as needed and take short breaks at your leisure

# ### New York Collisions
# 
# The City of New York collects detailed data on traffic collisions where police are involved. For each collision information including the date, time, geographic coordinates, vehicle details, and demographics of the people involved. They make this data and much, much more publicly available on [https://opendata.cityofnewyork.us/](https://opendata.cityofnewyork.us/). We have gone ahead and packaged this data into a SQLite object. The next code cell opens a connection to it.
# 
# In this notebook we're going to explore the structure of the tables in the connection, summarize them, and then preprocess and analyze geographic data.

# In[1]:


import re
import pandas as pd
import numpy as np
import sqlite3

conn = sqlite3.connect('file:resource/asnlib/publicdata/traffic.db?mode=ro', uri=True)


# ### Structure of tables
# 
# There are 3 tables in our connection: CRASHES, VEHICLES, and PERSON. We don't know of the relationships between the tables or even what columns they contain. The code we will write in the next two exercises will help find these answers.

# ## Exercise 0: (2 points)
# **get_table_cols**  
# 
# **Your task:** define `get_table_cols` as follows:
# 
# 

# Given a SQLite database connection and a table name, determine the column names for that table. Return your result as a Python list sorted in alphabetical order.
# 
# Your function 'get_table_cols' should first verify that the table_name parameter only contains letters, numbers, or underscores. If that is not the case a ValueError must be raised.
# 
# **Hint**: Your solution will likely require a dynamically generated query, as SQLite does not allow parameters in a FROM clause.  
# **Hint**: If you choose to use a SELECT statement, be mindful of how many rows it returns... It's probably not a good use of resources to use _all_ of them.

# In[2]:


### Solution - Exercise 0  

def get_table_cols(table_name, conn):
    
    pattern = "^[A-za-z0-9_]+$"
    
    if not bool(re.match(pattern, table_name)): #check the table_name parameter only contains letters, numbers, or underscores
        raise ValueError("Invalid table name.")
        
    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    query = f"SELECT * FROM {table_name} LIMIT 1" #Build the SQL query string using string formatting
    
    data = cursor.execute(query)
    
    py_list = []
    for column in data.description:
        py_list.append(column[0])
        
    py_list.sort()
    
    return py_list
  

### Demo function call
print(get_table_cols(table_name='vehicles', conn=conn))


# The demo above should display the following output:
# ```
# ['COLLISION_ID', 'CONTRIBUTING_FACTOR_1', 'CONTRIBUTING_FACTOR_2', 'CRASH_DATE', 'CRASH_TIME', 'DRIVER_LICENSE_JURISDICTION', 'DRIVER_LICENSE_STATUS', 'DRIVER_SEX', 'POINT_OF_IMPACT', 'PRE_CRASH', 'PUBLIC_PROPERTY_DAMAGE', 'PUBLIC_PROPERTY_DAMAGE_TYPE', 'STATE_REGISTRATION', 'TRAVEL_DIRECTION', 'UNIQUE_ID', 'VEHICLE_DAMAGE', 'VEHICLE_DAMAGE_1', 'VEHICLE_DAMAGE_2', 'VEHICLE_DAMAGE_3', 'VEHICLE_ID', 'VEHICLE_MAKE', 'VEHICLE_MODEL', 'VEHICLE_OCCUPANTS', 'VEHICLE_TYPE', 'VEHICLE_YEAR']
# 
# ```

#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for get_table_cols (exercise 0). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 

# In[3]:


def get_table_cols_wrapper(table_name, conn):
    out = None
    err = False
    try:
        out = get_table_cols(table_name, conn)
    except ValueError:
        err = True
    finally:
        return err, out


# In[4]:


### Test Cell - Exercise 0  

from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load

with open('resource/asnlib/publicdata/assignment_config.yaml') as f:
    ex_conf = safe_load(f)['exercises']['get_table_cols']['config']

ex_conf['func'] = get_table_cols_wrapper

tester = Tester(ex_conf, key=b'bCims7OtaJU-ugwkHsiGLrZlwMV_w-IQXM4JkYtV-m8=', path='resource/asnlib/publicdata/')
for _ in range(100):
    try:
        tester.run_test()
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
    except:
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
        raise

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ## Exercise 1: (1 points)
# **intersection_of_cols**  
# 
# **Your task:** define `intersection_of_cols` as follows:
# 
# 

# Given a list (`lol`) containing sub-lists of table column names, identify all column names which are present in at least `num` sublists.  
# 
# Return your result as a Python set.

# In[5]:


### Solution - Exercise 1  
from collections import Counter
def intersection_of_cols(lol: list, num=None) -> set:
    assert len(lol) > 1, '`lol` must have at least 2 items'
    if num is None:
        num = len(lol)
        
    name_counts = Counter() #Initialize an empty Counter to count names
    
    for sublist in lol:
        name_counts.update(sublist)
    
    result = []
    
    for key, value in name_counts.items():
        if value >= num:
            result.append(key)
    result = set(result)
        
    return result
    
### Demo function call
for num in [2,3]:
    demo_intersection = intersection_of_cols(
        lol=[['ringo', 'phyllis', 'angela', 'paul'], 
             ['kevin', 'paul', 'oscar', 'kelly', 'phyllis'], 
             ['phyllis', 'oscar', 'ryan', 'john', 'toby']],
        num=num)
    print(f'num={num}; intersection={demo_intersection}')


# The demo above should display the following output:
# ```
# num=2; intersection={'oscar', 'paul', 'phyllis'}
# num=3; intersection={'phyllis'}
# 
# ```

#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for intersection_of_cols (exercise 1). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 

# In[6]:


### Test Cell - Exercise 1  

from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load

with open('resource/asnlib/publicdata/assignment_config.yaml') as f:
    ex_conf = safe_load(f)['exercises']['intersection_of_cols']['config']

ex_conf['func'] = intersection_of_cols

tester = Tester(ex_conf, key=b'2Vf2WPfW2j0DLeUMjMzLkjVc8oiSatIE1WdsEL-_X5Q=', path='resource/asnlib/publicdata/')
for _ in range(100):
    try:
        tester.run_test()
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
    except:
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
        raise

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ### Summaries
# 
# We want to get some high level sense of the current traffic collision situation and how that situation has changed over time. We will accomplish this goal with the code for the next few exercises. 

# ## Exercise 2: (2 points)
# **summarize_person**  
# 
# **Your task:** define `summarize_person` as follows:
# 
# 

# Given a SQLite database connection which contains the PERSON table provide a summary with these columns:
# - YEAR: Year for which summary stats are computed. (taken from the CRASH_DATE field)
# - INJURY_COUNT: Count of records with 'Injured' values in the PERSON_INJURY field for the same year.
# - DEATHS_COUNT: Count of records with 'Killed' values in the PERSON_INJURY field for the same year.
# - UNSPECIFIED_COUNT: Count of records with 'Unspecified' values in the PERSON_INJURY field for the same year.
# 
# Return your result as a Pandas DataFrame.

# In[7]:


### Solution - Exercise 2  

def summarize_person(conn):
    #query = '''SELECT CRASH_DATE FROM PERSON LIMIT 2''' # 10/19/2017

    query = '''
    SELECT
        SUBSTR(CRASH_DATE, -4) AS YEAR, 
        SUM(CASE WHEN PERSON_INJURY = 'Injured' THEN 1 ELSE 0 END) AS INJURY_COUNT,
        SUM(CASE WHEN PERSON_INJURY = 'Killed' THEN 1 ELSE 0 END) AS DEATHS_COUNT,
        SUM(CASE WHEN PERSON_INJURY = 'Unspecified' THEN 1 ELSE 0 END) AS UNSPECIFIED_COUNT
    FROM PERSON 
    GROUP BY YEAR
    '''
    df = pd.read_sql_query(query, conn)

    return df
### Demo function call
demo_person_summary_df = summarize_person(conn)
display(demo_person_summary_df)


# The demo above should display the following output:  
# 
# |    |   YEAR |   INJURY_COUNT |   DEATHS_COUNT |   UNSPECIFIED_COUNT |
# |---:|-------:|---------------:|---------------:|--------------------:|
# |  0 |   2012 |          27447 |            137 |                  87 |
# |  1 |   2013 |          55127 |            297 |                 191 |
# |  2 |   2014 |          51212 |            262 |                 379 |
# |  3 |   2015 |          51357 |            243 |                 571 |
# |  4 |   2016 |          60076 |            239 |              740038 |
# |  5 |   2017 |          60655 |            261 |              900859 |
# |  6 |   2018 |          61918 |            231 |              884054 |
# |  7 |   2019 |          61388 |            244 |              792637 |
# |  8 |   2020 |          44614 |            269 |              368310 |
# |  9 |   2021 |          51782 |            296 |              333997 |
# | 10 |   2022 |          51931 |            289 |              310335 |
# | 11 |   2023 |          54230 |            273 |              284491 |
# | 12 |   2024 |           8037 |             41 |               41617 |

#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for summarize_person (exercise 2). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 

# In[8]:


### Test Cell - Exercise 2  

from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load

with open('resource/asnlib/publicdata/assignment_config.yaml') as f:
    ex_conf = safe_load(f)['exercises']['summarize_person']['config']

ex_conf['func'] = summarize_person

tester = Tester(ex_conf, key=b'RyeS0CX3AlR5W2hkDjq59hAtdzYRhkzP7eAhq88uBj0=', path='resource/asnlib/publicdata/')
for _ in range(5):
    try:
        tester.run_test()
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
    except:
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
        raise

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ## Exercise 3: (2 points)
# **summarize_crashes**  
# 
# **Your task:** define `summarize_crashes` as follows:
# 
# 

# Given a SQLite database connection which contains the CRASHES table provide a summary with these columns:
# - **YEAR**: Year for which summary stats are computed. (taken from the "CRASH DATE" field)
# - **CRASH_COUNT**: Count of crashes in the same year.
# - **DEATHS**: Sum of the "NUMBER OF PERSONS KILLED" values in the same year.
# - **PEDESTRIAN_DEATHS**: Sum of the "NUMBER OF PEDESTRIANS KILLED" values in the same year.
# - **PEDESTRIAN_DEATH_SHARE**: The quotient PEDESTRIAN_DEATHS/DEATHS
# - **DEATHS_PER_CRASH**: The quotient DEATHS/CRASH_COUNT
# 
# Return your result as a Pandas DataFrame

# In[9]:


### Solution - Exercise 3  

def summarize_crashes(conn):
    #query = '''SELECT "CRASH DATE" FROM CRASHES LIMIT 2''' # 09/11/2021

    query = '''
    SELECT
        SUBSTR("CRASH DATE", -4) AS YEAR, 
        COUNT(*) AS CRASH_COUNT,
        SUM("NUMBER OF PERSONS KILLED") AS DEATHS,
        SUM("NUMBER OF PEDESTRIANS KILLED") AS PEDESTRIAN_DEATHS,
        SUM("NUMBER OF PEDESTRIANS KILLED") / SUM("NUMBER OF PERSONS KILLED") AS PEDESTRIAN_DEATH_SHARE,
        SUM("NUMBER OF PERSONS KILLED") / COUNT(*) AS DEATHS_PER_CRASH
    FROM CRASHES 
    GROUP BY YEAR
    '''
    df = pd.read_sql_query(query, conn)
    
    return df

### Demo function call
demo_crashes_summary = summarize_crashes(conn)
display(demo_crashes_summary)


# The demo above should display the following output:  
# 
# |    |   YEAR |   CRASH_COUNT |   DEATHS |   PEDESTRIAN_DEATHS |   PEDESTRIAN_DEATH_SHARE |   DEATHS_PER_CRASH |
# |---:|-------:|--------------:|---------:|--------------------:|-------------------------:|-------------------:|
# |  0 |   2012 |        100545 |      137 |                  72 |                 0.525547 |        0.00136257  |
# |  1 |   2013 |        203742 |      297 |                 176 |                 0.592593 |        0.00145773  |
# |  2 |   2014 |        206033 |      262 |                 133 |                 0.507634 |        0.00127164  |
# |  3 |   2015 |        217694 |      243 |                 133 |                 0.547325 |        0.00111625  |
# |  4 |   2016 |        229831 |      246 |                 149 |                 0.605691 |        0.00107035  |
# |  5 |   2017 |        231007 |      256 |                 127 |                 0.496094 |        0.00110819  |
# |  6 |   2018 |        231564 |      231 |                 123 |                 0.532468 |        0.000997564 |
# |  7 |   2019 |        211486 |      244 |                 131 |                 0.536885 |        0.00115374  |
# |  8 |   2020 |        112915 |      269 |                 101 |                 0.375465 |        0.00238232  |
# |  9 |   2021 |        110549 |      296 |                 131 |                 0.442568 |        0.00267755  |
# | 10 |   2022 |        103881 |      289 |                 134 |                 0.463668 |        0.00278203  |
# | 11 |   2023 |         96563 |      273 |                 104 |                 0.380952 |        0.00282717  |
# | 12 |   2024 |         14259 |       41 |                  17 |                 0.414634 |        0.00287538  |

#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for summarize_crashes (exercise 3). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 

# In[10]:


### Test Cell - Exercise 3  

from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load

with open('resource/asnlib/publicdata/assignment_config.yaml') as f:
    ex_conf = safe_load(f)['exercises']['summarize_crashes']['config']

ex_conf['func'] = summarize_crashes

tester = Tester(ex_conf, key=b'LzLE2EBzHIODexIqa8grPVUkAbrllL3Y6PD6REvlZGo=', path='resource/asnlib/publicdata/')
for _ in range(100):
    try:
        tester.run_test()
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
    except:
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
        raise

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ## Exercise 4: (2 points)
# **summarize_vehicles**  
# 
# **Your task:** define `summarize_vehicles` as follows:
# 
# 

# Given a SQLite database connection which contains the VEHICLES and CRASHES tables provide a summary with these columns:
# - VEHICLE_TYPE: The upper-case VEHICLE_TYPE from VEHICLES for which summary stats are computed
#     - You may encounter records with NULL values in the VEHICLE_TYPE field. These should **not** be included in your calculation.
# - COUNT: The number of records with the same VEHICLE_TYPE
# - OUT_OF_STATE: The number of records with the same VEHICLE_TYPE having upper-case STATE_REGISTRATION values in VEHICLES other than 'NY' 
#     - NULL values in the STATE_REGISTRATION field **do not count as OUT_OF_STATE**.
# - DEATHS: The sum of the "NUMBER OF PERSONS KILLED" values in CRASHES associated with the same VEHICLE_TYPE. 
#     - You can relate VEHICLES to CRASHES by the COLLISION_ID column which is common to both tables.
#   
# Additionally,
# - The result should be sorted by COUNT in descending order then by VEHICLE_TYPE in ascending order.
# - The result should include at most 30 rows
# - Your result should only be derived from records which have a COLLISION_ID value present in both tables.
# - Your result should **not include** any row with NULL as the VEHICLE_TYPE value.
#   
# Return your result as a Pandas DataFrame

# In[11]:


### Solution - Exercise 4  

def summarize_vehicles(conn):
    query = '''
    SELECT 
        UPPER(v.VEHICLE_TYPE) AS VEHICLE_TYPE,
        COUNT(*) AS COUNT,
        SUM(CASE WHEN v.STATE_REGISTRATION != 'NY' 
        AND v.STATE_REGISTRATION = UPPER(v.STATE_REGISTRATION) 
        AND v.STATE_REGISTRATION IS NOT NULL THEN 1 ELSE 0 END) AS OUT_OF_STATE,
        -- CAST converts the text values to integers before summing them
        SUM(CAST(c."NUMBER OF PERSONS KILLED" AS INTEGER)) AS DEATHS
    FROM VEHICLES AS v
    INNER JOIN CRASHES AS c ON v.COLLISION_ID = c.COLLISION_ID
    WHERE v.VEHICLE_TYPE IS NOT NULL 
    GROUP BY UPPER(v.VEHICLE_TYPE)
    ORDER BY COUNT DESC, VEHICLE_TYPE ASC
    LIMIT 30;
     
    '''

    df = pd.read_sql_query(query, conn)
    return df
### Demo function call
demo_vehicle_summary = summarize_vehicles(conn)
display(demo_vehicle_summary)


# The demo above should display the following output:  
# 
# |    | VEHICLE_TYPE                        |   COUNT |   OUT_OF_STATE |   DEATHS |
# |---:|:------------------------------------|--------:|---------------:|---------:|
# |  0 | SEDAN                               | 1035884 |         191291 |     1131 |
# |  1 | STATION WAGON/SPORT UTILITY VEHICLE |  825981 |         126382 |     1115 |
# |  2 | PASSENGER VEHICLE                   |  770753 |         110002 |      623 |
# |  3 | SPORT UTILITY / STATION WAGON       |  337927 |          38312 |      383 |
# |  4 | TAXI                                |  152218 |           2326 |       97 |
# |  5 | UNKNOWN                             |  105571 |          12853 |       79 |
# |  6 | PICK-UP TRUCK                       |   91798 |          24261 |      118 |
# |  7 | 4 DR SEDAN                          |   73573 |          11448 |       58 |
# |  8 | VAN                                 |   68465 |          13626 |       72 |
# |  9 | BUS                                 |   67173 |           6527 |      147 |
# | 10 | BOX TRUCK                           |   53364 |          23557 |       81 |
# | 11 | BIKE                                |   46765 |            619 |      173 |
# | 12 | OTHER                               |   45966 |          12336 |       40 |
# | 13 | LARGE COM VEH(6 OR MORE TIRES)      |   28604 |          12494 |       66 |
# | 14 | SMALL COM VEH(4 TIRES)              |   26683 |           7717 |       12 |
# | 15 | MOTORCYCLE                          |   23321 |           2394 |      401 |
# | 16 | TRACTOR TRUCK DIESEL                |   20887 |          15208 |       77 |
# | 17 | LIVERY VEHICLE                      |   19441 |            359 |       10 |
# | 18 | BICYCLE                             |   19333 |            922 |       59 |
# | 19 | AMBULANCE                           |   10991 |            141 |        7 |
# | 20 | E-BIKE                              |    9055 |            198 |       73 |
# | 21 | DUMP                                |    8122 |           1288 |       47 |
# | 22 | CONVERTIBLE                         |    6470 |           1171 |        9 |
# | 23 | E-SCOOTER                           |    5779 |            126 |       25 |
# | 24 | FLAT BED                            |    5099 |           1728 |       26 |
# | 25 | MOPED                               |    4842 |            208 |       17 |
# | 26 | PK                                  |    4838 |           1414 |       11 |
# | 27 | 2 DR SEDAN                          |    4833 |            940 |        9 |
# | 28 | GARBAGE OR REFUSE                   |    4494 |            689 |       21 |
# | 29 | CARRY ALL                           |    4007 |           1897 |        7 |
# 

#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for summarize_vehicles (exercise 4). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 

# In[12]:


### Test Cell - Exercise 4  

from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load

with open('resource/asnlib/publicdata/assignment_config.yaml') as f:
    ex_conf = safe_load(f)['exercises']['summarize_vehicles']['config']

ex_conf['func'] = summarize_vehicles

tester = Tester(ex_conf, key=b'abnTJj1xha26W0V1GiFPY9_H9c3tllHziFuhZXXc66A=', path='resource/asnlib/publicdata/')
for _ in range(5):
    try:
        tester.run_test()
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
    except:
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
        raise

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ### Geographic Density  
# 
# The ultimate goal of collecting this data is to minimize traffic collision fatalities through policy changes and traffic engineering. Both methods require identifying problem areas for further study. This is exactly why the geographic location is captured!
# 
# In the next two exercises we will implement functions to overlay the density of fatal crashes on a map of the city. 

# ## Exercise 5: (1 points)
# **geo_filter_crashes**  
# 
# **Your task:** define `geo_filter_crashes` as follows:
# 
# 

# Given a SQL query, a connection, and a list of coordinate parameters your solution should:
# - Get the result of running the query against the connection using the coordinate parameters. This intermediate result should be a DataFrame.
# - Cast the CRASH_DATE column from a string (object) to datetime64.
# - Return the result.

# In[18]:


### Solution - Exercise 5  

def geo_filter_crashes(qry, conn, params): 
    df = pd.read_sql_query(qry, conn, params=params)
    df['CRASH_DATE'] = df['CRASH_DATE'].astype('datetime64')
    return df

### Demo function call
demo_qry = '''
        select
            "CRASH DATE" AS CRASH_DATE,
            LATITUDE,
            LONGITUDE,
            "NUMBER OF PERSONS KILLED" AS PERSONS_KILLED
        from
            crashes
        where
            latitude is not null and latitude between ? and ?
        and
            longitude is not null and longitude between ? and ?
        and
            PERSONS_KILLED is not null and PERSONS_KILLED > 0
    '''
demo_df = geo_filter_crashes(demo_qry, conn, [40.5, 40.95, -74.1, -73.65])
display(demo_df.head())


# The demo above should display the following output:  
# 
# |    | CRASH_DATE          |   LATITUDE |   LONGITUDE |   PERSONS_KILLED |
# |---:|:--------------------|-----------:|------------:|-----------------:|
# |  0 | 2021-07-09 00:00:00 |    40.7205 |    -73.8889 |                1 |
# |  1 | 2021-12-12 00:00:00 |    40.8404 |    -73.9181 |                1 |
# |  2 | 2021-04-15 00:00:00 |    40.6205 |    -74.0293 |                1 |
# |  3 | 2021-04-17 00:00:00 |    40.7825 |    -73.9788 |                1 |
# |  4 | 2021-07-08 00:00:00 |    40.7215 |    -73.9838 |                1 |
# 

#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for geo_filter_crashes (exercise 5). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 

# In[19]:


### Test Cell - Exercise 5  

from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load

with open('resource/asnlib/publicdata/assignment_config.yaml') as f:
    ex_conf = safe_load(f)['exercises']['geo_filter_crashes']['config']

ex_conf['func'] = geo_filter_crashes

tester = Tester(ex_conf, key=b'Js0HmgMQRjHXmmjXi4nPGc7_U3iIQ1qUUSDFWDdOM_g=', path='resource/asnlib/publicdata/')
for _ in range(20):
    try:
        tester.run_test()
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
    except:
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
        raise

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# We used a solution for the prior exercise to query the CRASHES table to get the latitude, longitude, and number of fatalities for all crashes in our dataset. Then we fed that result into a KDE model. KDE is a non-parametric technique for estimating the PDF of a distribution given some samples drawn from it. The high level is that for every observation we place a Gaussian distribution centered at the coordinates. Once all the distributions are placed, the sum is proportional to the PDF estimate. For our use case the model estimates the density of fatal crashes over a geographic area - i.e. given that there was a fatal crash higher estimates for the PDF indicate a higher probability of the crash having occurred at those coordinates. 
# 
# ```
# crash_density = stats.gaussian_kde(df[['LONGITUDE', 'LATITUDE']].values.T,
#                                   0.02,
#                                   weights=df['PERSONS_KILLED'].values)
# ```
# 
# The model outputs a function which takes a Numpy array as an input and returns a Numpy array of density estimates corresponding to the inputs. The input's shape is (# dimensions, # data points) and the output's shape in (# data points, ).

# ## Exercise 6: (3 points)
# **density_grid**  
# 
# **Your task:** define `density_grid` as follows:
# 
# 

# Given a bounding box of coordinates, a grid size, and an estimator.
# - Build an array (`x`) of `grid_size` evenly spaced numbers between and including the min and max x coordinates.
#     - The `np.linspace` function is useful here.
# - Build a similar array (`y`) for the y coordinates.
# - For every pair with one element chosen from `x` and one from `y` use the `estimator` to compute the PDF for the pair.
#     - You can use `np.meshgrid`, `np.vstack`, and `np.flatten` to compute a suitable input for the `estimator`.
#     - `estimator` expects an array with shape (2, # data points). The first row is the `x` values and the second row is the `y` values.
# - Return the result as a Numpy array.
#     - The array should have shape `(grid_size, grid_size)`.
#     - Each row in the array should be from the same `y` value. 
#     - Each column in the array should be from the same `x` value.
#     - `y` and `x` values increase from the origin at the top-left. 
#     
# **Note**: The bounds are given as a list `[xmin, xmax, ymin, ymax]`.  

# In[31]:


### Solution - Exercise 6  

def density_grid(bounds, grid_size, estimator):
   #Use the bounding box (the min and max values) to find your start and end points for both X and Y.
    x = np.linspace(bounds[0], bounds[1], num = grid_size)
    y = np.linspace(bounds[2], bounds[3], num = grid_size)

    #Create the 2D grid matrices
    X, Y = np.meshgrid(x,y) #10 X 10 matrices, 100 pairs
    
    #Create stacked array to compute a suitable input for the estimator (2, # data points), flatten to 1-D array

    stacked_array = np.vstack([X.flatten(), Y.flatten()]) 
    
    #Find density values using estimator
    
    density_val = estimator(stacked_array) #returns a flat 1D array of density values
    
    #Reshape to a Square
    
    square_array = density_val.reshape(grid_size, grid_size)
    
    
    return square_array


### Demo function call
demo_bounds = [0, 9, 0, 90]
demo_grid_size = 10
# estimator adds the x and y values
demo_estimator = lambda a: a[0] + a[1]
demo_grid = density_grid(demo_bounds, demo_grid_size, demo_estimator)
print(demo_grid)


# The demo above should display the following output:  
# 
# ```
# [[ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9.]
#  [10. 11. 12. 13. 14. 15. 16. 17. 18. 19.]
#  [20. 21. 22. 23. 24. 25. 26. 27. 28. 29.]
#  [30. 31. 32. 33. 34. 35. 36. 37. 38. 39.]
#  [40. 41. 42. 43. 44. 45. 46. 47. 48. 49.]
#  [50. 51. 52. 53. 54. 55. 56. 57. 58. 59.]
#  [60. 61. 62. 63. 64. 65. 66. 67. 68. 69.]
#  [70. 71. 72. 73. 74. 75. 76. 77. 78. 79.]
#  [80. 81. 82. 83. 84. 85. 86. 87. 88. 89.]
#  [90. 91. 92. 93. 94. 95. 96. 97. 98. 99.]]
# ```

#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for density_grid (exercise 6). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 

# In[32]:


### Test Cell - Exercise 6  

from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load

with open('resource/asnlib/publicdata/assignment_config.yaml') as f:
    ex_conf = safe_load(f)['exercises']['density_grid']['config']

ex_conf['func'] = density_grid

tester = Tester(ex_conf, key=b'OUm-rIOTtKW4RMUlmslRWQrXyW9IoJbDwb3UcOkhuCg=', path='resource/asnlib/publicdata/')
for _ in range(20):
    try:
        tester.run_test()
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
    except:
        (input_vars, original_input_vars, returned_output_vars, true_output_vars) = tester.get_test_vars()
        raise

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# **If you have reached this point, congratulations! Don't forget to submit your work!**
# 
# The remaining content is informational only.
# 
# We have filled in the gaps with the parameter values and used some reference map data to render the density of traffic collision fatalities over a road map of NYC. It takes a bit to render, so we're just providing the code for reference and showing the rendered image.
# 
# ```
# import geopandas
# from matplotlib import pyplot as plt
# from scipy import stats
# 
# ###
# ### This query identifies the date and coordinates of all traffic collision fatalities available.
# ###
# qry = '''
#         select
#             "CRASH DATE" AS CRASH_DATE,
#             LATITUDE,
#             LONGITUDE,
#             "NUMBER OF PERSONS KILLED" AS PERSONS_KILLED
#         from
#             crashes
#         where
#             latitude is not null and latitude between ? and ?
#         and
#             longitude is not null and longitude between ? and ?
#         and
#             PERSONS_KILLED is not null and PERSONS_KILLED > 0
#     '''
#     
# ###
# ### We feed the query into our geo_filter_crashes along with a bounding box for NYC and use 
# ### the result to define a KDE model.
# ###
# df = geo_filter_crashes(qry, conn, [40.5, 40.95, -74.1, -73.65])
# crash_density = stats.gaussian_kde(df[['LONGITUDE', 'LATITUDE']].values.T,
#                                   0.02,
#                                   weights=df['PERSONS_KILLED'].values)
# ###
# ### Set a grid size and bounding box then build our density grid
# ###
# grid_size = 800
# bounds = [df['LONGITUDE'].min(), 
#           df['LONGITUDE'].max(),
#           df['LATITUDE'].min(), 
#           df['LATITUDE'].max()]
# Z = density_grid(bounds, grid_size, crash_density)
# 
# ###
# ### Set up some stuff with the plotting library, read the roadmap from a file and plot it.
# ###
# plt.rcParams['figure.figsize'] = [40, 40]
# gdf=geopandas.read_file('resource/asnlib/publicdata/svwp-sbcd.geojson')
# gdf.plot(ax=ax, zorder=0)
# 
# ###
# ### Plot the density over the map.
# ###
# ax.imshow(Z, extent=bounds, cmap='plasma', alpha=.7*(Z > 20).astype(float), origin='lower')
# plt.show()
# ```
# 
# ![NYC Roadmap with traffic fatality density overlay](resource/asnlib/publicdata/density_plot.png "NYC Roadmap with traffic fatality density overlay")
