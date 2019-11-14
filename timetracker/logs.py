""" This module hoasts the Logger class used to store access the user's saved scores and settings in gui """

import os
import pickle
import numpy as np
import h5py
import yaml
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSettings
import inspect
from pprint import pprint

class Logger():
    def __init__(self):
        self.load_config()
        self.day = '20191205'
        print(self.config)

    def load_config(self):
        with open(os.path.dirname(os.path.realpath(__file__))+"/config.yml", 'r') as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                self.config = exc
        self.config['gui_cache_address'] = self.config['gui_cache_address'].replace('<DATE>','20191205')
        # print(self.config['gui_cache_address'])

    def check_data(self):
        return os.path.exists(self.config['logs'])

    def check_gui(self):
        return os.path.exists(self.config['gui_cache_address'])

    def data_load(self, data):
        with h5py.File(self.config['logs'], 'r') as hf:
            day = hf.get(self.day)
            for key, value in data.__dict__.items() :
                setattr(data,key,day.get(key).value)
            # pprint(data.__dict__)
            data.daily_errands = np.array([str(e)[2:-1] for e in data.daily_errands])
            data.weekly_errands = np.array([str(e)[2:-1] for e in data.weekly_errands])
            # pprint(data.__dict__)
        return data

    def data_save(self, data):
        if os.path.exists(self.config['logs']):
            with h5py.File(self.config['logs'], mode='r') as hf:
                keys = list(hf.keys())
            mode = 'w' if self.day in keys else 'a'
        else:
            mode = 'w'

        with h5py.File(self.config['logs'], mode=mode) as hf:
            day = hf.create_group(self.day)
            for key, value in data.__dict__.items():
                # saving lists of strings is tricky in h5py hence all the code below
                str_list_type = self.categorize_string_lists(value)
                if str_list_type is None:
                    day.create_dataset(key, data=value)
                elif str_list_type == 1:  #key == weekly and dailly errands
                    asciiList = [n.encode("ascii", "ignore") for n in value]
                    day.create_dataset(key, dtype='S20', data=asciiList)
                elif str_list_type == 2:  #key == todos
                    day.create_dataset(key, data=np.string_(value))
                else:
                    print('This should be a single string. Not needed until now')
                    raise NotImplementedError


    def categorize_string_lists(self, x):
        """Check if string or a list containing strings"""
        if isinstance(x, str):
            return 0
        try:
            if len(np.shape(x)) == 1:
                if isinstance(x[0], str):
                    return 1
            elif len(np.shape(x)) == 2:
                if isinstance(x[0][0], str):
                    return 2
        except (TypeError, IndexError):
            return None

    def GetHandledTypes(self):
        return (QComboBox, QLineEdit, QTextEdit, QCheckBox, QRadioButton, QSpinBox, QSlider, QListWidget, QProgressBar)

    def IsHandledType(self, widget):
        return any(isinstance(widget, t) for t in self.GetHandledTypes())

    def gui_save(self, ui : QWidget, settings : QSettings, uiName="uiwidget"):
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

            if isinstance(obj, QTextEdit):
                value = obj.toPlainText()

            if isinstance(obj, QCheckBox):
                value = obj.isChecked()

            if isinstance(obj, QRadioButton):
                value = obj.isChecked()

            if isinstance(obj, QSpinBox):
                value = obj.value()

            if isinstance(obj, QSlider):
                value = obj.value()

            if isinstance(obj, QProgressBar):
                value = obj.value()

            if isinstance(obj, QListWidget):
                settings.beginWriteArray(name)
                for i in range(obj.count()):
                    settings.setArrayIndex(i)
                    settings.setValue(namePrefix + name, obj.item(i).text())
                settings.endArray()
            elif value is not None:
                settings.setValue(namePrefix + name, value)


    def gui_restore(self, ui : QWidget, settings : QSettings, uiName="uiwidget"):
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

            if isinstance(obj, QTextEdit):
                obj.setText(value)

            if isinstance(obj, QCheckBox):
                obj.setChecked(strtobool(value))

            if isinstance(obj, QRadioButton):
                obj.setChecked(strtobool(value))

            if isinstance(obj, QSlider):
                obj.setValue(int(value))

            if isinstance(obj, QSpinBox):
                obj.setValue(int(value))

            if isinstance(obj, QProgressBar):
                obj.setValue(int(value))

            if isinstance(obj, QListWidget):
                size = settings.beginReadArray(namePrefix + name)
                for i in range(size):
                    settings.setArrayIndex(i)
                    value = settings.value(namePrefix + name)
                    if value is not None:
                        obj.addItem(value)
                settings.endArray()
