# Knet-XML-reporter
Reports metadata in figures and formatted files for ONDEX output. 

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

`python3 -in=/path/report.xml -out=/path/output_reports`

# Future plans

TODO - make filtering optional and add options to set graph sizes and what to filter by. Also refactor the figure plotting bodies as it's repetitive. 
