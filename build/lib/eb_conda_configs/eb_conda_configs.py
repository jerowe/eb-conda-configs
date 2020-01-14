"""
Create Easybuild configs from conda packages
Create an EasyBuild Config for a Single Conda Package:
1. You can create an easybuild config using the anaconda client show syntax. If you do not specify a version the latest will be pulled in for you.
    python ./create_eb_configs_from_conda_packages.py module -p bioconda/samtools/1.9 bioconda/trimmomatic/0.39 bioconda/fastqc
Will create the easybuild config files samtools-1.9.eb, trimmomatic-0.39.eb and fastqc-0.11.8.eb
2. Create an EasyConfig Bundle from 1 or more conda packages. This will also create any Conda EasyConfigs
    python ./create_eb_configs_from_conda_packages.py conda_bundle -n qc -v 1.0 -p bioconda/trimmomatic/0.39 bioconda/fastqc
3. Create a EasyConfig Bundle from modules (conda or not)
    python ./create_eb_configs_from_conda_packages.py bundle -n qc -v 1.0 -m trimmomatic=0.39 fastqc=0.11.8
"""

from binstar_client.utils import get_server_api, parse_specs
import argparse
from jinja2 import Environment, BaseLoader

aserver_api = get_server_api()


def write_eb_bundle_config(name, version, dependencies):
    eb_bundle_config = '''
easyblock = 'Bundle'
name = '{{name}}'
version = '{{version}}'
#Change the homepage!
homepage = 'none'
description = """Module for {{name}}"""
toolchain = SYSTEM 
dependencies = [
    {%- for i in dependencies %}
         ('{{i.name}}', '{{i.version}}'),
    {%- endfor %}
]
moduleclass = 'bio'
    '''
    data = {
        'name': name,
        'version': version,
        'dependencies': dependencies,
    }
    rtemplate = Environment(loader=BaseLoader).from_string(eb_bundle_config)
    rendered_data = rtemplate.render(**data)
    with open("{}-{}.eb".format(name, version), "w") as text_file:
        text_file.write(rendered_data)


def write_eb_conda_config(name, version, homepage, summary):
    eb_conda_config = '''##
# This is an easyconfig file for EasyBuild, see https://github.com/easybuilders/easybuild
##
easyblock = 'Conda'
name = "{{name}}"
version = "{{version}}"
homepage = '{{homepage}}'
description = """{{summary}}"""
toolchain = SYSTEM
requirements = "%(name)s=%(version)s"
channels = ['bioconda', 'conda-forge']
builddependencies = [('Miniconda3', '4.7.10')]
sanity_check_paths = {
    'files': ['bin/python'],
    'dirs': ['bin']
}
moduleclass = 'bio'
    '''
    data = {
        'homepage': homepage,
        'name': name,
        'version': version,
        'summary': summary
    }
    rtemplate = Environment(loader=BaseLoader).from_string(eb_conda_config)
    data = rtemplate.render(**data)
    with open("{}-{}.eb".format(name, version), "w") as text_file:
        text_file.write(data)


def write_eb_conda_config_many_requirements(name, version, dependencies):
    eb_conda_config = '''##
# This is an easyconfig file for EasyBuild, see https://github.com/easybuilders/easybuild
##
easyblock = 'Conda'
name = "{{name}}"
version = "{{version}}"
homepage = "none"
description = """EB Config for {{name}}"""
toolchain = SYSTEM
requirements = "{% for i in dependencies %} {{i.name}}={{i.version}} {% endfor %}"
channels = ['bioconda', 'conda-forge']
builddependencies = [('Miniconda3', '4.7.10')]
sanity_check_paths = {
    'files': ['bin/python'],
    'dirs': ['bin']
}
moduleclass = 'bio'
    '''
    data = {
        'name': name,
        'version': version,
        'dependencies': dependencies,
    }
    rtemplate = Environment(loader=BaseLoader).from_string(eb_conda_config)
    data = rtemplate.render(**data)
    with open("{}-{}.eb".format(name, version), "w") as text_file:
        text_file.write(data)


def get_package_data(package):
    specs = parse_specs(package)

    if not specs._package:
        raise Exception('You did not specify a package!')

    package_data = aserver_api.package(specs.user, specs.package)
    latest_version = package_data['latest_version']
    summary = package_data['summary']
    if specs.user == 'bioconda':
        homepage = 'https://bioconda.github.io/recipes/{}/README.html'.format(specs.package)
    else:
        homepage = 'homepage'

    version = latest_version
    if specs._version:
        version = specs.version

    return specs.package, version, homepage, summary


def bundle(**kwargs):
    dependencies = []
    for module in kwargs['modules']:
        t = module.split('=')
        dependencies.append({'version': t[1], 'name': t[0]})
    write_eb_bundle_config(kwargs['name'], kwargs['version'], dependencies)


def module(**kwargs):
    if kwargs['combine']:
        if not kwargs['name']:
            raise Exception('You must supply a name when using the -c/--combine argument')
        if not kwargs['version']:
            kwargs['version'] = '1.0'
        dependencies = []
        for package in kwargs['packages']:
            name, version, homepage, summary = get_package_data(package)
            dependencies.append({'name': name, 'version': version})
        write_eb_conda_config_many_requirements(kwargs['name'], kwargs['version'], dependencies)
    else:
        for package in kwargs['packages']:
            name, version, homepage, summary = get_package_data(package)
            write_eb_conda_config(name, version, homepage, summary)


def conda_bundle(**kwargs):
    dependencies = []
    for package in kwargs['packages']:
        name, version, homepage, summary = get_package_data(package)
        dependencies.append({'name': name, 'version': version})
    write_eb_bundle_config(kwargs['name'], kwargs['version'], dependencies)


def add_name_arg(subparser, required=True):
    subparser.add_argument('--name', '-n',
                           required=required,
                           help="""Module name to use with module load.""")


def add_version_arg(subparser, required=True):
    subparser.add_argument('--version', '-v',
                           required=required,
                           help="""Module version to use with module load.""")


def add_package_arg(subparser, required=True):
    subparser.add_argument('--packages', '-p',
                           nargs='+',
                           required=required,
                           help="""Packages to install as modules. 
                                      Package should be in format channel/name or channel/name/version.
                                      Example: bioconda/samtools/1.9
                                      You can specify more than 1 package by putting a space between.
                                      Example: bioconda/samtools/1.9 bioconda/samtools/1.8""")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='subparser',
                                       description='valid subcommands',
                                       help='Choose a valid subcommand')

    module_subparser = subparsers.add_parser('module')
    add_package_arg(module_subparser, True)
    add_name_arg(module_subparser, False)
    add_version_arg(module_subparser, False)
    module_subparser.add_argument('--combine', '-c',
                                  action='store_true', default=False,
                                  help="""
    Combine conda packages into a single module. 
    This is useful for R or Python environments that require libraries to be in the same environment.
    
    Example: -p conda-forge/r conda-forge/r-tidyverse
    Would translate to Easybuild executing - 
    conda create -n name-of-module r r-tidyverse
    
    Example: -p conda-forge/python/3.6 conda-forge/ipython conda-forge/pandas
    Would translate to Easybuild executing - 
    conda create -n name-of-module python=3.6 ipython pandas 
    """)

    bundle_subparser = subparsers.add_parser('bundle')
    add_name_arg(bundle_subparser, True)
    add_version_arg(bundle_subparser, True)
    bundle_subparser.add_argument('--modules', '-m',
                                  nargs='+',
                                  help="""Modules to include in the bundle. 
                                      Package should be in format name=version.
                                      Example: samtools=1.9""")

    conda_bundle_subparser = subparsers.add_parser('conda_bundle')
    add_name_arg(conda_bundle_subparser, True)
    add_version_arg(conda_bundle_subparser, True)
    add_package_arg(conda_bundle_subparser, True)

    kwargs = vars(parser.parse_args())

    if kwargs['subparser'] is not None:
        subparser = kwargs.pop('subparser')
        globals()[subparser](**kwargs)
    else:
        parser.parse_args(['-h'])


if __name__ == '__main__':
    main()
