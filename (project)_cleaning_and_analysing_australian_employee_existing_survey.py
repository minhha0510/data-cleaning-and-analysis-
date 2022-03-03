# -*- coding: utf-8 -*-
"""(Project) cleaning and analysing Australian employee existing survey.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KBHkwKcT9londgk3H2N6uMmUu6IbttLT

# Executive summary 

In this project, I'll work with exit surveys from employees of the Department of Education, Training and Employment (DETE) and the Technical and Further Education (TAFE) institute in Queensland, Australia. You can find the TAFE exit survey [here](https://raw.githubusercontent.com/minhha0510/data-cleaning-and-analysis-/main/tafe_survey.csv) and the survey for the DETE [here](https://raw.githubusercontent.com/minhha0510/data-cleaning-and-analysis-/main/dete_survey.csv).

Goals¶
In this project, I tried to answer the following question:
- Are employees who only worked for the institutes for a short period of time resigning due to some kind of dissatisfaction? What about employees who have been there longer?

- Are younger employees resigning due to some kind of dissatisfaction? What about older employees?

__Summary of Results__
The dissatisfaction distribution by age also seems to suggest that older people tend to renounce due to dissatisfaction more than younger people. The exception in the 26-30 group of people who also have high percentage of dissatisfied employees.

# Data exploration
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
url_dete_survey = "https://raw.githubusercontent.com/minhha0510/data-cleaning-and-analysis-/main/dete_survey.csv"
url_tafe_survey = "https://raw.githubusercontent.com/minhha0510/data-cleaning-and-analysis-/main/tafe_survey.csv"
dete_survey = pd.read_csv(url_dete_survey)
tafe_survey = pd.read_csv(url_tafe_survey)

dete_survey.isnull().sum()

dete_survey.head(3)

dete_survey.info()

"""The business unit missing a huge chunks of dete_survey. It could be correlated to the time employment of an employee."""

tafe_survey.head()
tafe_survey.info()

dete_survey.info()

"""In this project, I tried to answer the following question:
1. Are employees who only worked for the institutes for __a short period of time__ resigning due to some kind of __dissatisfaction__? What about employees who have been there __longer__?

2. __Are younger employees resigning due to some kind of dissatisfaction? What about older employees?__
"""

dete_survey.columns[28:49]

dete_survey.columns[0:28]

tafe_survey.columns[17:66]

"""# Data cleaning

I would like to use some of the columns in both databases for the final analyses, however, their names are a bit different so I'll rename it.
![image.png](attachment:image.png)
"""

# Rename the columns
dete_survey.columns = dete_survey.columns.str.lower().str.replace(" ", "_").str.strip()

dete_survey.columns

tafe_survey.columns

new_columns = {'Record ID': 'id',
'CESSATION YEAR':'cease_date',
'Reason for ceasing employment':'separation_type',
'Gender. What is your Gender?':'gender',
'CurrentAge. Current Age':'age',
'Employment Type. Employment Type':'employment_status',
'Classification. Classification':'position',
'LengthofServiceOverall. Overall Length of Service at Institute (in years)':'institute_service',
'LengthofServiceCurrent. Length of Service at current workplace (in years)':'role_service',
'Contributing Factors. Dissatisfaction':'factors_diss',
'Contributing Factors. Job Dissatisfaction':'factors_job_diss'
        }

tafe_survey = tafe_survey.rename(new_columns, axis = 1)
tafe_survey.columns

# Drop the columns that are not necessary for the analysis
dete_survey_updated= dete_survey.drop(dete_survey.columns[28:49], axis =1)
tafe_survey_updated= tafe_survey.drop(tafe_survey.columns[17:66], axis =1)
dete_survey_updated.columns

"""The end goal is to answer the following question:

Are employees who have only worked for the institutes for a short period of time __resigning__ due to some kind of dissatisfaction? What about employees who have been at the job longer?

So I only analyse survey respondents who resigned, so their separation type contains the string 'Resignation'.

Note that dete_survey_updated dataframe contains multiple separation types with the string 'Resignation':

Resignation-Other reasons
Resignation-Other employer
Resignation-Move overseas/interstate
I'll have to account for each of these variations so we don't unintentionally drop data!
"""

dete_survey_updated.rename({'separationtype': 'separation_type'}, axis=1, inplace=True)

dete_survey_updated.columns

dete_survey_updated["separation_type"].value_counts(dropna = False)

dete_survey_updated["cease_date"]
# check for the validity of our data. The simplest way would be to check the start and end date

# filtering out separation due to resignation
dete_survey_updated["separation_type"] = dete_survey_updated["separation_type"].str.split('-').str[0]
dete_resignations = dete_survey_updated.copy()[dete_survey_updated["separation_type"].str.contains(r'Resignation')]

dete_resignations.head(5)

# Extract the years and convert them to a float type
dete_resignations['cease_date'] = dete_survey_updated['cease_date'].str.split('/').str[-1]
dete_resignations['cease_date'].isnull()
#There are a few values in dete_resignation is not stated, we need to drop these data

dete_resignations.head(5)

dete_resignations["cease_date"].value_counts()

dete_resignations = dete_resignations[dete_resignations["cease_date"].str.contains("Not Stated")==False]

dete_resignations = dete_resignations[dete_resignations["dete_start_date"].str.contains("Not Stated")==False]

# Check if the "Not stated" rows had been removed
dete_resignations["cease_date"].value_counts()

tafe_resignations = tafe_survey_updated[tafe_survey_updated['separation_type'] == 'Resignation'].copy()

tafe_resignations['cease_date'].value_counts()

"""# Calculating service time

It is noiticable that the tafe_resignations dataframe already contains a `service` column, which we renamed to institute_service. In order to analyze both surveys together, we'll have to create a corresponding institute_service column in dete_resignations.
"""

dete_resignations['institute_service'] = (dete_resignations['dete_start_date'].astype(float)-dete_resignations['cease_date'].astype(float))*(-1)
dete_resignations['institute_service'].value_counts()

"""Excluding the null values of the institute_service field from the DETE dataset, we observe that 42% of the employees worked at most 5 years."""

tafe_resignations['institute_service'].value_counts(dropna = False)

tafe_resignations.info()

"""# Identification of Dissatisfied Employees
Also, we will work with dete_resignations and tafe_resignations as the dataset has data corresponding to resigned employees only. In dete_resignations, I think the following columns contribute to the employee's decision:

- 13 Job dissatisfaction
- 14 Dissatisfaction with the department
- 15 Physical work environment
- 16 Lack of recognition
- 17 Lack of job security
- 18 Work location
- 19 Employment conditions
- 20 Maternity/family
- 21 Relocation
- 22 Study/Travel
- 23 Ill Health
- 24 Traumatic incident
- 25 Work life balance
- 26 Workload
"""

# we will create a column 'dissatisfied' which will be of Boolean type
# the role of 'any' is to return whether any element is True
dete_resignations['dissatisfied'] = dete_resignations[['job_dissatisfaction',
       'dissatisfaction_with_the_department', 'physical_work_environment',
       'lack_of_recognition', 'lack_of_job_security', 'work_location',
       'employment_conditions', 'work_life_balance',
       'workload']].any(1,skipna=False)
dete_resignations_up = dete_resignations.copy()
dete_resignations_up['dissatisfied'].value_counts(dropna = False)

def update_val(val):
    """Update the value to boolean or np.nan.

    Args:
      val: The value to be updated.

    Returns:
      bool or np.nan.
    """
    if val == '-':
        return False
    elif pd.isnull(val):
        return np.nan
    else:
        return True

# similar to the above, but this is with tafe dataframe
tafe_resignations['dissatisfied'] = tafe_resignations[['factors_diss','factors_job_diss']].applymap(update_val).any(1,skipna=False)
tafe_resignations['dissatisfied'].head()
tafe_resignations_up = tafe_resignations.copy()
tafe_resignations_up['dissatisfied'].value_counts(dropna = False)

"""# Combining DataFrames
We have performed various actions to clean and filter our data. Now we will be reeady to merge iot. Also, as we practiced in some lessons before, while merging it is better that each dataset has it as own identity. We have given an identity to each dataste by dedicating a column with their title.
"""

dete_resignations_up['institute'] = 'DETE'
tafe_resignations_up['institute'] = 'TAFE'

# combining
combined = pd.concat([dete_resignations_up, tafe_resignations_up], ignore_index=True)
combined.shape

# Drop columns with less than 500 non null values
combined_updated = combined.dropna(thresh = 500, axis =1).copy()
combined_updated

"""# Classifying Employees by Length of Service
I classified employees according to their duration of work. Below is the classification:

- New: Less than 3 years at a company
- I’m Experienced: 3-6 years at a company
- Established: 7-10 years at a company
- Veteran: 11 or more years at a company
"""

# combined['institute_service'].astype('str')
combined_updated['institute_service'].value_counts(dropna = False)

# Extract the years of service and convert the type to float
combined_updated['institute_service_up'] = combined_updated['institute_service'].astype('str').str.extract(r'(\d+)')
combined_updated['institute_service_up'] = combined_updated['institute_service_up'].astype('float')

# Check the years extracted are correct
combined_updated['institute_service_up'].value_counts()

#Next, we'll map each value to one of the career stage definitions.

def transform_service(val):
    if val >= 11:
        return "Veteran"
    elif 7 <= val < 11:
        return "Established"
    elif 3 <= val < 7:
        return "Experienced"
    elif pd.isnull(val):
        return np.nan
    else:
        return "New"

# Updating the new definition
combined_updated['service_cat'] = combined_updated['institute_service_up'].apply(transform_service)

# Check
combined_updated['service_cat'].head()

"""# Perform analysis
First some of the data in the dissatisfied columns are missing, it need to be filled in and then aggregated.

Dissatisfied column consists of Boolean values, meaning they're either True or False. Methods such as the df.pivot_table() method actually treat Boolean values as integers, so a True value is considered to be 1 and a False value is considered to be 0. 

That means that the data can be aggregated and calculate the number of people in each group, the percentage of people in each group, etc.
"""

combined_updated['dissatisfied'].value_counts().dropna(inplace=False)

# Replace missing values with the most frequent value, False
combined_updated['dissatisfied'] = combined_updated['dissatisfied'].fillna(False)

dissatisfied_resignations = combined_updated.pivot_table(values='dissatisfied', index = 'service_cat')
dissatisfied_resignations

"""Doing a bivariate analysis between service category and dissatisfied employees, I obsreved that 51.6% of the resignations were from employees with more than 7 years in the institute (51.6% from established employees and 48.5% from veteran employees). With this data, *I can infer that people that work in the DETE and TAFE institute become unmotivated with their jobs probably because of the few challenges they are facing.*"""

# Commented out IPython magic to ensure Python compatibility.
# Calculating the percentage of employees who resigned due to dissatisfaction in each category
dis_pct = combined_updated.pivot_table(index='service_cat', values='dissatisfied')

# Plot the results
# %matplotlib inline
dis_pct.plot(kind='bar', rot=30)

"""## Deeper analysis by incorporating the age column
By dissecting the age column, we can analyze more in-depth the demographic of people that left and to answer the question: __Did more employees in the DETE survey or TAFE survey end their employment because they were dissatisfied in some way?__
"""

combined_updated['age'].value_counts().sort_index()

combined_updated['age'] = combined_updated['age'].str.replace("  ","-")

def age_cleanup(element):
    if element == "61 or older": return "56 or older"
    elif element == "56-60": return "56 or older"
    else: return element

combined_updated['age'] = combined_updated['age'].map(age_cleanup)

combined_updated['age'].value_counts(dropna=False).sort_index()

# Incorporating the age column into the dissatisfaction dataframe
combined_up_dis = combined_updated.loc[combined_updated['dissatisfied']==True,]

df_Age = combined_updated['age'].value_counts().sort_index().to_frame(name='Total')
df_Age['Dissatisfied'] = combined_up_dis['age'].value_counts().sort_index()
df_Age['Other reasons'] = df_Age['Total'] - df_Age['Dissatisfied']
df_Age['Dissatisfied %'] = round(df_Age['Dissatisfied'] / df_Age['Total'],2)
df_Age['Other reasons %'] = round(df_Age['Other reasons'] / df_Age['Total'],2)
df_Age.index.name = 'Age'                                                           
display(df_Age)

df_Age['Dissatisfied %'].plot(kind='bar')

"""The dissatisfaction distribution by age also seems to suggest that older people tend to renounce due to dissatisfaction more than younger people. The exception in the 26-30 group of people who also have high percentage of dissatisfied employees"""