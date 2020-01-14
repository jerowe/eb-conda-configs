# Create EasyBuild EasyConfigs for Conda Packages

This is a small wrapper script meant to help with creating [EasyConfigs](https://github.com/easybuilders/easybuild-easyconfigs) with Conda packages. Much of the metadata needed to write an EasyConfig is available using the anaconda client.

## Installation

Install with pip.

```
```

## Create an EasyConfig for a single Conda package

### Example - Create an EasyConfig for the Bioconda Trimmomatic Package

The CLI uses the anaconda-client syntax. The package syntax is {{channel}}/{{name}} or optionally, {{channel}}/{{name}}/{{version}}. 

#### Latest Version

If you don't specify a version the cli will pull in the information for the most recent version for you.

```
eb_conda_configs module -p bioconda/fastqc
```

#### Specify a Version

```
eb_conda_configs module -p bioconda/fastqc/0.11.8
```

## Create an EasyConfig for many Conda Packages
 
This is most useful with R or Python environments where the R/Python interpreter expects the packages to all be in the same environment. If you are creating modules for multiple command line utilities it is better to use the EasyBuild Bundle functionality.

### Example Python Environment

This would create an EasyConfig that loads a single conda environment named python-dev, which has the ipython and pandas libraries installed.

Underneath the hood the `eb` cli would run `conda create -n python-dev -c conda-forge ipython=latest-version python=latest-version pandas=latest-version`.

```
eb_conda_configs module -name python-dev -version 1.0 -c -p conda-forge/ipython conda-forge/python conda-forge/pandas 
```
 
### Example R Environment

Underneath the hood the `eb` cli would run `conda create -n python-dev -c conda-forge r=latest-version r-shiny=latest-version r-tidyverse=latest-version`.

```
eb_conda_configs module -name python-dev -version 1.0 -c -p conda-forge/r conda-forge/r-shiny conda-forge/r-tidyverse
```

## Create a Bundle EasyConfig to load many modules

If you have many command line utilities you want to load together use the `bundle` sub command.

This command will create 3 modules:

 1. An EasyConfig Bundle named `qc` with version `1.0`, 
 2. A Conda EasyConfig for trimmomatic 
 3. A Conda Easyconfig for fastqc. 
 
When you deploy the module and run `module load qc/1.0` it will also load the trimmomatic and fastqc modules with no intervention. This is an especially good option for projects with complex dependencies that require careful pinning.

```
eb_conda_configs conda_bundle -n qc -v 1.0 -p bioconda/trimmomatic/0.39 bioconda/fastqc
```

You can also use this command to create bundles for already deployed modules and/or modules that aren't from conda packages. 

```
eb_conda_configs conda_bundle -n qc -v 1.0 \
    -p bioconda/trimmomatic/0.39 bioconda/fastqc
    -m intel=1.0 
```
