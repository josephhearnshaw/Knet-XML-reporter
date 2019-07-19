# Knet-XML-reporter
Reports metadata in bar charts and formatted data frame outputs for ONDEX report output (plugin required to obtain this output). 

# Requirements 

Any version of [Python 3](https://www.python.org/) or greater is required.

The following modules are also required to be installed within your Py environment:

* [argparse](https://pypi.org/project/argparse/)
* [xmltodict](https://pypi.org/project/xmltodict/)
* [pandas](https://pypi.org/project/pandas/)
* [numpy](https://pypi.org/project/numpy/)
* [matplotlib](https://pypi.org/project/matplotlib/)
* [time](https://pypi.org/project/time/)


# Example use

Example usage: 

`python3 knet_xml_report.py -in=/path/report.xml -out=/path/output_reports`

# Future plans

TODO - make filtering optional and add options to set graph sizes and what to filter by. Booleans will be added for options. 
