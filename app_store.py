#!/usr/bin/env python2
#
# Copyright 2013 Tim O'Shea
#
# This file is part of PyBOMBS
#
# PyBOMBS is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# PyBOMBS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyBOMBS; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

from PyQt4.QtCore import Qt;
from PyQt4 import QtCore
import PyQt4.QtGui as QtGui
import sys
import os.path
from mod_pybombs import *;

try:
    print pybombs_ops.config_get("static")
except:
    pybombs_ops.config_set("static","False")

recipe_loader.load_all();

class AppList(QtGui.QWidget):
    def __init__(self, parent, name):
        super(AppList, self).__init__()
        self.parent = parent;
        self.lay = QtGui.QGridLayout();
        self.setLayout(self.lay);
        self.idx = 0;
        self.cbd = {};

    def cb(self):
        self._cb();

    def addButton(self, name, callback):
        self._cb = callback;
        pkgimg = "img/" + name + ".png";
        if os.path.exists(pkgimg):
            pixmap = QtGui.QPixmap(pkgimg); 
        else:
            defaultimg = "img/unknown.png";
            pixmap = QtGui.QPixmap(defaultimg);
        icon = QtGui.QIcon(pixmap);
        button = QtGui.QToolButton();
        action = QtGui.QAction( icon, str(name), self );
        action.setStatusTip('Install App')
        button.setDefaultAction(action);
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon);
        button.setIconSize(QtCore.QSize(self.parent.iconsize,self.parent.iconsize));
        button.setAutoRaise(True);
        self.connect(action, QtCore.SIGNAL("triggered()"), callback);
        self.lay.addWidget(button, self.idx/self.parent.width, self.idx%self.parent.width);
        self.idx = self.idx + 1;

class Installer:
    def __init__(self, parent, name):
        self.parent = parent;
        self.name = name;
    
    def cb(self):
        print "installing "+ self.name;
        install(self.name);
        self.parent.refresh();

class Remover:
    def __init__(self, parent, name):
        self.parent = parent;
        self.name = name;

    def cb(self):
        print "removing "+ self.name;
        remove(self.name);
        self.parent.refresh();
    

class ASMain(QtGui.QWidget):
#class ASMain(QtGui.QMainWindow):
    def __init__(self):
        self.width = 8;
        self.iconsize = 72

        super(ASMain, self).__init__()

        self.setWindowTitle("Python Build Overlay Managed Bundle System - APP STORE GUI");
        self.layout = QtGui.QVBoxLayout(self);
        self.setLayout(self.layout);

        self.menu = QtGui.QMenuBar(self);

        # Official GNU Radio logo
        # please see http://www.gnuradio.org
        pixmap = QtGui.QPixmap("img/logo.png")
        lbl = QtGui.QLabel(self)
        lbl.setPixmap(pixmap)

        l2 = QtGui.QHBoxLayout();
        l2.addWidget(QtGui.QLabel(" "));
        l2.addWidget(lbl);
        l2.addWidget(QtGui.QLabel(" "));

        self.tw = QtGui.QTabWidget(self);
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setWidget(self.tw)
        self.scrollArea.setWidgetResizable(True);

        self.layout.setMargin(0);

        self.layout.addWidget(self.menu);
        self.layout.addLayout(l2);
        self.layout.addWidget(self.scrollArea);

        # Populate Apps
        self.populate_tabs();

        # Populate the menu
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.triggered.connect(QtGui.qApp.quit)

        fileMenu = self.menu.addMenu('&File');
        fileMenu.addAction(exitAction);

        reloadAction = QtGui.QAction('&Refresh State', self)
        reloadAction.triggered.connect(self.reload_op)

        toolsMenu = self.menu.addMenu('&Tools');
        toolsMenu.addAction(reloadAction);

        self.resize(self.iconsize * self.width * 2, self.iconsize * self.width)
        self.show();
  
    def reload_op(self):
        inv.loadc();
        recipe_loader.load_all();
        self.refresh();

    def refresh(self):
        self.populate_tabs();

    def populate_tabs(self): 
        self.tw.clear();

        #categories = ["baseline", "common"]
        categories = ["common"]

        cbs = {};

        pages = [];
        for c in categories:
            pages.append( "Available %s Apps"%(c) );
            pages.append( "Installed %s Apps"%(c) );

        #pages = ["Available Apps", "Installed Apps"];
        tabw = [];
        for p in pages:
            pp = AppList(self, p);
            tabw.append(pp);
            self.tw.addTab(pp, p);

        catpkg = get_catpkgs()

        for c in categories:
            cbs[c] = {};

            cidx = categories.index(c);
            pkgs = catpkg[c];
            pkgs.sort();
            for p in pkgs:
                installed = global_recipes[p].satisfy();
                if(installed):   
                    cbs[c][p] = Remover(self, p);
                    pcidx = 2*cidx+1;
                else:
                    cbs[c][p] = Installer(self, p);
                    pcidx = 2*cidx;
                tabw[pcidx].addButton(p, cbs[c][p].cb);

        self.cbs = cbs;


app = QtGui.QApplication(sys.argv)
mw = ASMain();   
sys.exit(app.exec_());



