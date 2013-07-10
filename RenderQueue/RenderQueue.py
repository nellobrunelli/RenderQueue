import sys
import wx
import wx.lib.mixins.listctrl  as  listmix
import wx.lib.intctrl as intctrl
import os

# Declare GUI Constants
MENU_FILE_EXIT = 101
DRAG_SOURCE    = 201


class ListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

class FileDropTargetMXS(wx.FileDropTarget):
    """ This object implements Drop Target functionality for Files """
    def __init__(self, obj, obj2, output):
        """ Initialize the Drop Target, passing in the Object Reference to
            indicate what should receive the dropped files """
        # Initialize the wsFileDropTarget Object
        wx.FileDropTarget.__init__(self)

        # Store the Object Reference for dropped files
        self.obj = obj
        self.obj2 = obj2
        self.output = output
        self.extension = '.mxi'
        self.jpeg_dir = '\Images'

    def OnDropFiles(self, x, y, filenames):
        """ Implement File Drop """

        self.obj.SetInsertionPointEnd()
        for file in filenames:
            i = len(self.obj.GetValue())
            if i != 0:
                self.obj.Replace(0, i, file)
            else:
                self.obj.WriteText(file)
                fileName, fileExtension = os.path.splitext(file)
                fileExtension == self.extension
                file = fileName + self.extension
                self.obj2.WriteText(file)

                # create Images folder if doesnt exists and write the path in the output field
                path, file = os.path.split(file)
                path = path + self.jpeg_dir
                if not os.path.exists(path):
                    os.mkdir(path)
                self.output.WriteText(path)


class FileDropTarget(wx.FileDropTarget):
    """ This object implements Drop Target functionality for Files """
    def __init__(self, obj):
        """ Initialize the Drop Target, passing in the Object Reference to
            indicate what should receive the dropped files """
        # Initialize the wsFileDropTarget Object
        wx.FileDropTarget.__init__(self)
        # Store the Object Reference for dropped files
        self.obj = obj

    def OnDropFiles(self, x, y, filenames):
        """ Implement File Drop """

        self.obj.SetInsertionPointEnd()
        for file in filenames:

            i=len(self.obj.GetValue())
            if i != 0:
                self.obj.Replace(0, i, file)
            else:
                self.obj.WriteText(file)

class FileDropBatTarget(wx.FileDropTarget):
    """ This object implements Drop Target functionality for Files """

    def __init__(self, my_list, __totalBatchTime, timeLabel):

        """ Initialize the Drop Target, passing in the Object Reference to
            indicate what should receive the dropped files """
        # Initialize the wsFileDropTarget Object
        wx.FileDropTarget.__init__(self)
        # Store the Object Reference for dropped files

        self.my_list = my_list

        # params models, update it if needed with the right index, 0=column 0, 1=column 1, ... n=column n
        self.params = {
             0:'-mxs'
            ,1:'-mxi'
            ,2:'-o'
            ,3:'-res'
            ,4:'-time'
            ,5:'-th'
            ,6:'-s'
            ,7:'-ml'
            ,8:'-nowait'
            ,9:'-display'
            ,10:'-p'
        }

        self.__totalBatchTime = __totalBatchTime
        self.timeLabel = timeLabel

    def __findKey(self,value):
        """ Dictionary, find the key by the value"""
        for key, el in self.params.items():
            if value == el:
                return key
        return ""

    def OnDropFiles(self, x, y, filenames):
        """ Implement File Drop """

        # opening end reading the file
        file = filenames[0]
        file = open(file,"r")
        commands = file.readlines()
        file.close()

        all_batch = []

        for command in commands:

            # parse the command and build a dictionary with the list of the used params, like:
            # {0:'-mxs',1:'-mxi',2:'-o',3:'-res',4:'-time',5:'-th',6:'-s',10:'-p'}
            paramsInTheCommand = {}
            counter = 0
            for key, value in self.params.items():
                if command.find(value) != -1:
                    paramsInTheCommand[counter] = value
                    counter+=1

            # get the the index of the last parameter
            last_command = len(paramsInTheCommand) - 1

            # by the list of the used params the I can parse the command string properly
            parsed_commands = {}
            for key, value in paramsInTheCommand.items():
               if key != last_command:
                   param_begins = command.index(value)
                   param_ends = command.index(paramsInTheCommand[key+1])
                   parsed_commands[key] = command[param_begins:param_ends].strip()
               elif key == last_command:
                   param_begins = command.index(value)
                   parsed_commands[key] = command[param_begins:].strip()

            all_batch.append(parsed_commands)

        for command in all_batch:
            index = self.my_list.InsertStringItem(sys.maxint, "batch")
            for key, value in command.items():
                # retrieve the correct column from the params model
                key = self.__findKey(value.split(':')[0])
                self.my_list.SetStringItem(index, key, value)

        self.__totalBatchTime(self.my_list, self.timeLabel)


class MainWindow(wx.Frame):
    """ This window displays the GUI Widgets. """
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,-4, title, size = (600,720), style=wx.TAB_TRAVERSAL|wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.SetBackgroundColour(wx.LIGHT_GREY)
            
        wx.StaticText(self, -1, "MXI:", (10, 50))
        self.MXI = wx.TextCtrl(self, -1, "", pos=(10,70), size=(410,-1))
        dt4 = FileDropTarget(self.MXI)
        self.MXI.SetDropTarget(dt4)

        wx.StaticText(self, -1, "Output:", (10, 100))
        self.output = wx.TextCtrl(self, -1, "", pos=(10,120), size=(410,-1))
        dt5 = FileDropTarget(self.output)
        self.output.SetDropTarget(dt5)

        wx.StaticText(self, -1, "MXS:", (10, 1))
        self.MXS = wx.TextCtrl(self, -1, "", pos=(10,20), size=(410,-1))
        dt3 = FileDropTargetMXS(self.MXS, self.MXI, self.output)
        self.MXS.SetDropTarget(dt3)

        btnClear= wx.Button(self, 2, "Clear form", pos=(500,20))
        self.Bind(wx.EVT_BUTTON, self.Clear, btnClear)

        btnAdd= wx.Button(self, 5, "Add to batch", pos=(10,170))
        self.Bind(wx.EVT_BUTTON, self.AddToBatch, btnAdd)

        btnRemove= wx.Button(self, 6, "Remove from batch", pos=(120,170))
        self.Bind(wx.EVT_BUTTON, self.RemoveFromBatch, btnRemove)

        wx.StaticText(self, -1, "X:", (90, 200))
        wx.StaticText(self, -1, "Y:", (160, 200))
        wx.StaticText(self, -1, "Resolution:", (10, 220))
        self.res_X= intctrl.IntCtrl(self, -1, 0, size=(50, -1), pos=(90, 220))
        self.res_Y= intctrl.IntCtrl(self, -1, 0, size=(50, -1), pos=(160, 220))
        wx.StaticText(self, -1, "Time:", (10, 250))
        self.time= intctrl.IntCtrl(self, -1, 0, size=(50, -1), pos=(90, 250))
        wx.StaticText(self, -1, "Threads:", (10, 270))
        self.threads= intctrl.IntCtrl(self, -1, 0, size=(50, -1), pos=(90, 270))
        wx.StaticText(self, -1, "Sampling:", (10, 310))
        self.samplinglevel= intctrl.IntCtrl(self, -1, 0, size=(50, -1), pos=(90, 310))

        btnAdd= wx.Button(self, 1, "Apply to whole batch", pos=(10,370))
        self.Bind(wx.EVT_BUTTON, self.AddToWholeBatch, btnAdd)
                
        self.multilight = wx.CheckBox(self, -1, "Multilight", pos=(300,220))
        self.nowait = wx.CheckBox(self, -1, "No wait", pos=(300,240))
        self.display = wx.CheckBox(self, -1, "Display", pos=(300,260))
        self.lowpriority = wx.CheckBox(self, -1, "Low priority", pos=(300,280))
            
        self.multilight.SetValue(True)
        self.nowait.SetValue(True)
        self.display.SetValue(True)
        self.lowpriority.SetValue(True)

        self.timeLabel = wx.StaticText(self, -1, "Total Time: 0:0", (10, 650))
                
        self.my_list = ListCtrl(self, 5, pos=(10,430),size=(570,200),style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_SORT_ASCENDING)
        self.PopulateList()
        dt7 = FileDropBatTarget(self.my_list, self.__totalBatchTime, self.timeLabel)
        self.my_list.SetDropTarget(dt7)

        btnRun= wx.Button(self, 3, "Run Batch", pos=(500,650))
        self.Bind(wx.EVT_BUTTON, self.Run, btnRun)

        btnSave= wx.Button(self, 4, "Save Batch", pos=(400,650))
        self.Bind(wx.EVT_BUTTON, self.Save, btnSave)

        btnSave= wx.Button(self, 4, "Save Batch", pos=(400,650))
        self.Bind(wx.EVT_BUTTON, self.Save, btnSave)

        self.threads.SetValue(8)
        self.samplinglevel.SetValue(25)

        # Display the Window
        self.Show(True)

    def __totalBatchTime(self, my_list, timeLabel):
        """ Compute the total time of the batch jobs in the queue"""

        n = my_list.GetItemCount()
        total_time = 0
        for i in range(0,n):
            item = self.my_list.GetItem(i, 4)
            value = item.GetText()
            time = int(value.split(':')[1])
            total_time+= time

        hours, minutes = divmod(total_time, 60)
        timeLabel.SetLabel("Total Time " + str(hours) + ':' + str(minutes))

        return True

        
    def PopulateList(self):
        
        #self.my_list.InsertColumn(0, "Thumbnails")
        self.my_list.InsertColumn(1, "MXS")
        self.my_list.InsertColumn(2, "MXI")
        self.my_list.InsertColumn(3, "Output file")
        self.my_list.InsertColumn(4, "Resolution")
        self.my_list.InsertColumn(5, "Time")
        self.my_list.InsertColumn(6, "Threads")
        self.my_list.InsertColumn(7, "Sampling level")
        self.my_list.InsertColumn(8, "Multilight")
        self.my_list.InsertColumn(9,"No wait")
        self.my_list.InsertColumn(10,"Display")
        self.my_list.InsertColumn(11,"Low priority")
        
        self.currentItem = 0
    
    def OnDragInit(self, event):
        """ Begin a Drag Operation """
        # Create a Text Data Object, which holds the text that is to be dragged
        tdo = wx.PyTextDataObject(self.text.GetStringSelection())
        # Create a Drop Source Object, which enables the Drag operation
        tds = wx.DropSource(self.text)
        # Associate the Data to be dragged with the Drop Source Object
        tds.SetData(tdo)
        # Intiate the Drag Operation
        tds.DoDragDrop(True)
    
    def AddToBatch(self, event):
        """sotre the settings in the list object"""


        if self.multilight.GetValue() == True:
            multilight= "-ml"
        else:
            multilight= ""
        if self.nowait.GetValue() == True:
            nowait= "-nowait"
        else:
            nowait= ""
        if self.display.GetValue() == True:
            display="-display"
        else:
            display= ""
        if self.lowpriority.GetValue() == True:
            lowpriority="-p:low"
        else:
            lowpriority= ""
        
        index= self.my_list.InsertStringItem(sys.maxint, "-mxs:\""+self.MXS.GetValue()+"\"")
        self.my_list.SetStringItem(index, 1, "-mxi:\""+self.MXI.GetValue()+"\"")
        self.my_list.SetStringItem(index, 2, "-o:\""+self.output.GetValue()+"\"")
        self.my_list.SetStringItem(index, 3, "-res:"+str(self.res_X.GetValue())+'x'+str(self.res_Y.GetValue()))
        self.my_list.SetStringItem(index, 4, "-time:"+str(self.time.GetValue()))
        self.my_list.SetStringItem(index, 5, "-th:"+str(self.threads.GetValue()))
        self.my_list.SetStringItem(index, 6, "-s:"+str(self.samplinglevel.GetValue()))
        self.my_list.SetStringItem(index, 7, multilight)
        self.my_list.SetStringItem(index, 8, nowait)
        self.my_list.SetStringItem(index, 9, display)
        self.my_list.SetStringItem(index, 10, lowpriority)

        self.__totalBatchTime(self.my_list, self.timeLabel)

    def AddToWholeBatch(self, event):
        """ Apply to whole - file  """

        if self.multilight.GetValue() == True:
            multilight= "-ml"
        else:
            multilight= ""
        if self.nowait.GetValue() == True:
            nowait= "-nowait"
        else:
            nowait= ""
        if self.display.GetValue() == True:
            display="-display"
        else:
            display= ""
        if self.lowpriority.GetValue() == True:
            lowpriority="-p:low"
        else:
            lowpriority= ""

        n = self.my_list.GetItemCount()

        for i in range(0,n):
            self.my_list.SetStringItem(i, 3, "-res:"+str(self.res_X.GetValue())+'x'+str(self.res_Y.GetValue()))
            self.my_list.SetStringItem(i, 4, "-time:"+str(self.time.GetValue()))
            self.my_list.SetStringItem(i, 5, "-th:"+str(self.threads.GetValue()))
            self.my_list.SetStringItem(i, 6, "-s:"+str(self.samplinglevel.GetValue()))
            self.my_list.SetStringItem(i, 5, "-th:"+str(self.threads.GetValue()))
            self.my_list.SetStringItem(i, 6, "-s:"+str(self.samplinglevel.GetValue()))
            self.my_list.SetStringItem(i, 7, multilight)
            self.my_list.SetStringItem(i, 8, nowait)
            self.my_list.SetStringItem(i, 9, display)
            self.my_list.SetStringItem(i, 10, lowpriority)

        self.__totalBatchTime(self.my_list, self.timeLabel)

    def RemoveFromBatch(self, event):
    
        item = self.my_list.GetFirstSelected()
        self.my_list.DeleteItem(item)
    
    def Clear(self, evt):
        
        i=len(self.MXI.GetValue())
        if i != 0:
            self.MXI.Replace(0, i, '')
        else:
            self.MXI.WriteText('')
        
        i=len(self.MXS.GetValue())
        if i != 0:
            self.MXS.Replace(0, i, '')
        else:
            self.MXS.WriteText('')
        
        i=len(self.output.GetValue())
        if i != 0:
            self.output.Replace(0, i, '')
        else:
            self.output.WriteText('')
                    
        self.res_X.SetValue(0)
        self.res_Y.SetValue(0)
        self.time.SetValue(0)
        self.threads.SetValue(0)
        self.samplinglevel.SetValue(0)
        
        self.multilight.SetValue(True)
        self.nowait.SetValue(True)
        self.display.SetValue(True)
        self.lowpriority.SetValue(True)
    
    def Run(self, evt):
        """run the batch"""
        s= self.CreateBatch()
        path= 'render.bat'
        f= open(path, 'w')
        f.write(s)
        f.close()
        os.system(path)
        
    def Save(self, evt):
        """prompt the user for a file and write the batch"""
        s= self.CreateBatch()
        
        dlg = wx.FileDialog(self, message="Save file as ...", defaultDir=os.getcwd(), defaultFile="", wildcard=".bat", style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            f= open(path, 'w')
            f.write(s)
            f.close()
    
    def getColumnText(self, index, col):
        item = self.my_list.GetItem(index, col)
        return item.GetText()

    def CreateBatch(self):
        """write the batch strings"""
        n= self.my_list.GetItemCount()
        s=''
        for i in range(0,n):
            self.currentItem
            s+='maxwell '
            s+=self.getColumnText(i, 0)+' '
            s+=self.getColumnText(i, 1)+' '
            s+=self.getColumnText(i, 2)+' '
            s+=self.getColumnText(i, 3)+' '
            s+=self.getColumnText(i, 4)+' '
            s+=self.getColumnText(i, 5)+' '
            s+=self.getColumnText(i, 6)+' '
            s+=self.getColumnText(i, 7)+' '
            s+=self.getColumnText(i, 8)+' '
            s+=self.getColumnText(i, 9)+' '
            s+=self.getColumnText(i, 10)+' '
            s+='\n'
        
        return s
            
class MyApp(wx.App):
    """ Define the Render Queue Application """
    def OnInit(self):
        """ Initialize the Application """
        # Declare the Main Application Window
        frame = MainWindow(None, -1, "Render Queue 2.1")
        self.SetTopWindow(frame)
        return True

# Declare the Application and start the Main Loop
app = MyApp(0)
app.MainLoop()
