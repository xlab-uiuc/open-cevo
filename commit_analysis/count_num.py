#!/usr/bin/python
import re

def simple_count(file, commit_link_col):

	commit_list = []
	hdfs_commit_num = 0
	hbase_commit_num = 0
	saprk_commit_num = 0
	cassandra_commit_num = 0

	file = open(file)
	for line in file:
		vals = line.split(",")
		if vals[commit_link_col] not in commit_list:
			commit_list.append(vals[commit_link_col])
			if "hdfs" in vals[0].lower():
				hdfs_commit_num = hdfs_commit_num + 1
			if "hbase" in vals[0].lower():
				hbase_commit_num = hbase_commit_num + 1
			if "spark" in vals[0].lower():
				saprk_commit_num = saprk_commit_num + 1
			if "cassandra" in vals[0].lower():
				cassandra_commit_num = cassandra_commit_num + 1
	return hdfs_commit_num,hbase_commit_num,saprk_commit_num,cassandra_commit_num
	file.close()

def simple_count_by_keyword(file, keywords, keyword_col):
	file = open(file)
	count = 0
	for line in file:
		vals = line.split(",")
		flag = 0
		for keyword in keywords:
			if keyword in vals[keyword_col].lower():
				flag = 1
		if flag == 1:
			count = count + 1
	return count


def count_by_keyword(file, commit_link_col, keywords, keyword_col):

	commit_list = []
	hdfs_commit_num = 0
	hbase_commit_num = 0
	saprk_commit_num = 0
	cassandra_commit_num = 0
	file = open(file)
	for line in file:
		vals = line.split(",")
		flag = 0
		for keyword in keywords:
			if keyword in vals[keyword_col].lower():
				flag = 1
		if flag == 1:
			if vals[commit_link_col] not in commit_list:
				commit_list.append(vals[commit_link_col])
				if "hdfs" in vals[0].lower():
					hdfs_commit_num = hdfs_commit_num + 1
				if "hbase" in vals[0].lower():
					hbase_commit_num = hbase_commit_num + 1
				if "spark" in vals[0].lower():
					saprk_commit_num = saprk_commit_num + 1
				if "cassandra" in vals[0].lower():
					cassandra_commit_num = cassandra_commit_num + 1
	return hdfs_commit_num,hbase_commit_num,saprk_commit_num,cassandra_commit_num
	file.close()


def print_simple_count(category, file, commit_link_col):

	count = simple_count(file, commit_link_col)
	print (category + ' ' + str(count[0]) + ' ' + str(count[1]) + ' ' +  str(count[2]) + ' ' + str(count[3])
		+ ' ' + str(count[0] + count[1] + count[2] + count[3]))

def print_count_by_keyword(category, file, commit_link_col, keywords, keyword_col):

	count = count_by_keyword(file, commit_link_col, keywords, keyword_col)
	print (category + ' ' + str(count[0]) + ' ' + str(count[1]) + ' ' +  str(count[2]) + ' ' + str(count[3])
		+ ' ' + str(count[0] + count[1] + count[2] + count[3]))

#just for table VI
def print_commit_and_param_num(category, file, commit_link_col, keywords, keyword_col):
	commit_num = count_by_keyword(file, commit_link_col, keywords, keyword_col)
	param_num = simple_count_by_keyword(file, keywords, keyword_col)
	print (category + " " + str(commit_num[0] + commit_num[1] + commit_num[2] + commit_num[3]) + " " + str(param_num))

print("##########################################################")
print("Table IV")
print("INTERFACE is caculated by adding up AddParam, RemoveParam and ModifyParam")
print("BEHAVIOR is caculated by adding up Parse, Check, Handle and Use")
print("DOCUMENT is caculated by adding up User Manual and Code Comments")
print("##########################################################")
print("Table V")
print("AddParam, RemoveParam and ModifyParam are calculated by adding their sub-categories")
print_count_by_keyword("AddNewCode", "add_param.csv",1,{"new"},2)
print_count_by_keyword("AddCodeChange", "add_param.csv",1,{"change"},2)
print_simple_count("AddParameterization","parameterization.csv",4)
print_simple_count("RmvModule","rmv_with_code.csv",1)
print_simple_count("RmvReplace","rmv_replace.csv",3)
print_simple_count("ModNaming","param_rename.csv",2)
print_simple_count("ModDefualtValue","change_default_value.csv",4)
print_simple_count("ModConstraint","change_param_constraint.csv",4)
print("##########################################################")
print("Table VI")
print_commit_and_param_num("Performance","parameterization.csv",4,{"performance"},6)
print_commit_and_param_num("Reliability","parameterization.csv",4,{"reliability"},6)
print_commit_and_param_num("Manageability","parameterization.csv",4,{"manageability"},6)
print_commit_and_param_num("Debugging","parameterization.csv",4,{"debug"},6)
print_commit_and_param_num("Environment","parameterization.csv",4,{"env"},6)
print_commit_and_param_num("Compatibility","parameterization.csv",4,{"compatibility"},6)
print_commit_and_param_num("Testability","parameterization.csv",4,{"testability"},6)
print_commit_and_param_num("Security","parameterization.csv",4,{"security"},6)
print("##########################################################")
print("Table VIII")
print("Handle and Use are calculated by adding their sub-categories")
print_simple_count("Parse","config_parsing.csv",1)
print_count_by_keyword("Check","checking_and_handling_code.csv",4,{"check"},5)
print_count_by_keyword("HandleAction ","checking_and_handling_code.csv",4,{"exception"},5)
print_count_by_keyword("HandleMessage","checking_and_handling_code.csv",4,{"message"},5)
print_simple_count("UseChange","change_param_existing_usage.csv",4)
print_simple_count("UseAdd","param_new_use.csv",4)
print("##########################################################")
print("Documentation")
print_count_by_keyword("User Manual","change_documentation.csv",4,{"file","guide","command","description"},6)
print_count_by_keyword("Code Comments","change_documentation.csv",4,{"code comment"},6)







