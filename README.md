# elephant-tools
A set of python tools to explore the Myanmar Elephant Project demographic dataset at University of Turku.

**INSTALL**

Everything will be easier if you start by installing Anaconda (or Miniconda) for Python3 (version 3.5 or later) from the Anaconda website: https://www.anaconda.com/download/#linux
Then install the following dependencies (if not yet matched): scipy, numpy, pymysql, ete3, etetoolkit, PILLOW.
If using Anaconda, open your terminal (or cmd.exe on Windows) and enter:

**conda install -c scipy numpy pymysql etetoolkit ete3 PILLOW**

Note that you will need Tcl/tk toolkit version >= 8.6. You can upgrade it on your system, and proceed to upgrade the Python library with:

**conda install -c anaconda tk**

Then proceed to download the module. If in OSX or Linux, use:

**git clone https://github.com/rcristofari/elephant-tools.git**

In Windows, if you do not have git installed, just download using the direct download link.

Then move to the download directory in your terminal:

**cd /your/download/dir/elephant-tools-master/**

And run the installer. You will need superuser permissions. On OSX or Linux, type:

**sudo python3 setup.py install**

On Windows, open your cmd.exe as Administrator, and type:

**python setup.py install**

You can then run the program with:

**./ElephantGUI.py**

------------------------------------------------------------------

**We are a multi-disciplinary research group based at the University of Turku, Finland and the University of Sheffield, UK, studying a large and unique semi-captive population of timber elephants in Myanmar.**

*Our individual-based study uses a detailed longitudinal data set, which combines several decades of demographic data on the entire population with a more recent collection of data on individual phenotypes in the field. Myanmar has the largest captive Asian elephant population in the world but low rates of survival and reproduction necessitate capture of wild elephants to maintain the working population. The health of the captive population is therefore tightly linked to the endangered wild population. Our research aims to determine factors affecting health, fertility and mortality rates in the captive population and devising strategies to improve them.*

More details on [our webpage](http://www.elephant-project.science/)
