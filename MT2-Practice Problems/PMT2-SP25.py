
# coding: utf-8

# # `Midterm 2, Spring 2025`: `Data Deidentification`
# _Version 0.0.2_
# 
# *All of the header information is important. Please read it..*
# 
# **Topics number of exercises:** This problem builds on your knowledge of `SQL, basic Python, pandas, and NumPy`. It has **11** exercises numbered 0 to **10**. There are **22** available points. However to earn 100% the threshold is **14** points. (Therefore once you hit **14** points you can stop. There is no extra credit for exceeding this threshold.)
# 
# **Exercise ordering:** Each exercise builds logically on previous exercises but you may solve them in any order. That is if you can't solve an exercise you can still move on and try the next one. Use this to your advantage as the exercises are **not** necessarily ordered in terms of difficulty. Higher point values generally indicate more difficult exercises. 
# 
# **Demo cells:** Code cells starting with the comment `### Run Me!!!` load results from prior exercises applied to the entire data set and use those to build demo inputs. These must be run for subsequent demos to work properly but they do not affect the test cells. The data loaded in these cells may be rather large (at least in terms of human readability). You are free to print or otherwise use Python to explore them but we may not print them in the starter code.
# 
# **Debugging your code:** Right before each exercise test cell there is a block of text explaining the variables available to you for debugging. You may use these to test your code and can print/display them as needed (careful when printing large objects you may want to print the head or chunks of rows at a time).
# 
# **Exercise point breakdown:**
# 
# 
# - Exercise 0 - : **1** point(s)
# 
# - Exercise 1 - : **2** point(s)
# 
# - Exercise 2 - : **1** point(s)
# 
# - Exercise 3 - : **2** point(s)
# 
# - Exercise 4 - : **3** point(s)
# 
# - Exercise 5 - : **3** point(s)
# 
# - Exercise 6 - : **2** point(s)
# 
# - Exercise 7 - : **1** point(s)
# 
# - Exercise 8 - : **2** point(s)
# 
# - Exercise 9 - : **2** point(s)
# 
# - Exercise 10 - : **3** point(s)
# 
# 
# **Final reminders:** 
# 
# - Submit after **every exercise**
# - Review the generated grade report after you submit to see what errors were returned
# - Stay calm, skip problems as needed and take short breaks at your leisure

# ## The Problem
# 
# This exam mimics the process of exploring and extracting data from a university database for third-party research. The law in the United States requires your university to protect your personal information when working with outside organizations.
# 
# ## Your Overall Task
# 
# For this exam, you are given a mock university database, and you must "de-identify" it for sharing with outside researchers. Deidentification refers to hiding or removing details that could be used to associate data with specific people. Your overall task is to do the following:
# 
# 1. **Explore the Database Schema**  
#    Use SQL queries to explore the mock university database and understand its structure, including table names, columns, data types, and relationships between tables.
# 
# 2. **Pull the Required Data**  
#    Write SQL queries to retrieve the required data for analysis, ensuring the minimum necessary data is selected for the task.
# 
# 3. **Deidentify the Data**  
#    Use Python, Pandas, and NumPy to deidentify the data. This includes:
#    - **Masking**: Obfuscating identifiers like student ID, ethnicity, location, and major.
#    - **Perturbing**: Slightly modifying data values (e.g., GPA) to prevent reidentification while maintaining overall statistical properties.
# 
# By the end of this exam, you will have a deidentified dataset ready for third-party research.

# ### Run me!
# 
# Run the two cells below to load the global imports, database connection, and objects needed for the exam. In particular, take note of conn, a SQLite3 connection object. **The exam will not run without these cells**. 

# In[2]:


### Global imports
import dill
from cse6040_devkit import plugins, utils
from cse6040_devkit.training_wheels import run_with_timeout, suppress_stdout
import tracemalloc
from time import time
import re 
import sqlite3 
import hashlib 
import pandas as pd
import numpy as np
from pprint import pprint



# In[3]:


# Load the database and objects
conn = sqlite3.connect('resource/asnlib/publicdata/university.db')

SEED = 6040


# ## The Tables
# 
# The database has eight (8) tables whose overall organization and columns are depicted below. You do not need to understand all of these details right now, but you may find it helpful to refer back to them as you progress through the exam. Consider taking a screenshot, opening the picture in a new browser tab, using the Table of Contents feature to get back to this information later, or referring to the following [PDF copy of the image](https://gtvault-my.sharepoint.com/:b:/g/personal/ikerson3_gatech_edu/EafHXf9Ad3ZBimIsZNrGio8BqD3SA9C9sgQw5ROgtH_Yew?e=jhwmVy).
# 
# ## Schema Diagram
# 
# ![title](resource\asnlib\publicdata\schema_diagram.png)
# 
# 1. **`student_main`**  
#    Contains primary student information, including:
#    - `student_id`: Unique identifier for each student (primary key).
#    - `last_name`, `first_name`, `middle_initial`: Basic personal details.
#    - `email`: Email address, which may be null for some records.
#    - `gender`, `ethnicity`: Demographic details.
#    - `address`: Residential address.
#    - `us_citizen`, `us_resident`, `state_resident`, `pell_recipient`, `us_veteran`: Indicators for citizenship, residency, financial aid, and veteran status.
# 
# 2. **`student_enrollment`**  
#    Tracks student enrollment details, including:
#    - `id`: Primary key for each enrollment record.
#    - `student_id`: References `student_main.student_id`.
#    - `term`: Academic term (e.g., "202308" for Fall 2023).
#    - `major_code`: Code for the student's major.
#    - `semester_hours_attempted`, `semester_hours_earned`: Academic credit details.
#    - `semester_gpa`, `cumulative_hours_earned`, `cumulative_gpa`: Academic performance metrics.
# 
# 3. **`graduation`**  
#    Stores graduation records, including:
#    - `id`: Primary key for each graduation record.
#    - `student_id`: References `student_main.student_id`.
#    - `last_enroll_term`, `grad_term`: Last enrollment and graduation terms.
#    - `grad_level`: Graduation level (e.g., Bachelor, Master, Doctorate).
#    - `grad_status`: Graduation status (e.g., active, completed).
# 
# 4. **`student_key`**  
#    Links students to financial and employee records:
#    - `student_id`: Primary key, references `student_main.student_id`.
#    - `finance_id`: Financial record identifier.
#    - `employee_id`: Employee identifier (nullable).
# 
# 5. **`student_scholarship`**  
#    Records student scholarships and financial aid details, including:
#    - `id`: Primary key for each scholarship record.
#    - `finance_id`: References `student_key.finance_id`.
#    - `scholarship_term`: Term during which the scholarship was awarded.
#    - `scholarship_code`: Code identifying the scholarship, references `scholarship_rules.scholarship_code`.
#    - `scholarship_total`, `scholarship_payment`, `scholarship_refund`: Financial details of the scholarship.
# 
# 6. **`scholarship_rules`**  
#    Defines eligibility rules for scholarships, including:
#    - `id`: Primary key for each scholarship rule.
#    - `scholarship_crosswalk_id`: References `scholarship_crosswalk.id`.
#    - `scholarship_code`: Code identifying the scholarship.
#    - `major_code`: Eligibility criteria based on major, references `major_crosswalk.major_code`.
#    - `activation_date`: Date the rule became effective.
#    - `scholarship_active`: Indicates if the scholarship is currently active.
#    - `min_gpa`: Minimum GPA required to qualify.
#    - `gender`, `pell_recipient`, `us_veteran`, `us_citizen`, `us_resident`, `state_resident`: Eligibility criteria for specific demographics.
#    - `amount`: Scholarship amount awarded.
# 
# 7. **`scholarship_crosswalk`**  
#    Maps scholarships to descriptive details:
#    - `id`: Primary key for each scholarship description.
#    - `scholarship_code`: Code identifying the scholarship.
#    - `scholarship_description`: Description of the scholarship.
#    - `activation_date`: Date the description became effective.
# 
# 8. **`major_crosswalk`**  
#    Maps major codes to detailed descriptions:
#    - `id`: Primary key for each major description.
#    - `major_code`: Code for the major (e.g., "CS" for Computer Science).
#    - `major_description`: Descriptive name of the major.
#    - `activation_date`: Date the description became effective.
# 
# Review the helper functions below before tackling the exercises.

# ## Helper Functions
# 
# We have provided the following functions to **assist you in exploring the university database**. Run each cell to load the functions into your environment and view a demonstration of their usage. You are encouraged to use these functions to explore the database, understand its structure, and develop solutions to the exercises.

# In[4]:


def get_table_list(conn):
    """
    Retrieves the list of tables from the SQLite database.

    Args:
        conn: SQLite database connection object
        
    Returns:
        list: A list of table names in the database
    """
    # Query to get all tables from sqlite_master
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables_df = pd.read_sql_query(tables_query, conn)

    # Return the list of table names
    return tables_df['name'].tolist()

get_table_list_demo = get_table_list(conn)
for table in get_table_list_demo:
    print(table)


# In[5]:


def get_column_details(conn, table_name):
    """
    Retrieves column details for a specific table.

    Args:
        conn: SQLite database connection object
        table_name (str): Name of the table to get column details for
        
    Returns:
        DataFrame: A DataFrame containing column details with columns:
            - column_id: Column ID (0-based index)
            - column_name: Column name
            - data_type: Data type of the column
            - not_null: Whether column allows NULL values (1=NOT NULL, 0=NULL allowed)
            - primary_key: Whether column is a primary key (1=PRIMARY KEY, 0=not a primary key)
            - table_name: Name of the table
            
    Raises:
        AssertionError: If the provided table_name does not exist in the database
    """
    # Get the list of tables in the database and verify table_name exists
    tables = get_table_list(conn)
    assert table_name in tables, f"Table '{table_name}' does not exist in the database"

    # Use PRAGMA table_info to get column details
    pragma_query = f"PRAGMA table_info('{table_name}')"
    column_details = pd.read_sql_query(pragma_query, conn)

    # Add table name to the DataFrame
    column_details['table_name'] = table_name

    # Remove unnecessary columns
    column_details = column_details[['cid', 'name', 'type', 'notnull', 'pk', 'table_name']]

    # Rename columns for clarity
    column_details = column_details.rename(columns={
        'cid': 'column_id',
        'name': 'column_name',
        'type': 'data_type',
        'notnull': 'not_null',
        'pk': 'primary_key'
    })

    return column_details

get_column_details_demo_df = get_column_details(conn, 'student_main')
display(get_column_details_demo_df)


# In[6]:


def get_foreign_key_details(conn, table_name):
    """
    Retrieves foreign key details for a specific table.

    Args:
        conn: SQLite database connection object
        table_name (str): Name of the table to get foreign key details for
        
    Returns:
        DataFrame: A DataFrame containing foreign key details with columns:
            - column_name: Column name in the current table
            - references_table: Referenced table name
            - references_column: Referenced column name
            - table_name: Name of the table
            
    Raises:
        AssertionError: If the provided table_name does not exist in the database
    """
    # Get the list of tables in the database and verify table_name exists
    tables = get_table_list(conn)
    assert table_name in tables, f"Table '{table_name}' does not exist in the database"

    # Use PRAGMA foreign_key_list to get foreign key details
    pragma_query = f"PRAGMA foreign_key_list('{table_name}')"
    fk_details = pd.read_sql_query(pragma_query, conn)

    # If the DataFrame is empty, return an empty DataFrame with the required columns
    if fk_details.empty:
        empty_df = pd.DataFrame(columns=['column_name', 'references_table', 'references_column', 'table_name'])
        empty_df['table_name'] = table_name
        return empty_df

    # Add table name to the DataFrame
    fk_details['table_name'] = table_name

    # Keep only relevant columns and rename them for clarity
    fk_details = fk_details[['table_name', 'from', 'table', 'to']]
    fk_details.rename(columns={
        'from': 'column_name',
        'table': 'references_table', 
        'to': 'references_column'
    }, inplace=True)

    return fk_details

get_foreign_key_details_demo_df = get_foreign_key_details(conn, 'student_key')
display(get_foreign_key_details_demo_df)


# In[7]:


def get_table_schema(conn, table_name):
    """
    Combines column details and foreign key details for a specific table.

    Args:
        conn: SQLite database connection object
        table_name (str): Name of the table to get the schema for
        
    Returns:
        DataFrame: A DataFrame containing complete schema information for the table
        
    Raises:
        AssertionError: If the provided table_name does not exist in the database
    """
    # Get the list of tables in the database and verify table_name exists
    tables = get_table_list(conn)
    assert table_name in tables, f"Table '{table_name}' does not exist in the database"
    
    # Get column details
    column_details = get_column_details(conn, table_name)

    # Get foreign key details
    fk_details = get_foreign_key_details(conn, table_name)
    
    # Drop the table_name column from foreign key details before merging
    if not fk_details.empty:
        fk_details.drop(columns=['table_name'], inplace=True)

    # Merge only the foreign key columns we need, excluding table_name
    table_schema = column_details.merge(
        fk_details[['column_name', 'references_table', 'references_column']], 
        how='left',
        on='column_name'
    )
    
    return table_schema

get_table_schema_demo_df = get_table_schema(conn, 'student_main')
display(get_table_schema_demo_df)


# In the SQL section of the exam, you will use the `student_scholarship` table several times. Run the **FREE** exercise cell below to examine the table, understand the structure, and **get your free point**!

# ### Exercise 0: (1 points)
# **get_student_scholarship_schema__FREE**  
# 
# **Example:** we have defined `get_student_scholarship_schema__FREE` as follows:
# 
# **This is a free exercise!** 
# 
#     **Please run the test cell below to collect your FREE point**
# 

# In[8]:


### Solution - Exercise 0  
def get_student_scholarship_schema__FREE(conn):
    # Get schema information specifically for the student_scholarship table
    student_scholarship_schema = get_table_schema(conn, 'student_scholarship')
    
    # Return the schema information
    return student_scholarship_schema

### Demo function call
student_scholarship_schema = get_student_scholarship_schema__FREE(conn)
student_scholarship_schema


# In[9]:


### Run Me!!!
demo_result_get_student_scholarship_schema__FREE_TRUE = utils.load_object_from_publicdata('demo_result_get_student_scholarship_schema__FREE_TRUE')


#  
# 
# **The demo should display this output.**  
# 
# <div style="overflow-x:auto;">
#     <style>
#         table {
#             border-collapse: collapse;
#             margin: 15px 0;
#             font-size: 0.9em;
#             font-family: sans-serif;
#             width: auto;
#         }
#         th, td {
#             padding: 8px;
#             text-align: right;
#             border-bottom: 1px solid #ddd;
#         }
#         tr:hover {background-color: #f5f5f5;}
#     </style>
#     <table border="0" class="dataframe">
#   <thead>
#     <tr style="text-align: right;">
#       <th></th>
#       <th>column_id</th>
#       <th>column_name</th>
#       <th>data_type</th>
#       <th>not_null</th>
#       <th>primary_key</th>
#       <th>table_name</th>
#       <th>references_table</th>
#       <th>references_column</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <th>0</th>
#       <td>0</td>
#       <td>id</td>
#       <td>INTEGER</td>
#       <td>1</td>
#       <td>1</td>
#       <td>student_scholarship</td>
#       <td>NaN</td>
#       <td>NaN</td>
#     </tr>
#     <tr>
#       <th>1</th>
#       <td>1</td>
#       <td>finance_id</td>
#       <td>VARCHAR(12)</td>
#       <td>0</td>
#       <td>0</td>
#       <td>student_scholarship</td>
#       <td>student_key</td>
#       <td>finance_id</td>
#     </tr>
#     <tr>
#       <th>2</th>
#       <td>2</td>
#       <td>scholarship_term</td>
#       <td>VARCHAR(6)</td>
#       <td>0</td>
#       <td>0</td>
#       <td>student_scholarship</td>
#       <td>NaN</td>
#       <td>NaN</td>
#     </tr>
#     <tr>
#       <th>3</th>
#       <td>3</td>
#       <td>scholarship_code</td>
#       <td>VARCHAR</td>
#       <td>0</td>
#       <td>0</td>
#       <td>student_scholarship</td>
#       <td>scholarship_rules</td>
#       <td>scholarship_code</td>
#     </tr>
#     <tr>
#       <th>4</th>
#       <td>4</td>
#       <td>scholarship_total</td>
#       <td>INTEGER</td>
#       <td>0</td>
#       <td>0</td>
#       <td>student_scholarship</td>
#       <td>NaN</td>
#       <td>NaN</td>
#     </tr>
#     <tr>
#       <th>5</th>
#       <td>5</td>
#       <td>scholarship_payment</td>
#       <td>INTEGER</td>
#       <td>0</td>
#       <td>0</td>
#       <td>student_scholarship</td>
#       <td>NaN</td>
#       <td>NaN</td>
#     </tr>
#     <tr>
#       <th>6</th>
#       <td>6</td>
#       <td>scholarship_refund</td>
#       <td>INTEGER</td>
#       <td>0</td>
#       <td>0</td>
#       <td>student_scholarship</td>
#       <td>NaN</td>
#       <td>NaN</td>
#     </tr>
#   </tbody>
# </table>
#     </div>
# 
# 
#  ---
#  <!-- Test Cell Boilerplate -->  
#  The test cell below will always pass. Please submit to collect your free points for get_student_scholarship_schema__FREE (exercise 0).
#  

# In[10]:


### Test Cell - Exercise 0  


print('Passed! Please submit.')


# ## Part 1: Exploring and Compiling Data with SQL
#  
# In this section, you will use SQL queries to explore the mock university database and compile the required data for analysis. The connection to the database has been made for you, as part of the notebook starter code above, and is available in the environment as `conn`.

# ### Exercise 1: (2 points)
# **binary_indicators**  
# 
# **Your task:** define `binary_indicators` as follows:
# 
# To begin, it would be helpful to get a sense of the data in tables. Start by writing a SQL query to calculate the percentage of students with positive values for binary indicators.
# 
# **Inputs**:
# - None
# 
# **Return**:
# - A Python string containing a SQLite query that produces a table with 2 columns:
#     - `status`: The name of the binary indicator (column name)
#     - `percentage`: The percentage of students with a positive value for that indicator (between 0 and 100)
#     - The `status` column should be first and `percentage` column second; the order of the rows is not important.
# 
# **Requirements**:
# - Query the `student_main` table
# - Calculate percentages for these binary indicators and use the following text values in the `status` column:
#     - For `us_citizen` column → Use 'US Citizen' as the status value
#     - For `us_resident` column → Use 'US Resident' as the status value
#     - For `state_resident` column → Use 'State Resident' as the status value
#     - For `pell_recipient` column → Use 'Pell Recipient' as the status value
#     - For `us_veteran` column → Use 'US Veteran' as the status value
# - A positive value is indicated by 'Y' in the corresponding column
# 
# **Hints**:
# - Use UNION ALL to combine individual queries for each indicator. See the following [SQLite Union Documentation](https://www.sqlitetutorial.net/sqlite-union/) for an example.
# - Use SUM with CASE statements to calculate percentages of 'Y' values
# 

# In[11]:




### Solution - Exercise 1  
def binary_indicators() -> str:
    
    query_percentages = '''
    SELECT 'US Citizen' AS status,
    SUM(CASE WHEN us_citizen = 'Y' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS percentage
    FROM student_main
    UNION ALL
    SELECT 'US Resident' AS status,
    SUM(CASE WHEN us_resident = 'Y' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS percentage
    FROM student_main
    UNION ALL
    SELECT 'State Resident' AS status,
    SUM(CASE WHEN state_resident = 'Y' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS percentage
    FROM student_main
    UNION ALL
    SELECT 'Pell Recipient' AS status,
    SUM(CASE WHEN pell_recipient = 'Y' THEN 1 ELSE 0 END) * 100.0/ COUNT(*) AS percentage
    FROM student_main
    UNION ALL
    SELECT  'US Veteran' AS status,
    SUM(CASE WHEN  us_veteran = 'Y' THEN 1 ELSE 0 END) *100.0 / COUNT(*) AS percentage
    FROM student_main 
    
    '''
    return query_percentages
    
### Demo function call
demo_query_binary_indicators = binary_indicators()
demo_result_binary_indicators = pd.read_sql(demo_query_binary_indicators, conn)
demo_result_binary_indicators


# ### Run me!
# 
# Whether your solution is working or not, run the following code cell. It will load the proper results into memory and show the expected output for the demo cell above.

# In[12]:


### Run Me!!!
demo_result_binary_indicators_TRUE = utils.load_object_from_publicdata('demo_result_binary_indicators_TRUE')


#  
# 
# **The demo should display this output.**  
# 
# <div style="overflow-x:auto;">
#     <style>
#         table {
#             border-collapse: collapse;
#             margin: 15px 0;
#             font-size: 0.9em;
#             font-family: sans-serif;
#             width: auto;
#         }
#         th, td {
#             padding: 8px;
#             text-align: right;
#             border-bottom: 1px solid #ddd;
#         }
#         tr:hover {background-color: #f5f5f5;}
#     </style>
#     <table border="0" class="dataframe">
#   <thead>
#     <tr style="text-align: right;">
#       <th></th>
#       <th>status</th>
#       <th>percentage</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <th>0</th>
#       <td>US Citizen</td>
#       <td>88.60</td>
#     </tr>
#     <tr>
#       <th>1</th>
#       <td>US Resident</td>
#       <td>82.40</td>
#     </tr>
#     <tr>
#       <th>2</th>
#       <td>State Resident</td>
#       <td>81.20</td>
#     </tr>
#     <tr>
#       <th>3</th>
#       <td>Pell Recipient</td>
#       <td>25.60</td>
#     </tr>
#     <tr>
#       <th>4</th>
#       <td>US Veteran</td>
#       <td>11.20</td>
#     </tr>
#   </tbody>
# </table>
#     </div>
# 
# 
#  ---
#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for binary_indicators (exercise 1). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 
# 

# In[13]:


### Test Cell - Exercise 1  


from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load
from time import time

tracemalloc.start()
mem_start, peak_start = tracemalloc.get_traced_memory()
print(f"initial memory usage: {mem_start/1024/1024:.2f} MB")

# Load testing utility
with open('resource/asnlib/publicdata/execute_tests', 'rb') as f:
    executor = dill.load(f)

@run_with_timeout(error_threshold=200.0, warning_threshold=100.0)
@suppress_stdout
def execute_tests(**kwargs):
    return executor(**kwargs)


# Execute test
start_time = time()
passed, test_case_vars, e = execute_tests(func=plugins.sql_executor(binary_indicators),
              ex_name='binary_indicators',
              key=b'O0BU75J0b9vpmE9I87bfmsoeq8QjLtdkUmFw3nrTbWQ=', 
              n_iter=10)
# Assign test case vars for debugging
input_vars, original_input_vars, returned_output_vars, true_output_vars = test_case_vars
duration = time() - start_time
print(f"Test duration: {duration:.2f} seconds")
current_memory, peak_memory = tracemalloc.get_traced_memory()
print(f"memory after test: {current_memory/1024/1024:.2f} MB")
print(f"memory peak during test: {peak_memory/1024/1024:.2f} MB")
tracemalloc.stop()
if e: raise e
assert passed, 'The solution to binary_indicators did not pass the test.'

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ### Exercise 2: (1 points)
# **scholarship_payments**  
# 
# **Your task:** define `scholarship_payments` as follows:
# 
# Let's continue exploring the scholarship data. Write a SQL query to calculate the total amount paid out by each scholarship.
# 
# **Inputs**: 
# - None
# 
# **Return**:
# - A Python string containing a SQLite query that produces a table with 2 columns:
#   - `scholarship_code`: The 3-letter scholarship identifier
#   - `total_payment`: The sum of all `scholarship_payment` amounts made by that scholarship
#   - The `scholarship_code` column should be first and `total_payment` column second; the order of the rows is not important.
# 
# **Requirements**:
# - Query the `student_scholarship` table
# 

# In[14]:


### Solution - Exercise 2  
def scholarship_payments() -> str:
    query = '''
    SELECT scholarship_code,
    SUM(scholarship_payment) AS total_payment
    FROM
    student_scholarship
    GROUP BY scholarship_code
    
    '''
    
    return query

### Demo function call
demo_query_scholarship_payments = scholarship_payments()
demo_result_scholarship_payments = pd.read_sql(demo_query_scholarship_payments, conn)
demo_result_scholarship_payments


# ### Run me!
# 
# Whether your solution is working or not, run the following code cell. It will load the proper results into memory and show the expected output for the demo cell above.

# In[15]:


### Run Me!!!
demo_result_scholarship_payments_TRUE = utils.load_object_from_publicdata('demo_result_scholarship_payments_TRUE')


#  
# 
# **The demo should display this output.**  
# 
# <div style="overflow-x:auto;">
#     <style>
#         table {
#             border-collapse: collapse;
#             margin: 15px 0;
#             font-size: 0.9em;
#             font-family: sans-serif;
#             width: auto;
#         }
#         th, td {
#             padding: 8px;
#             text-align: right;
#             border-bottom: 1px solid #ddd;
#         }
#         tr:hover {background-color: #f5f5f5;}
#     </style>
#     <table border="0" class="dataframe">
#   <thead>
#     <tr style="text-align: right;">
#       <th></th>
#       <th>scholarship_code</th>
#       <th>total_payment</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <th>0</th>
#       <td>ALE</td>
#       <td>13738</td>
#     </tr>
#     <tr>
#       <th>1</th>
#       <td>BCI</td>
#       <td>51788</td>
#     </tr>
#     <tr>
#       <th>2</th>
#       <td>FEG</td>
#       <td>26333</td>
#     </tr>
#     <tr>
#       <th>3</th>
#       <td>FGA</td>
#       <td>128097</td>
#     </tr>
#     <tr>
#       <th>4</th>
#       <td>FRS</td>
#       <td>12500</td>
#     </tr>
#     <tr>
#       <th>5</th>
#       <td>GAM</td>
#       <td>71019</td>
#     </tr>
#     <tr>
#       <th>6</th>
#       <td>GVS</td>
#       <td>532829</td>
#     </tr>
#     <tr>
#       <th>7</th>
#       <td>KCJ</td>
#       <td>15708</td>
#     </tr>
#     <tr>
#       <th>8</th>
#       <td>PRE</td>
#       <td>1005649</td>
#     </tr>
#     <tr>
#       <th>9</th>
#       <td>USE</td>
#       <td>536667</td>
#     </tr>
#     <tr>
#       <th>10</th>
#       <td>WIM</td>
#       <td>6000</td>
#     </tr>
#   </tbody>
# </table>
#     </div>
# 
# 
#  ---
#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for scholarship_payments (exercise 2). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 
# 

# In[16]:


### Test Cell - Exercise 2  


from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load
from time import time

tracemalloc.start()
mem_start, peak_start = tracemalloc.get_traced_memory()
print(f"initial memory usage: {mem_start/1024/1024:.2f} MB")

# Load testing utility
with open('resource/asnlib/publicdata/execute_tests', 'rb') as f:
    executor = dill.load(f)

@run_with_timeout(error_threshold=200.0, warning_threshold=100.0)
@suppress_stdout
def execute_tests(**kwargs):
    return executor(**kwargs)


# Execute test
start_time = time()
passed, test_case_vars, e = execute_tests(func=plugins.sql_executor(scholarship_payments),
              ex_name='scholarship_payments',
              key=b'O0BU75J0b9vpmE9I87bfmsoeq8QjLtdkUmFw3nrTbWQ=', 
              n_iter=10)
# Assign test case vars for debugging
input_vars, original_input_vars, returned_output_vars, true_output_vars = test_case_vars
duration = time() - start_time
print(f"Test duration: {duration:.2f} seconds")
current_memory, peak_memory = tracemalloc.get_traced_memory()
print(f"memory after test: {current_memory/1024/1024:.2f} MB")
print(f"memory peak during test: {peak_memory/1024/1024:.2f} MB")
tracemalloc.stop()
if e: raise e
assert passed, 'The solution to scholarship_payments did not pass the test.'

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ### Exercise 3: (2 points)
# **avg_gpa_by_scholarship**  
# 
# **Your task:** define `avg_gpa_by_scholarship` as follows:
# 
# Write a SQL query to calculate the average semester GPA for students grouped by scholarship code.
# 
# **Inputs**: 
# - None
# 
# **Return**:
# - A Python string containing a SQLite query that produces a table with 2 columns:
#   - `scholarship_code`: The 3-letter scholarship identifier or 'NONE' for students without scholarships
#   - `avg_gpa`: The average semester GPA for students with that scholarship, rounded to 2 decimal places
#   - The results must be ordered by avg_gpa first and scholarship_code second.
# 
# **Requirements**:
# - Calculate the average of the `semester_gpa` with the alias `avg_gpa`
# - Use the following tables:
#   - `student_enrollment`
#   - `student_key`
#   - `student_scholarship`
# - Only include students that exist in both `student_enrollment` and `student_key`
# - Use the correct `JOIN` type when joining to `student_scholarship` so that students without scholarships are included
# - For students without a scholarship, use 'NONE' as their `scholarship_code` value
# - Sort results in descending order by `avg_gpa` 
# - Use `scholarship_code` as a tiebreaker (secondary sort) in ascending order for consistent results
# - Round the average GPA to 2 decimal places
# 
# **Hint**:
# - The `COALESCE` or `IFNULL` functions can be used to solve this exercise.
# 

# In[17]:


### Solution - Exercise 3  
def avg_gpa_by_scholarship() -> str:
    
    #LEFT JOIN to ensure students without scholarships are included in the "NONE" group
    query = '''
    
    SELECT 
    COALESCE(ss.scholarship_code, 'NONE') AS scholarship_code,
    ROUND(AVG(se.semester_gpa),2) AS avg_gpa
    FROM student_enrollment AS se
    JOIN student_key AS sk ON sk.student_id = se.student_id
    LEFT JOIN student_scholarship AS ss ON sk.finance_id = ss.finance_id
    GROUP BY ss.scholarship_code
    ORDER BY avg_gpa DESC, scholarship_code ASC
    
    '''
    return query

### Demo function call
demo_query_avg_gpa_by_scholarship = avg_gpa_by_scholarship()
demo_result_avg_gpa_by_scholarship = pd.read_sql(demo_query_avg_gpa_by_scholarship, conn)
demo_result_avg_gpa_by_scholarship


# ### Run me!
# 
# Whether your solution is working or not, run the following code cell. It will load the proper results into memory and show the expected output for the demo cell above.

# In[18]:


### Run Me!!!
demo_result_avg_gpa_by_scholarship_TRUE = utils.load_object_from_publicdata('demo_result_avg_gpa_by_scholarship_TRUE')


#  
# 
# **The demo should display this output.**  
# 
# <div style="overflow-x:auto;">
#     <style>
#         table {
#             border-collapse: collapse;
#             margin: 15px 0;
#             font-size: 0.9em;
#             font-family: sans-serif;
#             width: auto;
#         }
#         th, td {
#             padding: 8px;
#             text-align: right;
#             border-bottom: 1px solid #ddd;
#         }
#         tr:hover {background-color: #f5f5f5;}
#     </style>
#     <table border="0" class="dataframe">
#   <thead>
#     <tr style="text-align: right;">
#       <th></th>
#       <th>scholarship_code</th>
#       <th>avg_gpa</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <th>0</th>
#       <td>WIM</td>
#       <td>2.92</td>
#     </tr>
#     <tr>
#       <th>1</th>
#       <td>ALE</td>
#       <td>2.86</td>
#     </tr>
#     <tr>
#       <th>2</th>
#       <td>FEG</td>
#       <td>2.84</td>
#     </tr>
#     <tr>
#       <th>3</th>
#       <td>FRS</td>
#       <td>2.84</td>
#     </tr>
#     <tr>
#       <th>4</th>
#       <td>FGA</td>
#       <td>2.81</td>
#     </tr>
#     <tr>
#       <th>5</th>
#       <td>USE</td>
#       <td>2.81</td>
#     </tr>
#     <tr>
#       <th>6</th>
#       <td>KCJ</td>
#       <td>2.78</td>
#     </tr>
#     <tr>
#       <th>7</th>
#       <td>GVS</td>
#       <td>2.76</td>
#     </tr>
#     <tr>
#       <th>8</th>
#       <td>BCI</td>
#       <td>2.75</td>
#     </tr>
#     <tr>
#       <th>9</th>
#       <td>PRE</td>
#       <td>2.75</td>
#     </tr>
#     <tr>
#       <th>10</th>
#       <td>NONE</td>
#       <td>2.72</td>
#     </tr>
#     <tr>
#       <th>11</th>
#       <td>GAM</td>
#       <td>2.69</td>
#     </tr>
#   </tbody>
# </table>
#     </div>
# 
# 
#  ---
#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for avg_gpa_by_scholarship (exercise 3). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 
# 

# In[19]:


### Test Cell - Exercise 3  


from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load
from time import time

tracemalloc.start()
mem_start, peak_start = tracemalloc.get_traced_memory()
print(f"initial memory usage: {mem_start/1024/1024:.2f} MB")

# Load testing utility
with open('resource/asnlib/publicdata/execute_tests', 'rb') as f:
    executor = dill.load(f)

@run_with_timeout(error_threshold=200.0, warning_threshold=100.0)
@suppress_stdout
def execute_tests(**kwargs):
    return executor(**kwargs)


# Execute test
start_time = time()
passed, test_case_vars, e = execute_tests(func=plugins.sql_executor(avg_gpa_by_scholarship),
              ex_name='avg_gpa_by_scholarship',
              key=b'O0BU75J0b9vpmE9I87bfmsoeq8QjLtdkUmFw3nrTbWQ=', 
              n_iter=10)
# Assign test case vars for debugging
input_vars, original_input_vars, returned_output_vars, true_output_vars = test_case_vars
duration = time() - start_time
print(f"Test duration: {duration:.2f} seconds")
current_memory, peak_memory = tracemalloc.get_traced_memory()
print(f"memory after test: {current_memory/1024/1024:.2f} MB")
print(f"memory peak during test: {peak_memory/1024/1024:.2f} MB")
tracemalloc.stop()
if e: raise e
assert passed, 'The solution to avg_gpa_by_scholarship did not pass the test.'

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ### Exercise 4: (3 points)
# **active_scholarships**  
# 
# **Your task:** define `active_scholarships` as follows:
# 
# Write a SQL query to generate a comprehensive report of all currently active scholarships and their eligibility rules.
# 
# **Inputs**: 
# - None
# 
# **Return**:
# - A Python string containing a SQLite query that produces a table with the following columns:
#   - `scholarship_description`: Description of the scholarship
#   - `major_description`: Description of the eligible major
#   - `min_gpa`: Minimum GPA requirement
#   - `gender`: Gender requirement (if applicable)
#   - `pell_recipient`: Pell recipient status requirement
#   - `us_veteran`: US veteran status requirement
#   - `us_citizen`: US citizenship requirement
#   - `us_resident`: US residency requirement
#   - `state_resident`: State residency requirement
#   - `amount`: Scholarship award amount
#   - The columns must be ordered as listed above; the order of rows is not important.
# 
# **Requirements**:
# - Query the following tables:
#   - `scholarship_rules`
#   - `scholarship_crosswalk`
#   - `major_crosswalk`
# - Include only scholarships where the scholarship is active, i.e. `scholarship_active = 'Y'`
# - Use the current `scholarship_description` that matches the activation date in `scholarship_rules`
# - For major descriptions:
#   - Use the most recent `major_description` based on `activation_date` for each `major_code`
#   - If a scholarship is not limited to a specific major, `major_description` should be NULL
# 
# **Hints**:
# - You will need a subquery or CTE to find the most recent activation date for each major
# - Use appropriate joins to ensure scholarships without major requirements are still included (i.e. we want to include entries where `scholarship_rules.major_code` could be null)
# 

# In[20]:


### Solution - Exercise 4  
def active_scholarships() -> str:
    query = '''
        WITH LatestMajors AS (
        SELECT major_code, major_description, MAX(activation_date) 
        FROM major_crosswalk
        GROUP BY major_code)
        
        SELECT     
           sc.scholarship_description,
           lm.major_description,
           sr.min_gpa,
           sr.gender,
           sr.pell_recipient,
           sr.us_veteran,
           sr.us_citizen,
           sr.us_resident,
           sr.state_resident,
           sr.amount
    FROM scholarship_rules as sr
    JOIN scholarship_crosswalk as sc 
    ON sc.id = sr.id
    AND sc.activation_date = sr.activation_date
    LEFT JOIN LatestMajors as lm 
    ON lm.major_code = sr.major_code 
    WHERE sr.scholarship_active = 'Y'
  
             
    '''
    return query

### Demo function call
demo_query_active_scholarships = active_scholarships()
demo_result_active_scholarships = pd.read_sql(demo_query_active_scholarships, conn)
demo_result_active_scholarships


# ### Run me!
# 
# Whether your solution is working or not, run the following code cell. It will load the proper results into memory and show the expected output for the demo cell above.

# In[21]:


### Run Me!!!
demo_result_active_scholarships_TRUE = utils.load_object_from_publicdata('demo_result_active_scholarships_TRUE')


#  
# 
# **The demo should display this output.**  
# 
# <div style="overflow-x:auto;">
#     <style>
#         table {
#             border-collapse: collapse;
#             margin: 15px 0;
#             font-size: 0.9em;
#             font-family: sans-serif;
#             width: auto;
#         }
#         th, td {
#             padding: 8px;
#             text-align: right;
#             border-bottom: 1px solid #ddd;
#         }
#         tr:hover {background-color: #f5f5f5;}
#     </style>
#     <table border="0" class="dataframe">
#   <thead>
#     <tr style="text-align: right;">
#       <th></th>
#       <th>scholarship_description</th>
#       <th>major_description</th>
#       <th>min_gpa</th>
#       <th>gender</th>
#       <th>pell_recipient</th>
#       <th>us_veteran</th>
#       <th>us_citizen</th>
#       <th>us_resident</th>
#       <th>state_resident</th>
#       <th>amount</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <th>0</th>
#       <td>Georgia Veterans Fund</td>
#       <td>None</td>
#       <td>3.00</td>
#       <td>None</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>Y</td>
#       <td>Y</td>
#       <td>Y</td>
#       <td>2500</td>
#     </tr>
#     <tr>
#       <th>1</th>
#       <td>University Student Excellence Award</td>
#       <td>None</td>
#       <td>3.70</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>2000</td>
#     </tr>
#     <tr>
#       <th>2</th>
#       <td>Women in Mathematics Award</td>
#       <td>Mathematics</td>
#       <td>3.50</td>
#       <td>F</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>3000</td>
#     </tr>
#     <tr>
#       <th>3</th>
#       <td>Future Educators of Georgia Scholarship</td>
#       <td>Education</td>
#       <td>3.50</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>2500</td>
#     </tr>
#     <tr>
#       <th>4</th>
#       <td>First Generation Achievement Scholarship</td>
#       <td>None</td>
#       <td>3.50</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>1500</td>
#     </tr>
#     <tr>
#       <th>5</th>
#       <td>Pell Recipients Excellence Fund</td>
#       <td>None</td>
#       <td>3.00</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>Y</td>
#       <td>None</td>
#       <td>1500</td>
#     </tr>
#     <tr>
#       <th>6</th>
#       <td>Chris Kinkade Criminal Justice Fund</td>
#       <td>Criminal Justice</td>
#       <td>3.50</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>Y</td>
#       <td>Y</td>
#       <td>2500</td>
#     </tr>
#     <tr>
#       <th>7</th>
#       <td>Georgia Aquarium Marine Biology Fund</td>
#       <td>Marine Biology</td>
#       <td>3.00</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>2500</td>
#     </tr>
#     <tr>
#       <th>8</th>
#       <td>My Brother's Keeper Fund</td>
#       <td>None</td>
#       <td>3.50</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>None</td>
#       <td>N</td>
#       <td>N</td>
#       <td>N</td>
#       <td>1000</td>
#     </tr>
#     <tr>
#       <th>9</th>
#       <td>Audre Lorde English Studies Award</td>
#       <td>English</td>
#       <td>3.75</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>None</td>
#       <td>2500</td>
#     </tr>
#     <tr>
#       <th>10</th>
#       <td>Bell Center for International Studies Scholarship</td>
#       <td>International Relations</td>
#       <td>3.50</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>Y</td>
#       <td>None</td>
#       <td>2500</td>
#     </tr>
#     <tr>
#       <th>11</th>
#       <td>Feingold Institute for Religious Studies Award</td>
#       <td>Religious Studies</td>
#       <td>3.75</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>Y</td>
#       <td>None</td>
#       <td>2500</td>
#     </tr>
#     <tr>
#       <th>12</th>
#       <td>Professor Richard Vuduc Analytics Dreamers Scholarship</td>
#       <td>Analytics</td>
#       <td>3.75</td>
#       <td>None</td>
#       <td>None</td>
#       <td>None</td>
#       <td>Y</td>
#       <td>Y</td>
#       <td>Y</td>
#       <td>3000</td>
#     </tr>
#   </tbody>
# </table>
#     </div>
# 
# 
#  ---
#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for active_scholarships (exercise 4). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 
# 

# In[22]:


### Test Cell - Exercise 4  


from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load
from time import time

tracemalloc.start()
mem_start, peak_start = tracemalloc.get_traced_memory()
print(f"initial memory usage: {mem_start/1024/1024:.2f} MB")

# Load testing utility
with open('resource/asnlib/publicdata/execute_tests', 'rb') as f:
    executor = dill.load(f)

@run_with_timeout(error_threshold=200.0, warning_threshold=100.0)
@suppress_stdout
def execute_tests(**kwargs):
    return executor(**kwargs)


# Execute test
start_time = time()
passed, test_case_vars, e = execute_tests(func=plugins.sql_executor(active_scholarships),
              ex_name='active_scholarships',
              key=b'O0BU75J0b9vpmE9I87bfmsoeq8QjLtdkUmFw3nrTbWQ=', 
              n_iter=10)
# Assign test case vars for debugging
input_vars, original_input_vars, returned_output_vars, true_output_vars = test_case_vars
duration = time() - start_time
print(f"Test duration: {duration:.2f} seconds")
current_memory, peak_memory = tracemalloc.get_traced_memory()
print(f"memory after test: {current_memory/1024/1024:.2f} MB")
print(f"memory peak during test: {peak_memory/1024/1024:.2f} MB")
tracemalloc.stop()
if e: raise e
assert passed, 'The solution to active_scholarships did not pass the test.'

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ### Exercise 5: (3 points)
# **grad_retention_inds**  
# 
# **Your task:** define `grad_retention_inds` as follows:
# 
# Write a SQL query to calculate retention and graduation indicators for each student.
# 
# **Inputs**: 
# - None
# 
# **Return**:
# - A Python string containing a SQLite query that produces a table with 3 columns:
#   - `student_id`: The unique identifier for each student
#   - `retention_ind`: Binary indicator (1 or 0) showing whether a student was retained
#   - `graduation_ind`: Binary indicator (1 or 0) showing whether a student has graduated
#   - The columns must be ordered as listed above; the order of rows is not important.
# 
# 
# **Requirements**:
# - Query the following tables:
#   - `student_enrollment`
#   - `graduation`
# - A student is considered *retained* if they are enrolled *EXACTLY* one year after their first term
# - A student has graduated if they have a `grad_level` of 'B' and a `grad_status` of 'A' in the graduation table
# - Term format: The first 4 digits represent the year, and the last 2 digits represent the starting month
# 
# **Hints**:
# - You'll need to identify each student's first enrollment term
# - To calculate retention, you'll need to add 100 to the first term (representing one year later)
# - Use CAST() to convert string values to integers when performing arithmetic operations
#   - Example: `CAST('202001' AS INTEGER)` would become an integer value of `202001`
#   - Documentation: [SQLite CAST function](https://www.sqlite.org/lang_expr.html#castexpr)
# - Use a subquery or CTE to determine each student's first term
# - Binary indicators can be created by using MAX() with CASE statements
# 

# In[23]:


### Solution - Exercise 5  
def grad_retention_inds() -> str:
    query = '''
    SELECT
        se.student_id,
        MAX(CASE WHEN CAST(se.term AS integer) = (
        SELECT 
        MIN(CAST(se2.term AS integer))
        FROM student_enrollment AS se2
        WHERE se2.student_id = se.student_id) + 100 THEN 1 ELSE 0 END) AS retention_ind,
        MAX(CASE WHEN g.grad_level = 'B' AND  g.grad_status = 'A' THEN 1 ELSE 0 END) AS graduation_ind
        
    FROM student_enrollment AS se    
    LEFT JOIN graduation AS g 
    ON se.student_id = g.student_id
    GROUP BY se.student_id
   
    '''
    return query

### Demo function call
demo_query_grad_retention_inds = grad_retention_inds()
demo_result_grad_retention_inds = pd.read_sql(demo_query_grad_retention_inds, conn)
demo_result_grad_retention_inds.head(10)


# ### Run me!
# 
# Whether your solution is working or not, run the following code cell. It will load the proper results into memory and show the expected output for the demo cell above.

# In[24]:


### Run Me!!!
demo_result_grad_retention_inds_TRUE = utils.load_object_from_publicdata('demo_result_grad_retention_inds_TRUE')


#  
# 
# **The demo should display this output.**  
# 
# <div style="overflow-x:auto;">
#     <style>
#         table {
#             border-collapse: collapse;
#             margin: 15px 0;
#             font-size: 0.9em;
#             font-family: sans-serif;
#             width: auto;
#         }
#         th, td {
#             padding: 8px;
#             text-align: right;
#             border-bottom: 1px solid #ddd;
#         }
#         tr:hover {background-color: #f5f5f5;}
#     </style>
#     <table border="0" class="dataframe">
#   <thead>
#     <tr style="text-align: right;">
#       <th></th>
#       <th>student_id</th>
#       <th>retention_ind</th>
#       <th>graduation_ind</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <th>0</th>
#       <td>100052749</td>
#       <td>0</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>1</th>
#       <td>100636982</td>
#       <td>0</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>2</th>
#       <td>102689054</td>
#       <td>0</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>3</th>
#       <td>103503531</td>
#       <td>0</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>4</th>
#       <td>103972552</td>
#       <td>0</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>5</th>
#       <td>103975474</td>
#       <td>1</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>6</th>
#       <td>107116054</td>
#       <td>0</td>
#       <td>1</td>
#     </tr>
#     <tr>
#       <th>7</th>
#       <td>107372067</td>
#       <td>0</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>8</th>
#       <td>108283090</td>
#       <td>1</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>9</th>
#       <td>113524474</td>
#       <td>0</td>
#       <td>0</td>
#     </tr>
#   </tbody>
# </table>
#     </div>
# 
# 
#  ---
#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for grad_retention_inds (exercise 5). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 
# 

# In[25]:


### Test Cell - Exercise 5  


from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load
from time import time

tracemalloc.start()
mem_start, peak_start = tracemalloc.get_traced_memory()
print(f"initial memory usage: {mem_start/1024/1024:.2f} MB")

# Load testing utility
with open('resource/asnlib/publicdata/execute_tests', 'rb') as f:
    executor = dill.load(f)

@run_with_timeout(error_threshold=200.0, warning_threshold=100.0)
@suppress_stdout
def execute_tests(**kwargs):
    return executor(**kwargs)


# Execute test
start_time = time()
passed, test_case_vars, e = execute_tests(func=plugins.sql_executor(grad_retention_inds),
              ex_name='grad_retention_inds',
              key=b'O0BU75J0b9vpmE9I87bfmsoeq8QjLtdkUmFw3nrTbWQ=', 
              n_iter=10)
# Assign test case vars for debugging
input_vars, original_input_vars, returned_output_vars, true_output_vars = test_case_vars
duration = time() - start_time
print(f"Test duration: {duration:.2f} seconds")
current_memory, peak_memory = tracemalloc.get_traced_memory()
print(f"memory after test: {current_memory/1024/1024:.2f} MB")
print(f"memory peak during test: {peak_memory/1024/1024:.2f} MB")
tracemalloc.stop()
if e: raise e
assert passed, 'The solution to grad_retention_inds did not pass the test.'

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# # Part 2: Data Deidentification with Pandas and Numpy
#  
# In this section, you will shift your focus from exploring and compiling data to deidentifying the student records. The consolidated dataset has been built and loaded for you, as part of the notebook starter code above. It is available in the environment as `df_consolidated_data`.

# ### Run me!
# 
# Whether you solved the previous exercise or not, run the following code cell. It will load the proper results into memory for the next exercise.

# In[26]:


df_consolidated_data = utils.load_object_from_publicdata('df_consolidated_data.dill')


# ### Exercise 6: (2 points)
# **rename_recpt_columns**  
# 
# **Your task:** define `rename_recpt_columns` as follows:
# 
# Standardize the naming convention for scholarship recipient columns in a DataFrame.
# 
# **Inputs**: 
# - `df`: A DataFrame containing student records with columns that include the substring 'recpt'
# 
# **Return**:
# - A new DataFrame with standardized column names for scholarship recipient fields
# 
# **Requirements**:
# - Identify all columns in the DataFrame that contain the substring 'recpt'
# - Sort these columns alphabetically
# - Rename each column using the pattern 'scholarship_X_recpt', where X is a number starting at 1
#   - The first column in the alphabetically sorted list gets named 'scholarship_1_recpt'
#   - The second column gets named 'scholarship_2_recpt', and so on
# - Preserve the original order of all columns in the DataFrame
# - Do not modify the input DataFrame
# - Do not use SQLite
# 
# **Example**:
# 
# Given a DataFrame with columns containing 'recpt' in their names:
# 
# ```
# ['student_id', ...,  'b_recpt', 'a_recpt', ...]
# ```
# 
# The output DataFrame should have the following columns:
# ```
# ['student_id', ..., 'scholarship_2_recpt', 'scholarship_1_recpt', ...]
# ```
# 
# Note: In this example, 'a_recpt' becomes 'scholarship_1_recpt', 'b_recpt' becomes 'scholarship_2_recpt', based on alphabetical sorting, but the original order is preserved.
# 
# **Hint**:
# - The `enumerate()` function can be used to generate numbers for the new column names. See [the documentation](https://docs.python.org/3/library/functions.html#enumerate) for details.
# 
# **Note**: 
# - **The demo output below only returns the column names of the renamed DataFrame** and not the entire DataFrame.
# 

# In[27]:


### Solution - Exercise 6  
def rename_recpt_columns(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()
    recpt_cols = [col for col in df_copy.columns if 'recpt' in col]
    recpt_cols.sort()
    
    name_map ={}
    for i, col in enumerate(recpt_cols, start = 1):
        
        name_map[col] = f"scholarship_{i}_recpt"
        
    df_copy = df_copy.rename(columns = name_map)
        
   
    return df_copy
   
### Demo function call
renamed_df = rename_recpt_columns(df_consolidated_data)
print(renamed_df.columns)


# ### Run me!
# 
# Whether your solution is working or not, run the following code cell. It will load the proper results into memory and show the expected output for the demo cell above.

# In[28]:


### Run Me!!!
demo_result_rename_recpt_columns_TRUE = utils.load_object_from_publicdata('demo_result_rename_recpt_columns_TRUE')


#  
# 
# **The demo should display this printed output.**
# ```
# Index(['student_id', 'term', 'major_code', 'semester_hours_attempted',
#        'semester_hours_earned', 'semester_gpa', 'cumulative_hours_earned',
#        'cumulative_gpa', 'gender', 'ethnicity', 'state', 'us_citizen',
#        'us_resident', 'state_resident', 'pell_recipient', 'us_veteran',
#        'scholarship_7_recpt', 'scholarship_12_recpt', 'scholarship_13_recpt',
#        'scholarship_3_recpt', 'scholarship_4_recpt', 'scholarship_11_recpt',
#        'scholarship_8_recpt', 'scholarship_6_recpt', 'scholarship_9_recpt',
#        'scholarship_1_recpt', 'scholarship_2_recpt', 'scholarship_5_recpt',
#        'scholarship_10_recpt', 'retention_ind', 'graduation_ind'],
#       dtype='object')
# ```
# 
# 
#  ---
#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for rename_recpt_columns (exercise 6). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 
# 

# In[29]:


### Test Cell - Exercise 6  


from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load
from time import time

tracemalloc.start()
mem_start, peak_start = tracemalloc.get_traced_memory()
print(f"initial memory usage: {mem_start/1024/1024:.2f} MB")

# Load testing utility
with open('resource/asnlib/publicdata/execute_tests', 'rb') as f:
    executor = dill.load(f)

@run_with_timeout(error_threshold=200.0, warning_threshold=100.0)
@suppress_stdout
def execute_tests(**kwargs):
    return executor(**kwargs)


# Execute test
start_time = time()
passed, test_case_vars, e = execute_tests(func=plugins.sqlite_blocker(rename_recpt_columns),
              ex_name='rename_recpt_columns',
              key=b'O0BU75J0b9vpmE9I87bfmsoeq8QjLtdkUmFw3nrTbWQ=', 
              n_iter=20)
# Assign test case vars for debugging
input_vars, original_input_vars, returned_output_vars, true_output_vars = test_case_vars
duration = time() - start_time
print(f"Test duration: {duration:.2f} seconds")
current_memory, peak_memory = tracemalloc.get_traced_memory()
print(f"memory after test: {current_memory/1024/1024:.2f} MB")
print(f"memory peak during test: {peak_memory/1024/1024:.2f} MB")
tracemalloc.stop()
if e: raise e
assert passed, 'The solution to rename_recpt_columns did not pass the test.'

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ### Run me!
# 
# Whether you solved the previous exercise or not, run the following code cell. It will load the proper results into memory for the next exercise.

# In[30]:


renamed_df = utils.load_object_from_publicdata('renamed_df.dill')


# ### Exercise 7: (1 points)
# **adjust_term**  
# 
# **Your task:** define `adjust_term` as follows:
# 
# Anonymize student data by shifting the year component of all term values by a specified number of years.
# 
# **Inputs**: 
# - `df`: A DataFrame containing student records with a 'term' column
# - `n_years`: An integer specifying how many years to shift (can be positive or negative)
# 
# **Return**:
# - A new DataFrame with the year component of all term values adjusted
# 
# **Requirements**:
# - The 'term' column format is 'YYYYMM' where:
#   - The first 4 digits (YYYY) represent the year
#   - The last 2 digits (MM) represent the starting month
# - Adjust only the year component to each term value
# - The data frame you return must have the same data types as the input data frame
# - Do not modify the original input DataFrame
# - Do not use SQLite
# 
# **Example**:
# 
# Given an example `df` and `n_years = 1`:
# 
# Input:
# 
# 
# |    |   student_id |   term |
# |---:|-------------:|-------:|
# |  0 |            1 | 201801 |
# |  1 |            2 | 201805 |
# 
# 
# 
# Output:
# 
# 
# |    |   student_id |   term |
# |---:|-------------:|-------:|
# |  0 |            1 | 201901 |
# |  1 |            2 | 201905 |
# 
# 
# 
# 

# In[31]:


### Solution - Exercise 7  
def adjust_term(df: pd.DataFrame, n_years: int) -> pd.DataFrame:
 
    df_new = df.copy()
    df_new = df_new.dropna(subset=['term'])
    
    # 1. Convert to integer to handle any floats or strings uniformly
    # (e.g., '201905.0' -> 201905)
    vals = df_new['term'].astype(float).astype(int)
    
    # 2. Use Math to isolate components
    # Year is the quotient of dividing by 100 (201905 // 100 = 2019)
    # Month is the remainder (201905 % 100 = 05)
    year = vals // 100
    month = vals % 100
    
    shifted_year = year + n_years
    
    # 3. Reconstruct: (Year * 100) + Month
    # This guarantees the YYYYMM format as a number
    adjusted_numeric = (shifted_year * 100) + month
    
    # 4. Final cast back to original type
    df_new['term'] = adjusted_numeric.astype(df['term'].dtype)
    
    return df_new
    
    
    

### Demo function call
demo_result_adjust_term = adjust_term(renamed_df, 2)
demo_result_adjust_term[["student_id", "term"]].head(10)


# ### Run me!
# 
# Whether your solution is working or not, run the following code cell. It will load the proper results into memory and show the expected output for the demo cell above.

# In[32]:


### Run Me!!!
demo_result_adjust_term_TRUE = utils.load_object_from_publicdata('demo_result_adjust_term_TRUE')


#  
# 
# **The demo should display this output.**  
# 
# <div style="overflow-x:auto;">
#     <style>
#         table {
#             border-collapse: collapse;
#             margin: 15px 0;
#             font-size: 0.9em;
#             font-family: sans-serif;
#             width: auto;
#         }
#         th, td {
#             padding: 8px;
#             text-align: right;
#             border-bottom: 1px solid #ddd;
#         }
#         tr:hover {background-color: #f5f5f5;}
#     </style>
#     <table border="0" class="dataframe">
#   <thead>
#     <tr style="text-align: right;">
#       <th></th>
#       <th>student_id</th>
#       <th>term</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <th>0</th>
#       <td>100052749</td>
#       <td>201901</td>
#     </tr>
#     <tr>
#       <th>1</th>
#       <td>100052749</td>
#       <td>201905</td>
#     </tr>
#     <tr>
#       <th>2</th>
#       <td>100052749</td>
#       <td>201908</td>
#     </tr>
#     <tr>
#       <th>3</th>
#       <td>100636982</td>
#       <td>201701</td>
#     </tr>
#     <tr>
#       <th>4</th>
#       <td>100636982</td>
#       <td>201708</td>
#     </tr>
#     <tr>
#       <th>5</th>
#       <td>100636982</td>
#       <td>201901</td>
#     </tr>
#     <tr>
#       <th>6</th>
#       <td>100636982</td>
#       <td>201905</td>
#     </tr>
#     <tr>
#       <th>7</th>
#       <td>100636982</td>
#       <td>201908</td>
#     </tr>
#     <tr>
#       <th>8</th>
#       <td>100636982</td>
#       <td>202201</td>
#     </tr>
#     <tr>
#       <th>9</th>
#       <td>100636982</td>
#       <td>202205</td>
#     </tr>
#   </tbody>
# </table>
#     </div>
# 
# 
#  ---
#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for adjust_term (exercise 7). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 
# 

# In[33]:


### Test Cell - Exercise 7  


from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load
from time import time

tracemalloc.start()
mem_start, peak_start = tracemalloc.get_traced_memory()
print(f"initial memory usage: {mem_start/1024/1024:.2f} MB")

# Load testing utility
with open('resource/asnlib/publicdata/execute_tests', 'rb') as f:
    executor = dill.load(f)

@run_with_timeout(error_threshold=200.0, warning_threshold=100.0)
@suppress_stdout
def execute_tests(**kwargs):
    return executor(**kwargs)


# Execute test
start_time = time()
passed, test_case_vars, e = execute_tests(func=plugins.sqlite_blocker(adjust_term),
              ex_name='adjust_term',
              key=b'O0BU75J0b9vpmE9I87bfmsoeq8QjLtdkUmFw3nrTbWQ=', 
              n_iter=20)
# Assign test case vars for debugging
input_vars, original_input_vars, returned_output_vars, true_output_vars = test_case_vars
duration = time() - start_time
print(f"Test duration: {duration:.2f} seconds")
current_memory, peak_memory = tracemalloc.get_traced_memory()
print(f"memory after test: {current_memory/1024/1024:.2f} MB")
print(f"memory peak during test: {peak_memory/1024/1024:.2f} MB")
tracemalloc.stop()
if e: raise e
assert passed, 'The solution to adjust_term did not pass the test.'

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ### Run me!
# 
# Whether you solved the previous exercise or not, run the following code cell. It will load the proper results into memory for the next exercise.

# In[ ]:


new_term_df = utils.load_object_from_publicdata('new_term_df.dill')


# ### Exercise 8: (2 points)
# **generate_fake_ids**  
# 
# **Your task:** define `generate_fake_ids` as follows:
# 
# Create anonymized student identifiers to protect student privacy in the dataset.
# 
# **Inputs**: 
# - `df`: A DataFrame containing student records with a `student_id` column
# 
# **Return**:
# - A new DataFrame where the `student_id` column has been replaced with an `anon_id` column containing anonymized identifiers
# 
# **Requirements**:
# - Use the provided `generate_md5_hash` helper function to create anonymized IDs
#   - This function takes a student_id as input and returns a hashed identifier
# - Replace the 'student_id' column with a new 'anon_id' column containing the hashed identifiers
# - Maintain the same column ordering as the input DataFrame (with 'anon_id' in the same position as 'student_id' was)
# - If the 'student_id' column does not exist in the input, return the DataFrame unchanged
# - Do not modify the original input DataFrame
# - Do not use SQLite
# 
# **Note**: The `generate_md5_hash` function is already implemented and available for you to use
# 
# ---
# We have defined a **helper function**, `generate_md5_hash` as follows:  
# 
# Outputs an MD5 hash for a given original_id input.

# In[ ]:


### Helper Function
def generate_md5_hash(original_id) -> str:
    return hashlib.md5(str(original_id).encode()).hexdigest()

### Solution - Exercise 8  
def generate_fake_ids(df: pd.DataFrame) -> pd.DataFrame:
    
    if 'student_id' not in df.columns:
        return df
    
    df_copy = df.copy(deep=True)
    
    if 'anon_id' in df_copy:
        df_copy.drop(columns = 'anon_id', inplace = True)
    
    #Get the current column index
    column_index = df_copy.columns.get_loc('student_id')
    
    #Apply function to generate fake ids
   
    anon_vals = df_copy['student_id'].apply(generate_md5_hash)
    
    #Insert 'anon_id' at the same position and remove 'student_id'
    df_copy.insert(column_index, 'anon_id', anon_vals )
                       
    df_copy.drop(columns=['student_id'], inplace = True)
    return df_copy


### Demo function call
demo_result_generate_fake_ids = generate_fake_ids(new_term_df)
demo_result_generate_fake_ids[["anon_id"]].head(10)


# ### Run me!
# 
# Whether your solution is working or not, run the following code cell. It will load the proper results into memory and show the expected output for the demo cell above.

# In[ ]:


### Run Me!!!
demo_result_generate_fake_ids_TRUE = utils.load_object_from_publicdata('demo_result_generate_fake_ids_TRUE')


#  
# 
# **The demo should display this output.**  
# 
# <div style="overflow-x:auto;">
#     <style>
#         table {
#             border-collapse: collapse;
#             margin: 15px 0;
#             font-size: 0.9em;
#             font-family: sans-serif;
#             width: auto;
#         }
#         th, td {
#             padding: 8px;
#             text-align: right;
#             border-bottom: 1px solid #ddd;
#         }
#         tr:hover {background-color: #f5f5f5;}
#     </style>
#     <table border="0" class="dataframe">
#   <thead>
#     <tr style="text-align: right;">
#       <th></th>
#       <th>anon_id</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <th>0</th>
#       <td>9ee43c210f34e3f962279d84d72633d6</td>
#     </tr>
#     <tr>
#       <th>1</th>
#       <td>9ee43c210f34e3f962279d84d72633d6</td>
#     </tr>
#     <tr>
#       <th>2</th>
#       <td>9ee43c210f34e3f962279d84d72633d6</td>
#     </tr>
#     <tr>
#       <th>3</th>
#       <td>06dff90a4976f6fa8c9abc1f698e27ee</td>
#     </tr>
#     <tr>
#       <th>4</th>
#       <td>06dff90a4976f6fa8c9abc1f698e27ee</td>
#     </tr>
#     <tr>
#       <th>5</th>
#       <td>06dff90a4976f6fa8c9abc1f698e27ee</td>
#     </tr>
#     <tr>
#       <th>6</th>
#       <td>06dff90a4976f6fa8c9abc1f698e27ee</td>
#     </tr>
#     <tr>
#       <th>7</th>
#       <td>06dff90a4976f6fa8c9abc1f698e27ee</td>
#     </tr>
#     <tr>
#       <th>8</th>
#       <td>06dff90a4976f6fa8c9abc1f698e27ee</td>
#     </tr>
#     <tr>
#       <th>9</th>
#       <td>06dff90a4976f6fa8c9abc1f698e27ee</td>
#     </tr>
#   </tbody>
# </table>
#     </div>
# 
# 
#  ---
#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for generate_fake_ids (exercise 8). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 
# 

# In[ ]:


### Test Cell - Exercise 8  


from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load
from time import time

tracemalloc.start()
mem_start, peak_start = tracemalloc.get_traced_memory()
print(f"initial memory usage: {mem_start/1024/1024:.2f} MB")

# Load testing utility
with open('resource/asnlib/publicdata/execute_tests', 'rb') as f:
    executor = dill.load(f)

@run_with_timeout(error_threshold=200.0, warning_threshold=100.0)
@suppress_stdout
def execute_tests(**kwargs):
    return executor(**kwargs)


# Execute test
start_time = time()
passed, test_case_vars, e = execute_tests(func=plugins.sqlite_blocker(generate_fake_ids),
              ex_name='generate_fake_ids',
              key=b'O0BU75J0b9vpmE9I87bfmsoeq8QjLtdkUmFw3nrTbWQ=', 
              n_iter=20)
# Assign test case vars for debugging
input_vars, original_input_vars, returned_output_vars, true_output_vars = test_case_vars
duration = time() - start_time
print(f"Test duration: {duration:.2f} seconds")
current_memory, peak_memory = tracemalloc.get_traced_memory()
print(f"memory after test: {current_memory/1024/1024:.2f} MB")
print(f"memory peak during test: {peak_memory/1024/1024:.2f} MB")
tracemalloc.stop()
if e: raise e
assert passed, 'The solution to generate_fake_ids did not pass the test.'

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ### Run me!
# 
# Whether you solved the previous exercise or not, run the following code cell. It will load the proper results into memory for the next exercise.

# In[33]:


student_ids_df = utils.load_object_from_publicdata('student_ids_df.dill')


# ### Exercise 9: (2 points)
# **deidentify_columns**  
# 
# **Your task:** define `deidentify_columns` as follows:
# 
# Standardize and deidentify values in categorical columns by replacing original values with generic identifiers.
# 
# **Inputs**: 
# - `df`: A DataFrame containing student records
# - `columns`: A list of column names whose values should be deidentified
# 
# **Return**:
# - A new DataFrame with standardized values in the specified columns
# 
# **Requirements**:
# - For each specified column:
#   1. Identify all unique values in the column
#   2. Sort these unique values alphabetically
#   3. Replace each value with a new identifier following the pattern `column_name_X`
#      - Where `column_name` is the original column name
#      - And `X` is a number starting at 1, corresponding to the position in the sorted list
# - Preserve the original column order of the DataFrame
# - Do not modify the original input DataFrame
# - Do not use SQLite
# 
# **Example**:
# 
# Given a DataFrame with a `gender` column containing values `F` and `M`:
# 
# Before:
# ```
#    student_id  gender  age
# 0          1       F   21
# 1          2       M   19
# 2          3       F   22
# ```
# 
# After `deidentify_columns(df, ['gender'])`:
# ```
#    student_id     gender  age
# 0          1  gender_1   21
# 1          2  gender_2   19
# 2          3  gender_1   22
# ```
# 
# **Hint**:
# - The pandas Series.map() function is useful for replacing values based on a dictionary. See the documentation for more information: [pandas.Series.map](https://pandas.pydata.org/docs/reference/api/pandas.Series.map.html)
# - The `enumerate()` function can be used to generate numbers for the new identifiers. See the documentation for more information: [Python enumerate()](https://docs.python.org/3/library/functions.html#enumerate)
# 

# In[49]:


### Solution - Exercise 9  
def deidentify_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    df_copy = df.copy()
    
    existing_cols = [col for col in columns if col in df_copy.columns]
    
    for col in existing_cols:
        unique_vals = sorted(df_copy[col].unique())
        
        val_map = {}
        for i, val in enumerate(unique_vals, start=1):
            val_map[val] = f"{col}_{i}"
    
        df_copy[col] = df_copy[col].map(val_map)
                             
    return df_copy
        
        


### Demo function call
target_columns = ['major_code', 'gender', 'ethnicity', 'state']
demo_result_deidentify_columns = deidentify_columns(student_ids_df, target_columns)
demo_result_deidentify_columns[target_columns].head(10)


# ### Run me!
# 
# Whether your solution is working or not, run the following code cell. It will load the proper results into memory and show the expected output for the demo cell above.

# In[53]:


### Run Me!!!
demo_result_deidentify_columns_TRUE = utils.load_object_from_publicdata('demo_result_deidentify_columns_TRUE')


#  
# 
# **The demo should display this output.**  
# 
# <div style="overflow-x:auto;">
#     <style>
#         table {
#             border-collapse: collapse;
#             margin: 15px 0;
#             font-size: 0.9em;
#             font-family: sans-serif;
#             width: auto;
#         }
#         th, td {
#             padding: 8px;
#             text-align: right;
#             border-bottom: 1px solid #ddd;
#         }
#         tr:hover {background-color: #f5f5f5;}
#     </style>
#     <table border="0" class="dataframe">
#   <thead>
#     <tr style="text-align: right;">
#       <th></th>
#       <th>major_code</th>
#       <th>gender</th>
#       <th>ethnicity</th>
#       <th>state</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <th>0</th>
#       <td>major_code_47</td>
#       <td>gender_1</td>
#       <td>ethnicity_5</td>
#       <td>state_25</td>
#     </tr>
#     <tr>
#       <th>1</th>
#       <td>major_code_47</td>
#       <td>gender_1</td>
#       <td>ethnicity_5</td>
#       <td>state_25</td>
#     </tr>
#     <tr>
#       <th>2</th>
#       <td>major_code_47</td>
#       <td>gender_1</td>
#       <td>ethnicity_5</td>
#       <td>state_25</td>
#     </tr>
#     <tr>
#       <th>3</th>
#       <td>major_code_18</td>
#       <td>gender_1</td>
#       <td>ethnicity_2</td>
#       <td>state_58</td>
#     </tr>
#     <tr>
#       <th>4</th>
#       <td>major_code_50</td>
#       <td>gender_1</td>
#       <td>ethnicity_2</td>
#       <td>state_58</td>
#     </tr>
#     <tr>
#       <th>5</th>
#       <td>major_code_18</td>
#       <td>gender_1</td>
#       <td>ethnicity_2</td>
#       <td>state_58</td>
#     </tr>
#     <tr>
#       <th>6</th>
#       <td>major_code_18</td>
#       <td>gender_1</td>
#       <td>ethnicity_2</td>
#       <td>state_58</td>
#     </tr>
#     <tr>
#       <th>7</th>
#       <td>major_code_18</td>
#       <td>gender_1</td>
#       <td>ethnicity_2</td>
#       <td>state_58</td>
#     </tr>
#     <tr>
#       <th>8</th>
#       <td>major_code_18</td>
#       <td>gender_1</td>
#       <td>ethnicity_2</td>
#       <td>state_58</td>
#     </tr>
#     <tr>
#       <th>9</th>
#       <td>major_code_18</td>
#       <td>gender_1</td>
#       <td>ethnicity_2</td>
#       <td>state_58</td>
#     </tr>
#   </tbody>
# </table>
#     </div>
# 
# 
#  ---
#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for deidentify_columns (exercise 9). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 
# 

# In[50]:


### Test Cell - Exercise 9  


from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load
from time import time

tracemalloc.start()
mem_start, peak_start = tracemalloc.get_traced_memory()
print(f"initial memory usage: {mem_start/1024/1024:.2f} MB")

# Load testing utility
with open('resource/asnlib/publicdata/execute_tests', 'rb') as f:
    executor = dill.load(f)

@run_with_timeout(error_threshold=200.0, warning_threshold=100.0)
@suppress_stdout
def execute_tests(**kwargs):
    return executor(**kwargs)


# Execute test
start_time = time()
passed, test_case_vars, e = execute_tests(func=plugins.sqlite_blocker(deidentify_columns),
              ex_name='deidentify_columns',
              key=b'O0BU75J0b9vpmE9I87bfmsoeq8QjLtdkUmFw3nrTbWQ=', 
              n_iter=20)
# Assign test case vars for debugging
input_vars, original_input_vars, returned_output_vars, true_output_vars = test_case_vars
duration = time() - start_time
print(f"Test duration: {duration:.2f} seconds")
current_memory, peak_memory = tracemalloc.get_traced_memory()
print(f"memory after test: {current_memory/1024/1024:.2f} MB")
print(f"memory peak during test: {peak_memory/1024/1024:.2f} MB")
tracemalloc.stop()
if e: raise e
assert passed, 'The solution to deidentify_columns did not pass the test.'

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# ### Run me!
# 
# Whether you solved the previous exercise or not, run the following code cell. It will load the proper results into memory for the next exercise.

# In[34]:


deidentified_df = utils.load_object_from_publicdata('deidentified_df.dill')


# ### Exercise 10: (3 points)
# **perturb_gpa**  
# 
# **Your task:** define `perturb_gpa` as follows:
# 
# Apply data perturbation to GPA values to protect student privacy while preserving statistical properties.
# 
# **Inputs**: 
# - `df`: A DataFrame containing student records with 'semester_gpa' and scholarship columns ending with '_recpt'
# - `seed`: An integer seed value for the random number generator (default: 6040)
# 
# **Return**:
# - A new DataFrame with the same structure as the input but with perturbed 'semester_gpa' values
# 
# **Requirements**:
# - Perturb 'semester_gpa' values based on scholarship recipient status
# - Use the provided random number generator instance `rng` to ensure reproducibility
# - Do not modify the original input DataFrame
# - Do not use SQLite
# - Follow the exact calculation order specified in the steps below to maintain consistency
# 
# **Steps**:
# 1. Check if 'semester_gpa' column exists in the DataFrame. If not, return the DataFrame unchanged.
# 2. Identify scholarship columns (those ending with '_recpt' suffix).
# 3. If no scholarship columns exist, return the DataFrame unchanged.
# 4. Identify students with no scholarships (all '_recpt' columns = 0):
#    - Calculate the mean semester_gpa for this group
#    - Perturb their GPAs using a normal distribution with the group mean and standard deviation = 0.1
# 5. For each specific scholarship type, IN THE ORDER THEY APPEAR IN THE COLUMNS LIST:
#    - Identify students who received only this specific scholarship (this '_recpt' column = 1 and all others = 0)
#    - Calculate the mean semester_gpa for students with this specific scholarship
#    - Perturb their GPAs using a normal distribution with this scholarship-specific mean and standard deviation = 0.1
# 6. Leave semester_gpa values unchanged for students with multiple scholarships.
# 7. Return the DataFrame with scholarship-specific perturbed values.
# 
# **Important Note on Random Number Generation**:
# The random number generator maintains its state between calls. This means the sequence of random numbers
# depends on the order of operations. You must process the student groups in the exact order specified above
# (no-scholarship students first, then single-scholarship students in column order) to ensure reproducible results.
# Each call to `rng.normal()` advances the generator's internal state.
# 
# **Example**:
# 
# If a group has a mean GPA of 3.5:
# - A student with a GPA of 3.6 might be perturbed to 3.45
# - A student with a GPA of 3.4 might be perturbed to 3.58
# - All while maintaining a group mean close to 3.5
# 
# **Hints**:
# - The random number generator `rng` is already created for you using `np.random.default_rng(seed)`
# - Use boolean masks to select the appropriate rows for each scholarship group
# - Use `rng.normal(loc=mean, scale=standard_deviation, size=number_of_values)` to generate perturbed values
# - For more information on NumPy random number generator state, see this [Stack Overflow discussion](https://stackoverflow.com/questions/32172054/how-can-i-retrieve-the-current-seed-of-numpys-random-number-generator)
# - Use boolean indexing to update the 'semester_gpa' values
# 

# In[55]:


### Solution - Exercise 10  
def perturb_gpa(df: pd.DataFrame, seed: int = 6040) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    
    df_copy = df.copy()
    if 'semester_gpa' not in df_copy.columns:
        return df_copy
    
    # 1. Identify scholarship columns (suffix check)
    schol_cols = [col for col in df_copy.columns if col.endswith('_recpt')]
    
    # 2. Return unchanged if no scholarship columns exist
    if not schol_cols:
        return df_copy
    
    total_schol = df_copy[schol_cols].sum(axis=1)
    
    # 3. NO SCHOLARSHIP (First in order for rng consistency)
    group_no_schol = (total_schol == 0)
    if group_no_schol.any():
        avg_gpa_no_schol = df_copy.loc[group_no_schol, 'semester_gpa'].mean()
        # No .round() unless specifically requested in the steps
        df_copy.loc[group_no_schol, 'semester_gpa'] = rng.normal(loc=avg_gpa_no_schol, scale=0.1, size=group_no_schol.sum())

    # 4. SPECIFIC SCHOLARSHIPS (In column order)
    for col in schol_cols:
        # Identify students with ONLY this scholarship
        group_w_schol = (total_schol == 1) & (df_copy[col] == 1)
        
        if group_w_schol.any():
            avg_gpa_w_schol = df_copy.loc[group_w_schol, 'semester_gpa'].mean()
            df_copy.loc[group_w_schol, 'semester_gpa'] = rng.normal(loc=avg_gpa_w_schol, scale=0.1, size=group_w_schol.sum())
    
    return df_copy
    
    
### Demo function call
demo_result_perturb_gpa = perturb_gpa(deidentified_df, seed=SEED)
filtered_demo_result_perturb_gpa = demo_result_perturb_gpa[['semester_gpa', 'scholarship_4_recpt', 'scholarship_12_recpt']]
no_scholarships = filtered_demo_result_perturb_gpa[(filtered_demo_result_perturb_gpa['scholarship_4_recpt'] == 0) & 
                                            (filtered_demo_result_perturb_gpa['scholarship_12_recpt'] == 0)]
both_scholarships = filtered_demo_result_perturb_gpa[(filtered_demo_result_perturb_gpa['scholarship_4_recpt'] == 1) & 
                                            (filtered_demo_result_perturb_gpa['scholarship_12_recpt'] == 1)]
only_scholarship1 = filtered_demo_result_perturb_gpa[(filtered_demo_result_perturb_gpa['scholarship_4_recpt'] == 1) & 
                                            (filtered_demo_result_perturb_gpa['scholarship_12_recpt'] == 0)]
only_scholarship2 = filtered_demo_result_perturb_gpa[(filtered_demo_result_perturb_gpa['scholarship_4_recpt'] == 0) & 
                                            (filtered_demo_result_perturb_gpa['scholarship_12_recpt'] == 1)]
sample = pd.concat([
    no_scholarships.head(3), both_scholarships.head(3), only_scholarship1.head(2), only_scholarship2.head(2)
]).reset_index(drop=True)
sample


# ### Run me!
# 
# Whether your solution is working or not, run the following code cell. It will load the proper results into memory and show the expected output for the demo cell above.

# In[57]:


### Run Me!!!
demo_result_perturb_gpa_TRUE = utils.load_object_from_publicdata('demo_result_perturb_gpa_TRUE')


#  
# 
# **The demo should display this output.**  
# 
# <div style="overflow-x:auto;">
#     <style>
#         table {
#             border-collapse: collapse;
#             margin: 15px 0;
#             font-size: 0.9em;
#             font-family: sans-serif;
#             width: auto;
#         }
#         th, td {
#             padding: 8px;
#             text-align: right;
#             border-bottom: 1px solid #ddd;
#         }
#         tr:hover {background-color: #f5f5f5;}
#     </style>
#     <table border="0" class="dataframe">
#   <thead>
#     <tr style="text-align: right;">
#       <th></th>
#       <th>semester_gpa</th>
#       <th>scholarship_4_recpt</th>
#       <th>scholarship_12_recpt</th>
#     </tr>
#   </thead>
#   <tbody>
#     <tr>
#       <th>0</th>
#       <td>2.87</td>
#       <td>0</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>1</th>
#       <td>2.66</td>
#       <td>0</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>2</th>
#       <td>2.85</td>
#       <td>0</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>3</th>
#       <td>2.89</td>
#       <td>1</td>
#       <td>1</td>
#     </tr>
#     <tr>
#       <th>4</th>
#       <td>2.92</td>
#       <td>1</td>
#       <td>1</td>
#     </tr>
#     <tr>
#       <th>5</th>
#       <td>2.89</td>
#       <td>1</td>
#       <td>1</td>
#     </tr>
#     <tr>
#       <th>6</th>
#       <td>3.06</td>
#       <td>1</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>7</th>
#       <td>2.48</td>
#       <td>1</td>
#       <td>0</td>
#     </tr>
#     <tr>
#       <th>8</th>
#       <td>3.06</td>
#       <td>0</td>
#       <td>1</td>
#     </tr>
#     <tr>
#       <th>9</th>
#       <td>3.20</td>
#       <td>0</td>
#       <td>1</td>
#     </tr>
#   </tbody>
# </table>
#     </div>
# 
# 
#  ---
#  <!-- Test Cell Boilerplate -->  
# The cell below will test your solution for perturb_gpa (exercise 10). The testing variables will be available for debugging under the following names in a dictionary format.  
# - `input_vars` - Input variables for your solution.   
# - `original_input_vars` - Copy of input variables from prior to running your solution. Any `key:value` pair in `original_input_vars` should also exist in `input_vars` - otherwise the inputs were modified by your solution.  
# - `returned_output_vars` - Outputs returned by your solution.  
# - `true_output_vars` - The expected output. This _should_ "match" `returned_output_vars` based on the question requirements - otherwise, your solution is not returning the correct output. 
# 

# In[56]:


### Test Cell - Exercise 10  


from cse6040_devkit.tester_fw.testers import Tester
from yaml import safe_load
from time import time

tracemalloc.start()
mem_start, peak_start = tracemalloc.get_traced_memory()
print(f"initial memory usage: {mem_start/1024/1024:.2f} MB")

# Load testing utility
with open('resource/asnlib/publicdata/execute_tests', 'rb') as f:
    executor = dill.load(f)

@run_with_timeout(error_threshold=200.0, warning_threshold=100.0)
@suppress_stdout
def execute_tests(**kwargs):
    return executor(**kwargs)


# Execute test
start_time = time()
passed, test_case_vars, e = execute_tests(func=plugins.sqlite_blocker(perturb_gpa),
              ex_name='perturb_gpa',
              key=b'O0BU75J0b9vpmE9I87bfmsoeq8QjLtdkUmFw3nrTbWQ=', 
              n_iter=20)
# Assign test case vars for debugging
input_vars, original_input_vars, returned_output_vars, true_output_vars = test_case_vars
duration = time() - start_time
print(f"Test duration: {duration:.2f} seconds")
current_memory, peak_memory = tracemalloc.get_traced_memory()
print(f"memory after test: {current_memory/1024/1024:.2f} MB")
print(f"memory peak during test: {peak_memory/1024/1024:.2f} MB")
tracemalloc.stop()
if e: raise e
assert passed, 'The solution to perturb_gpa did not pass the test.'

###
### AUTOGRADER TEST - DO NOT REMOVE
###

print('Passed! Please submit.')


# Fin
