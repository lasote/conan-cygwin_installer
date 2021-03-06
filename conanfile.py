#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools
import os


class CygwinInstallerConan(ConanFile):
    name = "cygwin_installer"
    version = "2.9.0"
    license = "https://cygwin.com/COPYING"
    description = "Cygwin is a distribution of popular GNU and other Open Source tools running on Microsoft Windows"
    url = "https://github.com/bincrafters/conan-cygwin_installer"
    settings = {"os": ["Windows"], "arch": ["x86", "x86_64"]}
    install_dir = 'cygwin-install'
    short_paths = True

    def build(self):
        filename = "setup-%s.exe" % self.settings.arch
        url = "https://cygwin.com/%s" % filename
        tools.download(url, filename)

        if not os.path.isdir(self.install_dir):
            os.makedirs(self.install_dir)

        # https://cygwin.com/faq/faq.html#faq.setup.cli
        command = filename
        command += ' --arch %s' % self.settings.arch
        # Disable creation of desktop and start menu shortcuts
        command += ' --no-shortcuts'
        # Do not check for and enforce running as Administrator
        command += ' --no-admin'
        # Unattended setup mode
        command += ' --quiet-mode'
        command += ' --root %s' % os.path.abspath(self.install_dir)
        # TODO : download and parse mirror list, probably also select the best one
        command += ' -s http://cygwin.mirror.constant.com'
        packages = ['pkg-config', 'make', 'libtool', 'binutils', 'gcc-core', 'gcc-g++']
        command += ' --packages %s' % ','.join(packages)
        self.run(command)

        os.unlink(filename)

        # create /tmp dir in order to avoid
        # bash.exe: warning: could not find /tmp, please create!
        tmp_dir = os.path.join(self.install_dir, 'tmp')
        if not os.path.isdir(tmp_dir):
            os.makedirs(tmp_dir)
        tmp_name = os.path.join(tmp_dir, 'dummy')
        with open(tmp_name, 'a'):
            os.utime(tmp_name, None)

    def package(self):
        self.copy(pattern="*", dst=".", src=self.install_dir)

    def fix_symlinks(self):
        path = os.path.join(self.package_folder, 'bin', '*')
        self.run('attrib -r +s /D "%s" /S /L' % path)

    def package_info(self):
        # workaround for error "cannot execute binary file: Exec format error"
        # symbolic links must have system attribute in order to work properly
        self.fix_symlinks()

        cygwin_root = self.package_folder
        cygwin_bin = os.path.join(cygwin_root, "bin")
        
        self.output.info("Creating CYGWIN_ROOT env var : %s" % cygwin_root)
        self.env_info.CYGWIN_ROOT = cygwin_root
        
        self.output.info("Creating CYGWIN_BIN env var : %s" % cygwin_bin)
        self.env_info.CYGWIN_BIN = cygwin_bin

        self.output.info("Appending PATH env var with : " + cygwin_bin)
        self.env_info.path.append(cygwin_bin)
              