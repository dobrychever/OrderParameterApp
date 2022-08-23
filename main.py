import wx
import numpy as np
import sys
import os
import subprocess


'''Global constants'''
DEG2RAD = np.pi / 180

BUFFER_FILENAME_FOR_CONFIG_SAVING = 'C:/Users/Mikhail/PycharmProjects/pythonProject/bufferconfig.npy'

DEFAULT_MAIN_WINDOW_SIZE = (1280, 720)

DEFAULT_PARAMETER_PANEL_SIZE = (320, 240)

DEFAULT_BOTS_PANEL_SIZE = (320, 480)
DEFAULT_BOTS_NUMBER_TEXT_SIZE = (320, 20)
DEFAULT_BUTTON_SIZE = (106, 20)
DEFAULT_ADD_BUTTON_SIZE = (80, 20)
DEFAULT_BOTS_LIST_SIZE = (320, 420)
DEFAULT_BOTS_LIST_NUMBER_COLUMN_WIDTH = 80
DEFAULT_BOTS_LIST_ID_COLUMN_WIDTH = 80
DEFAULT_BOTS_LIST_ANGLE_COLUMN_WIDTH = 80
DEFAULT_BOTS_LIST_COORDINATE_COLUMN_WIDTH = 80


DEFAULT_PICTURE_PANEL_SIZE = (960, 720)



'''Graphical Interface'''


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=DEFAULT_MAIN_WINDOW_SIZE, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
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
        picturePanel = PicturePanel(mainPanel, config)

        botsPanel.setPicturePanel(picturePanel)
        picturePanel.setBotsPanel(botsPanel)

        hboxsizer = wx.BoxSizer(wx.HORIZONTAL)
        vboxsizer = wx.BoxSizer(wx.VERTICAL)

        vboxsizer.Add(parameterPanel, proportion=0, flag=wx.EXPAND)
        vboxsizer.Add(botsPanel, proportion=0, flag=wx.EXPAND)

        hboxsizer.Add(vboxsizer, proportion=0, flag=wx.EXPAND)
        hboxsizer.Add(picturePanel, proportion=0, flag=wx.EXPAND)

        mainPanel.SetSizerAndFit(hboxsizer)

        self.Show(True)


class BotsPanel(wx.Panel):
    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY, size=DEFAULT_BOTS_PANEL_SIZE, style=wx.SUNKEN_BORDER)

        self.config = config
        self.picture_panel = None

        self.bots_number_text = wx.StaticText(self, wx.ID_ANY, '', size=DEFAULT_BOTS_NUMBER_TEXT_SIZE, style=wx.SIMPLE_BORDER)
        self._updateBotsNumberText()

        self.load_button = wx.Button(self, wx.ID_ANY, "Load", size=DEFAULT_BUTTON_SIZE)
        self.save_button = wx.Button(self, wx.ID_ANY, "Save", size=DEFAULT_BUTTON_SIZE)
        self.clear_button = wx.Button(self, wx.ID_ANY, "Clear", size=DEFAULT_BUTTON_SIZE)

        self.Bind(wx.EVT_BUTTON, self.onLoad, self.load_button)
        self.Bind(wx.EVT_BUTTON, self.onSave, self.save_button)
        self.Bind(wx.EVT_BUTTON, self.onClear, self.clear_button)


        self.add_edit_button = wx.Button(self, wx.ID_ANY, "Add", size=DEFAULT_ADD_BUTTON_SIZE)
        self.new_bot_id_text_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", size = (DEFAULT_BOTS_LIST_ID_COLUMN_WIDTH, 20))
        self.new_bot_angle_text_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", size = (DEFAULT_BOTS_LIST_ANGLE_COLUMN_WIDTH, 20))
        self.new_bot_coordinate_x_text_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", size = (DEFAULT_BOTS_LIST_ID_COLUMN_WIDTH // 2, 20))
        self.new_bot_coordinate_y_text_ctrl = wx.TextCtrl(self, wx.ID_ANY, "", size = (DEFAULT_BOTS_LIST_ID_COLUMN_WIDTH // 2, 20))

        self.Bind(wx.EVT_BUTTON, self.onAdd, self.add_edit_button)

        self.bots_list = wx.ListCtrl(self, wx.ID_ANY, size=DEFAULT_BOTS_LIST_SIZE, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.bots_list.InsertColumn(0, '№', width=DEFAULT_BOTS_LIST_NUMBER_COLUMN_WIDTH)
        self.bots_list.InsertColumn(1, 'Identifier', width=DEFAULT_BOTS_LIST_ID_COLUMN_WIDTH)
        self.bots_list.InsertColumn(2, 'Angle', width=DEFAULT_BOTS_LIST_ANGLE_COLUMN_WIDTH)
        self.bots_list.InsertColumn(3, 'Coordinate', width=DEFAULT_BOTS_LIST_COORDINATE_COLUMN_WIDTH)
        self._updateBotsList()

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelect, self.bots_list)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated, self.bots_list)

        vboxsizer = wx.BoxSizer(wx.VERTICAL)
        vboxsizer.Add(self.bots_number_text, proportion=0, flag=wx.EXPAND)

        hboxsizer1 = wx.BoxSizer(wx.HORIZONTAL)
        hboxsizer1.Add(self.load_button, proportion=0, flag=wx.EXPAND)
        hboxsizer1.Add(self.save_button, proportion=0, flag=wx.EXPAND)
        hboxsizer1.Add(self.clear_button, proportion=0, flag=wx.EXPAND)
        vboxsizer.Add(hboxsizer1, proportion=0, flag=wx.EXPAND)

        hboxsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hboxsizer2.Add(self.add_edit_button, proportion=0, flag=wx.EXPAND)
        hboxsizer2.Add(self.new_bot_id_text_ctrl, proportion=0, flag=wx.EXPAND)
        hboxsizer2.Add(self.new_bot_angle_text_ctrl, proportion=0, flag=wx.EXPAND)
        hboxsizer2.Add(self.new_bot_coordinate_x_text_ctrl, proportion=0, flag=wx.EXPAND)
        hboxsizer2.Add(self.new_bot_coordinate_y_text_ctrl, proportion=0, flag=wx.EXPAND)
        vboxsizer.Add(hboxsizer2, proportion=0, flag=wx.EXPAND)

        vboxsizer.Add(self.bots_list, proportion=0, flag=wx.EXPAND)

        self.SetSizerAndFit(vboxsizer)

    def setPicturePanel(self, picture_panel):
        self.picture_panel = picture_panel

    def onAdd(self, event):
        id = self.new_bot_id_text_ctrl.GetLineText(0)
        angle = self.new_bot_angle_text_ctrl.GetLineText(0)
        x = self.new_bot_coordinate_x_text_ctrl.GetLineText(0)
        y = self.new_bot_coordinate_y_text_ctrl.GetLineText(0)

        if '' not in [id, angle, x, y]:
            self.config.AddBot(int(id), float(angle), (float(x), float(y)))
            self._updateBotsNumberText()
            self._updateBotsList()
            self.picture_panel.callConfigRedraw()

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

    def onItemSelect(self, event):
        print(event.Index)

    def onItemActivated(self, event):
        print(str(event.Index) + ' a')

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
    def __init__(self, parent, config=[], scale=1):
        wx.Panel.__init__(self, parent, wx.ID_ANY, size=DEFAULT_PARAMETER_PANEL_SIZE, style=wx.SUNKEN_BORDER)

        self.config = config
        self.scale = scale

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
    def __init__(self, parent, config):
        wx.Panel.__init__(self, parent, wx.ID_ANY, size=DEFAULT_PICTURE_PANEL_SIZE, style=wx.SUNKEN_BORDER)

        self.config = config
        self.bots_panel = None
        self.drawTypeFlag = 'config'

        self.Bind(wx.EVT_PAINT, self.onPaint, self)

        self.center = (self.Size[0] // 2, self.Size[1] // 2)
        self.Bind(wx.EVT_MOTION, self.onMouseMove, self)
        self.Bind(wx.EVT_SIZE, self.onResize, self)
        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftClick, self)

        self.mouse_pos = (0, 0)

    def setBotsPanel(self, bots_panel):
        self.bots_panel = bots_panel

    def callConfigRedraw(self):
        self.drawTypeFlag = 'config'
        self.Refresh(eraseBackground=True)

    def onPaint(self, event):
        self.dc = wx.PaintDC(self)
        self.gc = wx.GraphicsContext.Create(self.dc)
        self.gc.SetPen(wx.Pen("navy", 1))
        self.gc.SetBrush(wx.Brush("pink"))

        if self.drawTypeFlag == 'config':
            path = self.gc.CreatePath()
            self._addConfigToPath(path, 10)
            self.gc.StrokePath(path)

    def onMouseMove(self, event):
        self.Refresh(eraseBackground=True)

    def onResize(self, event):
        self.center = (event.GetSize()[0] // 2, event.GetSize()[1] // 2)

    def onLeftClick(self, event):
        pass

    def _addConfigToPath(self, graphics_path, scale):
        for bot in self.config.GetBotsPositions():
            points = self._getBotPoints(bot)
            self._addBotToPath(graphics_path, points, scale)


    def _addBotToPath(self, graphics_path, bot_points, scale):
        nose_point = self._sumPoints((0,0), bot_points[0], scale)
        right_point = self._sumPoints((0,0), bot_points[1][0], scale)
        left_point = self._sumPoints((0,0), bot_points[1][1], scale)
        center_point = self._sumPoints((0,0), bot_points[2], scale)
        radius = bot_points[3] * scale

        right_rel = self._sumPoints(right_point, center_point, -1)
        left_rel = self._sumPoints(left_point, center_point, -1)
        # graphics_path.CloseSubpath()
        graphics_path.MoveToPoint(left_point[0], left_point[1])
        graphics_path.AddLineToPoint(nose_point[0], nose_point[1])
        graphics_path.AddLineToPoint(right_point[0], right_point[1])
        # graphics_path.MoveToPoint(left_point[0], left_point[1])
        # graphics_path.CloseSubpath()
        center_point = wx.Point2D(center_point[0], center_point[1])
        graphics_path.AddCircle(center_point[0], center_point[1], radius)
        # graphics_path.CloseSubpath()


    def _getBotPoints(self, bot):
        ipraw = intersect_points_raw = (
            (-0.1635, 2.25),
            (-0.1635, -2.25)
        )
        l_1 = 6.5
        r = 2.5
        angle = bot[1]
        pos = bot[2]
        nose_pos = (pos[0] + l_1 * np.cos(angle * DEG2RAD), pos[1] + l_1 * np.sin(angle * DEG2RAD))
        nose_pos_rel = self._sumPoints(nose_pos, pos, -1)
        iprot = (
            self._rotatePoint(ipraw[0], angle),
            self._rotatePoint(ipraw[1], angle)
        )
        iprot_pos = (
            self._sumPoints(iprot[0], pos, 1),
            self._sumPoints(iprot[1], pos, 1),
        )
        return nose_pos, iprot_pos, pos, r

    def _rotatePoint(self, point, angle_deg):
        return (
            point[0] * np.cos(angle_deg*DEG2RAD) - point[1] * np.sin(angle_deg*DEG2RAD),
            point[0] * np.sin(angle_deg*DEG2RAD) + point[1] * np.cos(angle_deg*DEG2RAD),
        )

    def _sumPoints(self, p1, p2, scale):
        return (p1[0] + scale * p2[0],
                p1[1] + scale * p2[1])




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

