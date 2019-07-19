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

class bcolours:
    """ Useful print outs for the console - colours et al., """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def createFile(path):
    """ Creates the file path if it doesn't exist"""
    if os.path.exists(path):
        pass
    else:
        os.makedir(path)

def pretty_print_xml(xml, output):
    """ Pretty prints XML data """
    #Use xmllint natively to format data
    command = f"xmllint --format {xml} > {output}"
    run(command,shell=True)

def getIndex(list, element):
    """ Obtains the Index of specific elements in the list provided """
    index = list.index(element)
    return index

def metaDataListAppender(metaDict):
    """ Obtains the meta data counts and name from the XML data source """
        # Append to meta data concept class list with the concepts and their counts
        meta_count_list = []
        for slice in metaDict:
            for key, val in slice.items():
                meta_count_list.append(val)

        meta_count_dict = dict(itertools.zip_longest(*[iter(meta_count_list)] * 2, fillvalue=""))

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


""" User Args """
parser = argparse.ArgumentParser(
    description="This script will perform read through the report output from Ondex and provide statistical outputs\n")
# Args init
parser.add_argument(
    '-in', '--input_file', help='Specify the location of the report xml.', required=True)
parser.add_argument(
    '-out', '--output_dir', help='Specify the output of the stats.', required=True)

input = args['input_file']
output = args['output_dir']
output = output.rstrip("/") if output.endswith('/') else output
output = output.replace("\\", "") if output.find("\\") else output

if input is not None:
    if input.endswith(".xml"):

        folder_list = [f"{output}/barplots", f"{output}/dataframes"]
        [createFile(folder) for folder in folder_list]
        pretty_print_xml(xml=input, output = f"{output}/report.xml")

        # Iterate through the report
        with open(f"{output}/report.xml") as fd:
            doc = xmltodict.parse(fd.read())

            """ Total Counts """
            tot_concept_count = doc['info']['general']['numberOfConcepts']
            tot_relationship_count = doc['info']['general']['numberOfRelations']

            print(f"Total number of concept counts is : {bcolours.FAIL}{tot_concept_count}{bcolours.ENDC},"
                  f" the total number of relationship counts is {bcolours.FAIL}{tot_relationship_count}{bcolours.ENDC}\n\n")

            """ MetaData """
            metaCC_dict = doc['info']['metadata']['conceptClasses']['conceptClass']
            metaDataSet_dict= doc['info']['metadata']['dataSources']['dataSource']
            metaRelationship_dict = doc['info']['metadata']['relationTypes']['relationType']


            metaCC_counts_list, metaCC_concept_list = metaDataListAppender(metaCC_dict)
            metaDS_counts_list, metaDS_name_list = metaDataListAppender(metaDataSet_dict)
            metaRS_counts_list, metaRS_name_list = metaDataListAppender(metaRelationship_dict)

            """ DataSource MetaData """
            # Create DF with all DS but plot the core DS
            dataframeCreatorWriter(meta_name_list=metaDS_name_list, meta_name_string='Datasource',
                                   meta_counts_list=metaDS_counts_list, df_out_str=f"{output}/dataframes/dataset_counts.txt")


            # Get the Core datasets for plotting purposes - the rest are in a table
            matching_colons_DS = [elem for elem in metaDS_name_list if ":" in elem]
            DS_rm_index = [getIndex(metaDS_name_list, element) for element in matching_colons_DS]
            rmMetaData(rm_index=DS_rm_index, name_list=metaDS_name_list, count_list=metaDS_counts_list)
            # Get pandas series for counts in DS as method cannot be re-used above
            s2_metaDS_counts = pd.Series(metaDS_counts_list, name='Count')
            # Plot the DS figure
            red_bar_ds = metaDS_counts_list.index(max(s2_metaDS_counts))

            fig_ds_counts = plt.figure(figsize=(20,8))
            ax_DS = s2_metaDS_counts.plot(kind='bar')
            ax_DS.set_title('Core Dataset counts (without merged datasets)')
            ax_DS.set_xlabel('Datasource')
            ax_DS.set_ylabel('Counts')
            ax_DS.set_xticklabels(s2_metaDS_counts)
            rects_DS = ax_DS.patches
            ax_DS.patches[red_bar_ds].set_facecolor('#aa3333')

            for rect_ds, metaDS_name_list in zip(rects_DS, metaDS_name_list):
                heights_ds = rect_ds.get_height()
                ax_DS.text(rect_ds.get_x() + rect_ds.get_width()/2, heights_ds + 5, metaDS_name_list,
                        ha='center', va='bottom')

            fig_ds_counts.savefig(f'{output}/barplots/datasource_counts_barplt.png')

            """ Concept Class MetaData """
            # Obtain indexes of Thing, Transport and Protcomplex to remove - can later change this to be a user option
            names2rm = ['Thing', 'Transport', 'Protcmplx']
            rm_index = [getIndex(metaCC_concept_list, element) for element in names2rm]
            rmMetaData(rm_index=rm_index, name_list=metaCC_concept_list, count_list=metaCC_counts_list)
            s2_metaCC_counts = pd.Series(metaCC_counts_list, name='Count')

            # Create DF's and write out
            dataframeCreatorWriter(meta_name_list=metaCC_concept_list, meta_name_string='Concept Name',
                                   meta_counts_list=metaCC_counts_list, df_out_str=f"{output}/dataframes/concept_counts.txt")

            # Plot the CC figure
            red_bar_cc = metaCC_counts_list.index(max(s2_metaCC_counts))

            fig_cc_counts = plt.figure(figsize=(14,8))
            ax_cc = s2_metaCC_counts.plot(kind='bar')
            ax_cc.set_title('Concept class counts')
            ax_cc.set_xlabel('Concept')
            ax_cc.set_ylabel('Counts')
            ax_cc.set_xticklabels(s2_metaCC_counts)
            rects = ax_cc.patches
            ax_cc.patches[red_bar_cc].set_facecolor('#aa3333')

            for rect, metaCC_concept_list in zip(rects, metaCC_concept_list):
                heights = rect.get_height()
                ax_cc.text(rect.get_x() + rect.get_width()/2, heights + 5, metaCC_concept_list,
                        ha='center', va='bottom')

            fig_cc_counts.savefig(f'{output}/barplots/concept_counts_barplt.png')

            """ Relationship MetaData """
            # Create DF's and write out
            dataframeCreatorWriter(meta_name_list=metaRS_name_list, meta_name_string='Semantic Motif',
                                   meta_counts_list=metaRS_counts_list, df_out_str=f"{output}/dataframes/relationship_counts.txt")

            names2rm_RS = ['cat_c', 'pd_by', 'pos_reg', 'neg_reg', 'regulates', 'cs_by', 'ac_by', 'located_in']
            rm_index_Rs = [getIndex(metaRS_name_list, element) for element in names2rm_RS]
            rmMetaData(rm_index=rm_index_Rs, name_list=metaRS_name_list, count_list=metaRS_counts_list)
            s2_metaRS_counts = pd.Series(metaRS_counts_list, name='Count')

            # Plot the CC figure
            red_bar_RS = metaRS_counts_list.index(max(s2_metaRS_counts))

            fig_RS_counts = plt.figure(figsize=(30,10))
            ax_RS = s2_metaRS_counts.plot(kind='bar')
            ax_RS.set_title('Relationship counts')
            ax_RS.set_xlabel('Semantic Motif')
            ax_RS.set_ylabel('Counts')
            ax_RS.set_xticklabels(s2_metaRS_counts)
            rects_RS = ax_RS.patches
            ax_RS.patches[red_bar_RS].set_facecolor('#aa3333')

            for rects_RS, metaRS_name_list in zip(rects_RS, metaRS_name_list):
                heights = rects_RS.get_height()
                ax_RS.text(rects_RS.get_x() + rects_RS.get_width()/2, heights + 10, metaRS_name_list,
                        ha='center', va='bottom')

            fig_RS_counts.savefig(f'{output}/barplots/relationships_counts_barplt.png')

else:
    print(f"{bcolours.FAIL}Please provide a valid xml output file!\n")
