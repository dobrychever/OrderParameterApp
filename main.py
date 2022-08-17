import wx
import numpy as np
import sys
import os
import subprocess


'''Global constants'''


BUFFER_FILENAME_FOR_CONFIG_SAVING = 'C:/Users/Mikhail/PycharmProjects/pythonProject/bufferconfig.npy'


'''Graphical Interface'''


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1280, 720))
        self.SetBackgroundColour(wx.WHITE)
        self.CreateStatusBar()

        '''Creating menu'''

        filemenu = wx.Menu()
        filemenu.Append(wx.ID_ABOUT, "About", "Information about this Program")
        filemenu.AppendSeparator()
        filemenu.Append(wx.ID_EXIT, "Exit", "Terminate the Program")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "File")

        self.SetMenuBar(menuBar)

        '''Creating bots configuration object'''

        config = Configuration()

        '''Main panels'''

        mainPanel = wx.Panel(self)

        parameterPanel = ParameterPanel(mainPanel, config)
        botsPanel = BotsPanel(mainPanel, config)
        picturePanel = PicturePanel(mainPanel)

        sizer = wx.GridBagSizer()

        sizer.Add(parameterPanel, (0, 0), (1, 1), flag=wx.EXPAND)
        sizer.Add(botsPanel, (1, 0), (1, 1), flag=wx.EXPAND)
        sizer.Add(picturePanel, (0, 1), (2, 2), flag=wx.EXPAND)

        sizer.AddGrowableRow(0)
        sizer.AddGrowableRow(1)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableCol(2)


        mainPanel.SetSizerAndFit(sizer)

        self.Show(True)


class BotsPanel(wx.Panel):
    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.SUNKEN_BORDER)

        self.config = config

        self.add_button = wx.Button(self, wx.ID_ANY, "Add")
        self.load_button = wx.Button(self, wx.ID_ANY, "Load")
        self.save_button = wx.Button(self, wx.ID_ANY, "Save")
        self.clear_button = wx.Button(self, wx.ID_ANY, "Clear")

        self.Bind(wx.EVT_BUTTON, self.onAdd, self.add_button)
        self.Bind(wx.EVT_BUTTON, self.onLoad, self.load_button)
        self.Bind(wx.EVT_BUTTON, self.onSave, self.save_button)
        self.Bind(wx.EVT_BUTTON, self.onClear, self.clear_button)

        self.bots_number_text = wx.StaticText(self, wx.ID_ANY, '')
        self._updateBotsNumberText()

        self.bots_list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
        self.bots_list.InsertColumn(0, '№')
        self.bots_list.InsertColumn(1, 'Identifier')
        self.bots_list.InsertColumn(2, 'Angle')
        self.bots_list.InsertColumn(3, 'Coordinate')
        self._updateBotsList()

        sizer = wx.GridBagSizer()

        sizer.Add(self.add_button, (0,0), (1,1), flag=wx.EXPAND)
        sizer.Add(self.load_button, (0,1), (1,1), flag=wx.EXPAND)
        sizer.Add(self.save_button, (0,2), (1,1), flag=wx.EXPAND)
        sizer.Add(self.clear_button, (0,3), (1,1), flag=wx.EXPAND)
        sizer.Add(self.bots_number_text, (1, 0), (1,4), flag=wx.EXPAND)
        sizer.Add(self.bots_list, (2,0), (1,4), flag=wx.EXPAND)

        sizer.AddGrowableRow(0)
        sizer.AddGrowableRow(1)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableCol(2)
        sizer.AddGrowableCol(3)

        self.SetSizerAndFit(sizer)

    def onAdd(self, event):
        self.config.AddBot(1, 2, (3,4))
        self._updateBotsNumberText()
        self._updateBotsList()

    def onLoad(self, event):
        with wx.FileDialog(self, "Open .npy file", wildcard='*.npy', style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as filedialog:
            if filedialog.ShowModal() == wx.ID_CANCEL:
                return
            filename = filedialog.GetPath()
            try:
                self.config.LoadConfiguration(filename)
                self._updateBotsList()
                self._updateBotsNumberText()
            except IOError:
                wx.LogError(f'Cannot open file {filename}')

    def onSave(self, event):
        with wx.FileDialog(self, "Save .npy file", wildcard="*.npy", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as filedialog:
            if filedialog.ShowModal() == wx.ID_CANCEL:
                return
            filename = filedialog.GetPath()
            try:
                self.config.SaveConfiguration(filename)
            except IOError:
                wx.LogError(f'Cannot save into {filename}')

    def onClear(self, event):
        self.config.ClearConfiguration()
        self._updateBotsNumberText()
        self._updateBotsList()

    def _updateBotsNumberText(self):
        self.bots_number_text.SetLabel(f'Bots number: {self.config.GetBotsNumber()}')

    def _updateBotsList(self):
        self.bots_list.DeleteAllItems()
        bots_number = self.config.GetBotsNumber()
        bots_positions = self.config.GetBotsPositions()
        for i in range(bots_number):
            self.bots_list.InsertItem(i, str(i + 1))
            self.bots_list.SetItem(i, 1, str(bots_positions[i][0]))
            self.bots_list.SetItem(i, 2, str(bots_positions[i][1]))
            self.bots_list.SetItem(i, 3, str(bots_positions[i][2]))


class ParameterPanel(wx.Panel):
    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.SUNKEN_BORDER)

        self.config = config
        self.parameter_name = ''
        self.parameter_file = ''
        self.parameter_value = None

        self.header_text = wx.StaticText(self, wx.ID_ANY, '')
        self._updateHeaderText()

        self.parameter_name_text_ctrl = wx.TextCtrl(self, wx.ID_ANY)

        self.load_button = wx.Button(self, wx.ID_ANY, 'Load')
        self.calculate_button = wx.Button(self, wx.ID_ANY, 'Calculate')

        self.Bind(wx.EVT_BUTTON, self.onLoad, self.load_button)
        self.Bind(wx.EVT_BUTTON, self.onCalculate, self.calculate_button)

        self.parameters_list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
        self.parameters_list.InsertColumn(0, '№')
        self.parameters_list.InsertColumn(1, 'Parameter name')
        self.parameters_list.InsertColumn(2, 'Value')

        sizer = wx.GridBagSizer()

        sizer.Add(self.parameter_name_text_ctrl, (0,0), (1,1), flag=wx.EXPAND)
        sizer.Add(self.load_button, (0,1), (1,1), flag=wx.EXPAND)
        sizer.Add(self.calculate_button, (0,2), (1,1), flag=wx.EXPAND)
        sizer.Add(self.header_text, (1,0), (1,3), flag=wx.EXPAND)
        sizer.Add(self.parameters_list, (2,0), (1,3), flag=wx.EXPAND)

        sizer.AddGrowableRow(0)
        sizer.AddGrowableRow(1)
        sizer.AddGrowableRow(2)
        sizer.AddGrowableCol(0)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableCol(2)

        self.SetSizerAndFit(sizer)

    def onLoad(self, event):
        self.parameter_name = self.parameter_name_text_ctrl.GetLineText(0)
        self.parameter_name_text_ctrl.Clear()
        self._updateHeaderText()
        with wx.FileDialog(self, 'Open .py file', wildcard='*.py', style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as filedialog:
            if filedialog.ShowModal() == wx.ID_CANCEL:
                return
            filename = filedialog.GetPath()
            self.parameter_file = filename
        print(self.parameter_file)

    def onCalculate(self, event):
        self.config.SaveConfiguration(BUFFER_FILENAME_FOR_CONFIG_SAVING)
        args = [sys.executable, self.parameter_file, BUFFER_FILENAME_FOR_CONFIG_SAVING]
        complited_process = subprocess.run(args, capture_output=True, text=True, check=True)
        self.parameter_value = complited_process.stdout
        self._updateHeaderText()

    def _updateHeaderText(self):
        self.header_text.SetLabel(f'Parameter: {self.parameter_name}, value: {self.parameter_value}')

class PicturePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.SUNKEN_BORDER)

        self.dc = wx.ClientDC(self)
        self.gc = wx.GraphicsContext.Create(self.dc)

        self.gc.SetPen(wx.Pen("navy", 1))
        self.gc.SetBrush(wx.Brush("pink"))

        path = self.gc.CreatePath()
        path.AddCircle(50, 50, 50)
        self.gc.DrawPath(path)


        self.center = (self.Size[0] // 2, self.Size[1] // 2)
        self.Bind(wx.EVT_MOTION, self.onMouseMove, self)
        self.Bind(wx.EVT_SIZE, self.onResize, self)

    def onMouseMove(self, event):
        pos = event.GetLogicalPosition(self.dc)
        print(pos)

    def onResize(self, event):
        self.center = (event.GetSize()[0] // 2, event.GetSize()[1] // 2)

    def drawConfig(self):
        pass


'''Bots configuration part'''


class Configuration:
    def __init__(self):
        self.bots_positions = []

    def GetBotsPositions(self):
        return self.bots_positions

    def GetBotsNumber(self):
        return len(self.bots_positions)

    def LoadConfiguration(self, filename):
        self.bots_positions = np.load(filename, allow_pickle=True).tolist()

    def SaveConfiguration(self, filename):
        np.save(filename, np.array(self.bots_positions, dtype=object), allow_pickle=True)

    def AddBot(self, identifier, angle, center):
        self.bots_positions.append([identifier, angle, center])

    def ClearConfiguration(self):
        self.bots_positions = []


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainWindow(None, "First program")
    app.MainLoop()

