#!/usr/bin/env python
import argparse
from subprocess import run
import xmltodict
import itertools
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
from time import time


def timeFormat(time_in_secs):
    """ Formats Seconds to relevant time interval"""

    time_in_secs = float("{0:.2f}".format(time_in_secs))
    days = time_in_secs // 86400
    hours = (time_in_secs - days * 86400) // 3600
    minutes = (time_in_secs - days * 86400 - hours * 3600) // 60
    seconds = time_in_secs - days * 86400 - hours * 3600 - minutes * 60
    time = ("{0} day{1}, ".format(days, "s" if days != 1 else "") if days else "") + \
        ("{0} hour{1} ".format(hours, "s" if hours != 1 else "") if hours else "") + \
        ("{0} minute{1} ".format(minutes, "s" if minutes != 1 else "") if minutes else "") + \
        ("{0} second{1} ".format(seconds, "s" if seconds != 1 else "") if seconds else "")
    return time


def is_non_zero_file(fpath):
    """ Check if the file exists, return boolean """
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0


def createFile(path):
    """ Creates the file path if it doesn't exist"""
    if os.path.exists(path):
        pass
    else:
        print("Making directory\n")
        os.mkdir(path)


def pretty_print_xml(xml, output):
    """ Pretty prints XML data """
    # Use xmllint natively to format data
    command = f"xmllint --format {xml} > {output}"
    run(command, shell=True)


def getIndex(list, element):
    """ Obtains the Index of specific elements in the list provided """
    index = list.index(element)
    return index


def smIterator(input_sm):
    """ Read through SM file and return the concepts and relationships; remove duplicates too."""

    concepts, relationships = '#Finite', '#Transitions'
    sm_concept_list, sm_relationships_list = [], []
    start_concepts, start_relationships = False, False

    with open(input_sm, "r") as sm_line:
        for line in sm_line:
            if relationships in line:
                start_concepts = False
            if start_concepts and "#" not in line:
                if line != "\n":
                    line = line.strip().split("\t")[1]
                    sm_concept_list.append(line)
            if concepts in line:
                start_concepts = True
            if start_relationships and "#" not in line:
                if line != "\n":
                    line = line.strip().split("\t")[1]
                    sm_relationships_list.append(line)
            if relationships in line:
                start_relationships = True
    # Remove duplicates by making list items keys; dicts can't have duplicate keys, automatically removed. Then convert back to list.
    sm_relationships_list, sm_concept_list = list(dict.fromkeys(
        sm_relationships_list)), list(dict.fromkeys(sm_concept_list))
    return sm_relationships_list, sm_concept_list


def metaDataListAppender(metaDict):
    """ Obtains the meta data counts and name from the XML data source """
    # Append to meta data concept class list with the concepts and their counts
    meta_count_list = []
    for slice in metaDict:
        for key, val in slice.items():
            meta_count_list.append(val)

    meta_count_dict = dict(itertools.zip_longest(
        *[iter(meta_count_list)] * 2, fillvalue=""))

    meta_counts_list = []
    meta_name_list = []
    for key, val in meta_count_dict.items():
        meta_name_list.append(key)
        meta_counts_list.append(val)
    meta_counts_list = list(map(int, meta_counts_list))
    return meta_counts_list, meta_name_list


def dataframeCreatorWriter(meta_name_list, meta_name_string, meta_counts_list, df_out_str):
    """ Creates dataframes for the data and saves them"""
    # Get pandas series to create dataframe to write out for Concept class
    s1 = pd.Series(meta_name_list, name=meta_name_string)
    s2 = pd.Series(meta_counts_list, name='Count')

    meta_df = pd.DataFrame({meta_name_string: s1,
                            'Count': s2})

    meta_df.to_csv(df_out_str, sep="\t", index=None, header=True)


def rmMetaData(rm_index, name_list, count_list):
    """ Deletes what is indexed from the lists """
    for i in sorted(rm_index, reverse=True):
        del name_list[i]
        del count_list[i]


def returnNotMatches(a, b):
    """ Check for differences between list sets and return the differences between lists """
    a = set(a)
    b = set(b)
    return [list(b - a), list(a - b)]


def plotFig(meta_counts_list, series_counts_pd, x_size, y_size, title, xlabel, output_name, label_height, meta_names_list):

    # Plot the CC figure
    red_bar = meta_counts_list.index(max(series_counts_pd))
    fig = plt.figure(figsize=(x_size, y_size))
    ax = series_counts_pd.plot(kind='bar')
    ax.set_title(title)
    ax.set_xlabel('Concept')
    ax.set_ylabel('Counts')
    ax.set_xticklabels(series_counts_pd)
    rects = ax.patches
    ax.patches[red_bar].set_facecolor('#aa3333')

    for rect, meta_names_list in zip(rects, meta_names_list):
        heights = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, heights + label_height, meta_names_list,
                ha='center', va='bottom')
    fig.savefig(f'{output}/barplots/{output_name}.png')


""" User Args """
parser = argparse.ArgumentParser(
    description="This script will perform read through the report output from Ondex and provide statistical outputs\n")
# Args init
parser.add_argument(
    '-xml', '--xml_input_file', help='Specify the location of the report xml.', required=True)
parser.add_argument(
    '-sm', '--semantics_input_file', help="Specify the location of the Semantic Motif file you're using for your knet", required=False)
parser.add_argument(
    '-out', '--output_dir', help='Specify the output of the stats.', required=True)

# Initiate the arguments
args = vars(parser.parse_args())

input, output, input_sm = args['xml_input_file'], args['output_dir'], args['semantics_input_file']
output = output.rstrip("/") if output.endswith('/') else output
output = output.replace("\\", "") if output.find("\\") else output

try:
    start_time = time()
    folder_list = [output, f"{output}/barplots", f"{output}/dataframes"]
    [createFile(folder) for folder in folder_list]
    pretty_print_xml(xml=input, output=f"{output}/report.xml")

    if is_non_zero_file(input_sm) and input_sm is not None:
        sm_relationships_list, sm_concept_list = smIterator(input_sm)
    else:
        print("\033[91mERROR:\033[0m No Semantic Motifs file found,are you sure"
              "you provided the correct file path?\n\nUsing default settings instead.\n")

    # Iterate through the report
    with open(f"{output}/report.xml") as fd:
        doc = xmltodict.parse(fd.read())

        """ Total Counts """
        tot_concept_count = doc['info']['general']['numberOfConcepts']
        tot_relationship_count = doc['info']['general']['numberOfRelations']

        print(f"Total number of concept counts is : \033[91m {tot_concept_count}\033[0m,"
              f" the total number of relationship counts is \033[91m{tot_relationship_count}\033[0m\n\n")

        """ MetaData Dicts """
        metaCC_dict = doc['info']['metadata']['conceptClasses']['conceptClass']
        metaDataSet_dict = doc['info']['metadata']['dataSources']['dataSource']
        metaRelationship_dict = doc['info']['metadata']['relationTypes']['relationType']

        """ MetaData counts and names """
        metaCC_counts_list, metaCC_concept_list = metaDataListAppender(
            metaCC_dict)
        metaDS_counts_list, metaDS_name_list = metaDataListAppender(
            metaDataSet_dict)
        metaRS_counts_list, metaRS_name_list = metaDataListAppender(
            metaRelationship_dict)

        """ DataSource MetaData """
        # Create DF with all DS but plot the core DS
        dataframeCreatorWriter(meta_name_list=metaDS_name_list, meta_name_string='Datasource',
                               meta_counts_list=metaDS_counts_list, df_out_str=f"{output}/dataframes/dataset_counts.txt")

        # Get the Core datasets for plotting purposes - the rest are in a table
        matching_colons_DS = [elem for elem in metaDS_name_list if ":" in elem]
        DS_rm_index = [getIndex(metaDS_name_list, element)
                       for element in matching_colons_DS]
        rmMetaData(rm_index=DS_rm_index, name_list=metaDS_name_list,
                   count_list=metaDS_counts_list)
        # Get pandas series for counts in DS as method cannot be re-used above
        s2_metaDS_counts = pd.Series(metaDS_counts_list, name='Count')
        # Plot the DS figure
        plotFig(meta_counts_list=metaDS_counts_list, series_counts_pd=s2_metaDS_counts,
                x_size=20, y_size=8, title='Core Dataset counts (without merged datasets)',
                xlabel='Datasource', output_name='datasource_counts_barplt', label_height=5, meta_names_list=metaDS_name_list)

        """ Concept Class MetaData """
        # Create DF's and write out
        dataframeCreatorWriter(meta_name_list=metaCC_concept_list, meta_name_string='Concept Name',
                               meta_counts_list=metaCC_counts_list, df_out_str=f"{output}/dataframes/concept_counts.txt")

        if is_non_zero_file(input_sm) and input_sm is not None:
            names2rm = returnNotMatches(
                sm_concept_list, metaCC_concept_list)[0]
        else:
            names2rm = ['Thing', 'Transport', 'Protcmplx']

        rm_index = [getIndex(metaCC_concept_list, element)
                    for element in names2rm]
        rmMetaData(rm_index=rm_index, name_list=metaCC_concept_list,
                   count_list=metaCC_counts_list)
        s2_metaCC_counts = pd.Series(metaCC_counts_list, name='Count')
        # Plot CC metadata
        plotFig(meta_counts_list=metaCC_counts_list, series_counts_pd=s2_metaCC_counts,
                x_size=14, y_size=8, title='Concept class counts',
                xlabel='Concept', output_name='concept_counts_barplt', label_height=5, meta_names_list=metaCC_concept_list)

        """ Relationship MetaData """
        # Create DF's and write out
        dataframeCreatorWriter(meta_name_list=metaRS_name_list, meta_name_string='Semantic Motif',
                               meta_counts_list=metaRS_counts_list, df_out_str=f"{output}/dataframes/relationship_counts.txt")

        if is_non_zero_file(input_sm) and input_sm is not None:
            names2rm_RS = returnNotMatches(
                sm_relationships_list, metaRS_name_list)[0]
        else:
            names2rm_RS = ['pd_by', 'pos_reg', 'neg_reg',
                           'regulates', 'cs_by', 'ac_by']

        rm_index_Rs = [getIndex(metaRS_name_list, element)
                       for element in names2rm_RS]

        rmMetaData(rm_index=rm_index_Rs, name_list=metaRS_name_list,
                   count_list=metaRS_counts_list)
        s2_metaRS_counts = pd.Series(metaRS_counts_list, name='Count')
        # Plot RS bar chart
        plotFig(meta_counts_list=metaRS_counts_list, series_counts_pd=s2_metaRS_counts,
                x_size=30, y_size=10, title='Relationship counts',
                xlabel='Semantic Motif', output_name='relationships_counts_barplt', label_height=10, meta_names_list=metaRS_name_list)

        fd.close()
        print(f"\nFinished outputting graphs and dataframes. Time taken to do this was: {timeFormat(time()-start_time)}!\n")
except Exception as exc:
    print(f"\033[91mPlease provide a valid xml output file!\nError was: {exc}")
