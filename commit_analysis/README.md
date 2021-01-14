# Data Layout

There are 7 data sheets corresponding to the sections in the submitted paper.

## Data Sheets

* Section IV (CONFIGURATION INTERFACE EVOLUTION)

  * IV.A.1) (Parameterization) &rarr; `parameterization.csv` 
  
  * IV.A.2) (Removing Parameters) &rarr; `param_removal.csv`

  * IV.B (Evolution of Default Values) &rarr; `change_default_value.csv`

* Section V (CONFIGURATION USAGE EVOLUTION)

  * V.A (Evolution of Parameter Checking Code) &rarr; `checking_and_handling_code.csv`

  * V.B (Evolution of Error-handling Code) &rarr; `checking_and_handling_code.csv`

  * V.C (Evolution of Using Parameter Values) &rarr; `change_param_existing_usage.csv` and `param_new_use.csv`

* Section VI (CONFIGURATION DOCUMENT EVOLUTION) &rarr; `change_doucumentation.csv`

## Metadata Tags

The first row describes the metadata. Besides the common metadata tags such as `#Parmameter`, `#Issue ID`, `#Title`, `#Issue URL`, `#Commit URL`, `#Note`, there are also specific tags in each spreadsheet. 

**Note that some tags are only available for a subset of commit/parameters. We list them here to avoid any confusion.**

* `change_default_value.csv` : "#How to choose new value" is for 32 numeric parameters. Please refer to "Choosing new values" in Section IV.B.

* `change_doucumentation.csv` : "#Info added" is for 63 changes that enhance inadequate documents. Please refer to "Content added to enhance documentation" in Section VI

* `checking_and_handling_code.csv`: "#Checking content" is for configuration check changes (please refer to Section V.A); "#Changed message" is for misconfiguration feedback messages (please refer to Section V.B).



