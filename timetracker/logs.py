""" This module hoasts the Logger class used to store access the user's saved scores and settings in Dashboard """

import os
import pickle
import yaml
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSettings
import inspect

class Logger():
    def __init__(self):
        self.load_config()
        print(self.config)

    def load_config(self):
        with open("config.yml", 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                self.config = exc
        self.config['gui_cache_address'] = self.config['gui_cache_address'].replace('<DATE>','20191205')
        print(self.config['gui_cache_address'])

    def check_today(self):
        """ Check if cache for today's GUI exists """
        if os.path.exists(self.config['gui_cache_address']):
            return True
        else:
            return False

    # def load_today(self, ui, settings):
    #     """ Load the Dashboard instance """
    #     GuiRestore(ui, settings)
    #     # with open(self.config['gui_cache_address'], 'rb') as handle:
    #     #     data = pickle.load(handle)
    #     # return data
    #
    # def save_today(self, ui, settings):
    #     """ Save the Dashboard instance """
    #     GuiSave(ui, settings)
    #     # with open(self.config['gui_cache_address'], 'wb') as handle:
    #     #     pickle.dump(settings, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def GetHandledTypes(self):
        return (QComboBox, QLineEdit, QCheckBox, QRadioButton, QSpinBox, QSlider, QListWidget)

    def IsHandledType(self, widget):
        return any(isinstance(widget, t) for t in self.GetHandledTypes())

    def GuiSave(self, ui : QWidget, settings : QSettings, uiName="uiwidget"):
        """
        save "ui" controls and values to registry "setting"

        :param ui:
        :param settings:
        :param uiName:
        :return:
        """

        namePrefix = f"{uiName}/"
        settings.setValue(namePrefix + "geometry", ui.saveGeometry())

        for name, obj in inspect.getmembers(ui):
            if not self.IsHandledType(obj):
                continue

            name = obj.objectName()
            value = None
            if isinstance(obj, QComboBox):
                index = obj.currentIndex()  # get current index from combobox
                value = obj.itemText(index)  # get the text for current index

            if isinstance(obj, QLineEdit):
                value = obj.text()

            if isinstance(obj, QCheckBox):
                value = obj.isChecked()

            if isinstance(obj, QRadioButton):
                value = obj.isChecked()

            if isinstance(obj, QSpinBox):
                value = obj.value()

            if isinstance(obj, QSlider):
                value = obj.value()

            if isinstance(obj, QListWidget):
                settings.beginWriteArray(name)
                for i in range(obj.count()):
                    settings.setArrayIndex(i)
                    settings.setValue(namePrefix + name, obj.item(i).text())
                settings.endArray()
            elif value is not None:
                settings.setValue(namePrefix + name, value)


    def GuiRestore(self, ui : QWidget, settings : QSettings, uiName="uiwidget"):
        """
        restore "ui" controls with values stored in registry "settings"

        params
        ------
        :param ui:
        :param settings:
        :param uiName:

        """
        from distutils.util import strtobool

        namePrefix = f"{uiName}/"
        geometryValue = settings.value(namePrefix + "geometry")
        if geometryValue:
            ui.restoreGeometry(geometryValue)

        for name, obj in inspect.getmembers(ui):
            if not self.IsHandledType(obj):
                continue

            name = obj.objectName()
            value = None
            if not isinstance(obj, QListWidget):
                value = settings.value(namePrefix + name)
                if value is None:
                    continue

            if isinstance(obj, QComboBox):
                index = obj.findText(value)  # get the corresponding index for specified string in combobox

                if index == -1:  # add to list if not found
                    obj.insertItems(0, [value])
                    index = obj.findText(value)
                    obj.setCurrentIndex(index)
                else:
                    obj.setCurrentIndex(index)  # preselect a combobox value by index

            if isinstance(obj, QLineEdit):
                obj.setText(value)

            if isinstance(obj, QCheckBox):
                obj.setChecked(strtobool(value))

            if isinstance(obj, QRadioButton):
                obj.setChecked(strtobool(value))

            if isinstance(obj, QSlider):
                obj.setValue(int(value))

            if isinstance(obj, QSpinBox):
                obj.setValue(int(value))

            if isinstance(obj, QListWidget):
                size = settings.beginReadArray(namePrefix + name)
                for i in range(size):
                    settings.setArrayIndex(i)
                    value = settings.value(namePrefix + name)
                    if value is not None:
                        obj.addItem(value)
                settings.endArray()