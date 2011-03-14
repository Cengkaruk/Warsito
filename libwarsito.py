#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""Warung Aplikasi Builder module.

Exported class :
BuildOnPackage -- Class for creating BlankOn Package

"""

import os
import tarfile
import string
import apt
from hashlib import md5
import gettext
import tempfile
import apt_pkg
import shutil
import warsiexceptions
import urllib
import apt.progress.gtk2
from apt_inst import debExtractControl
import ConfigParser
from libwarsi import OnPackage

class BuildOnPackage(object):
    """
    BuildOnPackage -- Class for creating BlankOn Package
    """
    def __init__(self):
        self.cache = apt.Cache(apt.progress.text.OpProgress())

    def WarsitoConfig(self, configfile):
        """Warsito configurations

        Arguments:
        configfile - A string, config file destination

        Result:
        config - A dict

        """
        config = {}
        arch = []

        configparser = ConfigParser.ConfigParser()
        try:
            configparser.read(configfile)
            
            for section in configparser.sections():
                options = Config.options(section)
                for option in options:
                    try:
                        if option == "ARCH":
                            lines = Config.get(section, option)
                            for line in lines:
                                arch.append(line)
                            config[option] = arch
                            continue
                        config[option] = Config.get(section, option)
        except ConfigParser.Error:
            raise ex.WarsiIOError(_("Cannot read warsito configuration"))
        
        return config

    def WarsitoSetConfig(self, *args):
        """Set warsito configurations

        Arguments:
        *args - arguments of config

        Returns:
        TRUE or FALSE

        """

    def create(self, pkg, seed, config):
        """Creating BlankOn Package

        Arguments:
        pkgs - A String, name of package (debian package)
        seed - A String, seed config
        config - A Dict, from WarsitoConfig

        Returns:
        on_pkg - A string, BlankOn Package file

        """
        urls = []
        if self.cache.has_key(pkg):
            main_pkg = self.cache[pkg]
            dist = config['DIST'] + config['VERSION']
            dir = self.prepare_dir(main_pkg, dist)
            main_url = self.show_url(main_pkg)
            urls.append(main_url)
            check_deps = self.check_deps(pkg)
            check_base = BuildOnPackage.base_packages(build, seed)
            for dep in check_deps:
                for base in check_base:
                    if not dep == base:
                        urls.append(dep)
        else:
            raise ex.BuildCreateError(_('{0} is not found'.format(pkg)))

        down_pkgs = self.download_packages(dir['datadir'], urls)
        self.manifest(dir['tempdir'], dir['datadir'])
        self.blankinfo(dir['tempdir'], down_pkgs[0])
        on_pkg = self.compress(dir['tempdir'], config['RESULTDIR'])

        return on_pkg

    def compress(self, pkgdir, resultdir, config):
        """Compres Package

        Compressing BlankOn Package with lzma, bz2, or gz archive.

        Arguments:
        pkg - A String, name in BlankOn Package
        config - A Dict, Config Parser

        Returns:
        on - A String, BlankOn Package file

        """

        compression_type = config['COMPRESSION']

        if not compression_type:
            compression_type = "default"

        if compression_type == "default":
            
        elif compression_type == "bz2":
            fileon = pkgdir + ".on"
            on = tarfile.open(fileon, 'w:bz2')
            on.add(pkgdir)
            on.close()
        elif compression_type == "gz":
            

        return on

    def manifest(self, tempdir, datadir):
        """Create Manifest file

        Create all checksum of debian packages

        Arguments:
        tempdir - A String, destination of temporary directory
        datadir - A Sring, Data temporary directory

        Returns:
        sumsfile - A String, checksums file

        """
        for deb in os.listdir(datadir):
            debfile = os.path.join(datadir, deb)
            s = md5(open(debfile, "rb").read()).hexdigest()
            sumsfile = os.path.join(tempdir, 'blank.manifest')
            manifest = open(sumsfile, "a")
            manifest.write(deb)
            manifest.write(" : %s\n" %s)
            manifest.close()

        return sumsfile

    def blankinfo(self, tempdir, pkg):
        """Create Package Info file

        Arguments:
        temdir - A String, destination of temporary directory
        pkg - A String, main deb package

        Results:
        control - A String, info file

        """
        abs_pkg = os.path.abspath(pkg)
        controlfile = debExtractControl(abs_pkg)
        infofile = os.path.join(tempdir, 'blank.info')
        control = open(infofile, "a")
        control.write(controlfile)
        control.close()

        return control

    def show_url(self, pkg):
        """Show Url

        Show url of debian packages

        Arguments:
        pkg - A cache object

        Returns:
        url - A String, debian package url

        """
        return pkg.versions[0].uri
	
    def prepare_dir(self, pkg, dist):
        """Prepare Temporary Directory

        Arguments:
        pkg - A String, name of package
        dist - A String, distribution name of BlankOn

        Returns:
        dir - A String, temporary directory

        """
        name = []
        name.append(pkg.name)
        name.append(pkg.versions[0].version)
        name.append(dist)
        name.append(pkg.versions[0].architecture)
        separator = "_"
        name_dir = separator.join(name)

        tmp = tempfile.gettempdir()
        dir = {}
        dir_name = os.path.join(tmp, name_dir)
        dir['tempdir'] = dir_name

        if not os.path.lexists(dir_name):
            try:
                os.mkdir(dir_name)
            except os.error:
                raise ex.BuildPreparationError(_("Cannot create temporary directory."))

        data_dir = os.path.join(dir_name, "data")
        dir['datadir'] = data_dir

        if not os.path.lexists(data_dir):
            try:
                os.mkdir(data_dir)
            except os.error:
                raise ex.BuildPreparationError(_("Cannot create temporary directory."))
	
        return dir

    def check_deps(self, pkg):
        """Check Dependencies

        Arguments:
        pkg - A String, name of package

        Returns:
        pkgs - A List, dependencies package

        """
        for dep_pkg in pkg.candidate.dependencies:
            pkgs = []
            for dep in dep_pkg.or_dependencies:
                name = dep.name
                
                if self.cache.has_key(name):
                    pkg_cache = self.cache[name]
                    
                    pkgs.append(pkg_cache)

        return pkgs

    def download_packages(self, datadir, urls):
        """Download Packages

        Arguments:
        datadir - A String, temporary directory
        urls - A List, url of packages

        Returns:
        localfiles - A List, downloaded package    

        """
        localfiles = []
        for url in urls:
            webfile = urllib.urlretrieve(url, datadir)
            file = open(url.split('/')[-1], 'w')
            localfile = os.path.join(datadir, file)

            localfiles.append(localfile)

        return localfiles

    def base_packages(self, seed):
        """List all base packages from seed configuration

        Arguments:
        seed - A seed config file

        Returns:
        pkgs - A List, all base packages    

        """
        packages = []
        try:
            f = open(seed, "r")
            try:
                lines = f.readlines()
                for line in lines:
                    if line.startwith(" #"):
                        continue
                    elif line.startswith(" *"):
                        item = line.split(" ")[1]
    
                        package = re.sub(r'[\()]', '', item)
                        pakages.append(package)
            finally:
                f.close()
        except IOError:
            raise ex.WarsiIOError(_("Cannot read seed configuration"))  

        return packages  

class Repository(object):
    """
    Repository -- Class for syncronizing BlankOn Packages repository
    """
    
    def listresultdir(self):

    def listresultpath(self):
    
    def sync(self):
        """Sync result packages to public repository
            
        """

    def create_packages_info(self, config, pkgs):
        """Creating Packages.info Information

        """
        public_dir = config["PUBLICDIR"]
        distdir = os.path.join(public_dir, config["DIST"])
        ondir = os.path.join(distdir, config["ARCH"])

        for on in os.listdir(ondir):
            for pkg in pkgs:
                on_name = on.split("_")[0]

                if on_name == pkg:
                    info = OnPackage.show_info(on, pkg)
                    md5sum = md5(open(on, "rb").read()).hexdigest()
                    size = os.path.getsize(on)
                    infofile = os.path.join(ondir, 'Packages.info')
                    package_info = open(infofile, "a")
                    package_info.write("[%s]" %info['Package'])
                    package_info.write("Version: %s" %info['Version'])
                    package_info.write("Architecture: %s" %info['Architecture'])
                    package_info.write("Description: %s" %info['Description'])
                    package_info.write("Section: %s" %info['Section'])
                    package_info.write("Homepage: %s" %info['Homepage'])
                    package_info.write("Filename: %s" %info['Filename'])
                    package_info.write("Size: %s" %size)
                    package_info.write("MD5sum: %s" %md5sum)

class Utils(object):
    """
    Utilities
    """
    
    def cronjob(self):
    
