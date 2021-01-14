# Artifacts for Configuration Evolution of Cloud Systems

This repository includes the artifacts of the evolutionary study of software configuration design and implementation in cloud systems.

The repository includes the following artifacts:

* `config_commits`: 1178 configuration evolution commits from a recent
2.5 year (2017.06-2019.12) version control history of four large-scale open-source projects (HDFS, HBase, Spark, and
Cassandra). 
* `commit_analysis`: Studied commits with well-labeled categorizations and analysis results, organized based on the structure of the paper.
* `code`: Python scripts for collecting raw commits that touch configuration.
* `commit_study.md`: Documentation of the manual study methodology (analyzing raw commits and issues), including code snippet examples and descriptions for each category in Table II of the submission. 

## 1. Data Comprehension and Layout

We provide the data that we studied in this paper. All the data sheets are in the format of CSV, with titles/labels as the first rows. Note that some labels are recorded for specific commits/parameters. (e.g. "How to choose new value" in `change_default_value.csv` is just for numeric parameters and we describe the reason in Section IV.B in the paper)

All the data sheets except `change_doucumentation.csv` use each row to record an individual parameter change, with the links to the commit/issue page. In `change_doucumentation.csv`, each row records a document change.

**Note that one commit can contains changes of multiple parameters for multiple reasons.**

Here is a mapping from the subsection of the paper to the data sheet (in the `commit_analysis` directory).

* **Section IV (Configuration Interface Evolution)**

  * Section IV.A(1) (Parameterization) &rarr; `parameterization.csv` 
  
  * Section IV.A(2) (Removing parameters) &rarr; `rmv_replace.csv`

  * Section IV.B (Evolution of default values) &rarr; `change_default_value.csv`

* **Section V (Configuration Usage Evolution)**

  * Section V.A (Evolution of parameter checking code) &rarr; `checking_and_handling_code.csv`

  * Section V.B (Evolution of error-handling code) &rarr; `checking_and_handling_code.csv`

  * Section V.C (Evolution of using parameter values) &rarr; `change_param_existing_usage.csv` and `param_new_use.csv`

* **Section VI (Configuration Document Evolution)** &rarr; `change_doucumentation.csv`

We also provide sheets for other categories for future study and reuse.
The script in `commit_analysis` is to count the numbers and generate the main tables in the paper:

~~~
python3 count_num.py
~~~

## 2. Commit Collection and Analysis

Besides the data in this paper, for future reuse and study, we also provide the script we use to collect the raw commits and a tutorial to show how we do the manual study of each raw commit.

### 2.1 Collect raw commits that touch configuration

Please use python3 to install the dependencies and run the code(we use python 3.8.5).

1. Install dependenceis
~~~bash
pip3 install pathlib
pip3 install nltk
pip3 install beautifulsoup4
~~~

2. Goto `code/'software'` 
Change the following file path in `download_diff.py`
* DIFF_FILE_PATH = "The path that you want to store the commit diff files"  
And run:  
```bash
python3 get_commit.py
```
to download the raw commits for the target software projects. Please add the latest `commit_page_url` of studied software among studied time span in `commit_url.txt` (There is already one in the file). 
* Note: You can stop the downloading process by using ctrl+c whenever you think the time span is enough (downloading all the commits and diff files are time-comsuming, you can first try with a short time-span). If you want to continue the downloading process, just simply run the `get_commit.py` again. (The url in `commit_url.txt` will be automatically updated, you can check `url_log.txt`). If the programm stops (mostly are network issues or too many request), also run `get_commit.py` again to continue.

The output will be `commit_info.txt` that contains basic info of each commit, and corresponding diff files will be downloaded in `DIFF_FILE_PATH`

3. Run  
```bash
python3 commit_selection.py
``` 
to automtically select commits that touch configuration. The out put will be `commit_selected.txt` that has structured info for each selected commit, and the info contains hints that how this diff touches configuration. **By search those hints in the diff file, one can quickly locate/briefly understant the configuration change.**

The detailed methodologies are described in the submitted paper. 
One method of selecting configuration-related commits is to use regular expressions to capture configuation-related code patterns. For example, one of the regular expressions used for HDFS is: 
~~~
HDFS_CONFIG_LOAD_FUNC_RE = '[a-zA-Z\.\_\-]*[cC]onf[ig]*[\(\)]*[\s]*[\n]*[\s]*\.[\s]*[\n]*[\s]*get[a-zA-Z]*\([^;<>]+\)'
~~~

The regular expression can find commits like [HDFS-13607](https://github.com/apache/hadoop/commit/c81ac2ff0220b180cd6cbbf18221290c3783bfd5) which adds a new parameter `dfs.journalnode.edit-cache-size.bytes` by matching the following code snippet:

~~~
+  capacity = conf.getInt(DFSConfigKeys.DFS_JOURNALNODE_EDIT_CACHE_SIZE_KEY,
+      DFSConfigKeys.DFS_JOURNALNODE_EDIT_CACHE_SIZE_DEFAULT);
~~~

The complete output info of this commit is shown below. 

~~~
HDFS-13607. [SBN read] Edit Tail Fast Path Part 1                                   //commit title
https://github.com/apache/hadoop/commit/c81ac2ff0220b180cd6cbbf18221290c3783bfd5    //commit link
2018-05-09T22:40:07Z                                                                //commit time
Commit message touches config:False                                                 //whether commit message touch "config" keyword
Diff touches config define:True                                                     //whether diff touches config define
Diff touches config loading:True                                                    //whether diff touches config load
Diff touches config setting:False                                                   //whether diff touches config set
Diff touches config variable (data flow):True                                       //whether diff touches config variable
Diff touches config message:False                                                   //whether diff touches message that have "config" keyword

_________________touchedConfigDefine_____________________

+hdfs-default.xml 

___________________touchedConfigLoad___________________

+conf.getInt(DFSConfigKeys.DFS_JOURNALNODE_EDIT_CACHE_SIZE_KEY,DFSConfigKeys.DFS_JOURNALNODE_EDIT_CACHE_SIZE_DEFAULT)

___________________touchedConfigSet____________________

Null

___________________touchedConfigVariable_____________________

+capacity JournaledEditsCache.java

___________________touchedMessage_____________________

Null
~~~

We provide a [demo](https://github.com/xlab-uiuc/open-cevo/tree/main/code/hdfs_demo_examples) (The above case is in that demo) for all HDFS commit examples in [commit_study.md (tutorial)](https://github.com/xlab-uiuc/open-cevo/blob/main/commit_study.md), they are HDFS-13607, HDFS-12291, HDFS-12412, HDFS-11998, HDFS-12716, HDFS-11576 and HDFS-12603. Run `commit_selection.py` in `/code/hdfs_demo_examples` to see `commit_selected.txt` and the structured info for each commit.
~~~bash
cd code/hdfs_demo_examples
python3 commit_selection.py
~~~

We implement software-specific regular expressions which can be found in `diff_file_parser.py` in each software subdirectory. All the regular expressions are carefully crafted based on a pilot study of configuration-related commits of the target software projects.

### 2.2 Commit Study

We validate, analyze and categorize each commit based on the commit log and diff, as well as the corresponding JIRA or GitHub Issues as described in the paper. Our categorization is based on the taxonomy of Figure 1 and Table II of the submission. This step currently is manually without program automation. We provide a [tutorial](https://github.com/xlab-uiuc/open-cevo/blob/main/commit_study.md) that contains concrete code examples for every category.

**Note that one commit can touch several categories; we study it in each category.**

We also analyze JIRA issues or GitHub Pull Requests (PRs) that linked with each commit which provides more background and context information of the commit. 

All the commits in our study are linked to JIRA issues or GitHub PRs. 

## 3. Reusability

### 3.1 Extending our study to longer time span

We provide our script to select commits related to configuration, which can be reused for large-scale studies (e.g., longer time span). 

To do so, please change the `url` in `code/'software'/commit_url.txt` to the corresponding commit you want to start with. Our script will crawl **oldler** commit based on this. For example, if you want to crawl commit of `HBase` before `Dec.25 2020`, one can do:
   ```bash
   echo "https://github.com/apache/hbase/commits/master?before=0f868da05d7ffabe4512a0cae110ed097b033ebf+35&branch=master" > code/hbase/commit_url.txt
   ```

### 3.2 Extending our study to other software projects

The main idea to select configuration related commits is using text-based regular expression matching. We show the regex we used in `diff_file_parser.py` in each
`code/'software'` folder. One can reuse and tweak the scripts for other software projects. We suggest you to test the regex using [regex101](https://regex101.com).


You will need to modify:
 - ```bash
   cd code
   mkdir other_software
   cp -r hbase/* other_software/
   ```
 - change`commit_url.txt`, using the github commits page url of that software.
 - change the **regular expressions** global varaibles in diff_file_parser.py specific to the target software project.

### 3.3 Followup analysis based on the commits in this artifact

We provide an [tutorial](https://github.com/xlab-uiuc/open-cevo/blob/main/commit_study.md) to explain our taxonomy/categorization to help followup studies.
