# coding:UTF-8
import datetime
import sys
import wx
import time
import os
import threading
import random
########################################################################
# set the file filter
wildcard1 = "Txt source (*.txt)|*.txt|"\
            "All files (*.*)|*.*|" \
            "Python source (*.py; *.pyc)|*.py;*.pyc"
wildcard2 = "Txt source (*.txt)|*.txt|"\
    "Python source (*.py; *.pyc)|*.py;*.pyc|" \
            "All files (*.*)|*.*"
########################################################################
########################################################################
# 获取脚本路径
# 判断为脚本文件还是py2exe编译后的文件，
# 如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
curFilePath = sys.path[0] if os.path.isdir(
    sys.path[0]) else os.path.dirname(sys.path[0])  # 全局变量，当前文件路径
########################################################################
########################################################################
# 盲点检测图片集
MDataPicPath = [
    ['Mpic/np_0.jpg', 'Mpic/w-np_0.jpg'],
    ['Mpic/np_1.jpg', 'Mpic/w-np_1.jpg'],
    ['Mpic/np_2.jpg', 'Mpic/w-np_2.jpg'],
    ['Mpic/np.jpg', 'Mpic/w-np.jpg']
]
########################################################################
# 用户预测图片集
PDataPicPath = [
    ['Upic/up1/up_0_10.jpg', 'Upic/up1/up_0_20.jpg', 'Upic/up1/up_0_30.jpg',
        'Upic/up1/up_0_60.jpg', 'Upic/up1/up_0.jpg'],
    ['Upic/up2/up_1_10.jpg', 'Upic/up2/up_1_20.jpg', 'Upic/up2/up_1_30.jpg',
        'Upic/up2/up_1_60.jpg', 'Upic/up2/up_1.jpg'],
    ['Upic/up3/up_2_10.jpg', 'Upic/up3/up_2_20.jpg', 'Upic/up3/up_2_30.jpg',
        'Upic/up3/up_2_60.jpg', 'Upic/up3/up_2.jpg'],
]
########################################################################
########################################################################
# 物化视图视图文件名
viewfilename = "view.txt"
########################################################################


class Computing(threading.Thread):
    """
    This computing bigdata thread.
    """

    def __init__(self, filePath, colNum, flag, window):
        threading.Thread.__init__(self)
        self.filePath = filePath
        self.window = window
        self.colNum = colNum
        self.flag = flag  # 此flag标识的大数据计算方法，为0则使用常规方法，为1则使用物化视图方法
        self.messageDelay = 0.1 + 2.0 * random.random()
        # 初始化实例时即可开始run
        self.start()

    def run(self):
        OutGrids = ''  # 用于统计数据，将计算所用时间综合显示\
        # ISOTIMEFORMAT = '%Y-%m-%d %X'#设定时间显示格式
        # 给出当前处理相关信息， 标记为1则清除panel3的显示
        OutGrids = u"当前处理文件:" + self.filePath + "\n" + u"当前处理数据行数:" + \
            str(self.colNum) + "\n" + u"当前数据计算：" + \
            self.window.ComputingSet + "\n"
        wx.CallAfter(self.window.GridsMsg, OutGrids, 1)
        try:
            if(self.flag == 0):
                # 数据计算开始，标记为2则标识数据计算的开始
                OutGrids = u"常规数据计算开始时间:"
                wx.CallAfter(self.window.GridsMsg, OutGrids, 2)
                msg = u"开始常规数据计算!"
                wx.CallAfter(self.window.LogMessage, msg)
                # 打开传入子线程的文件，并读取文件的数据
                fout = open(self.filePath)
                contents = fout.readlines()[:self.colNum]
                # temp存入计算后的结果，i则为了显示计算过程设置的千位数
                temp = 0
                i = 0
                for content in contents:
                    if (i % 1000 == 0):
                        msg = u"正在计算第" + str(i / 1000 + 1) + u"千行数据！"
                        wx.CallAfter(self.window.LogMessage, msg)
                    data = content.rsplit(",")
                    diaoxian = (float(data[1]) - float(data[2])) / \
                        (float(data[3]) - float(data[4].rstrip("\n")))
                    temp += diaoxian
                    i += 1
                    # count = count + 1
                    # keepGoing = dialog.Update(count)
                temp /= self.colNum
                # 每次常规计算后都将计算结果存入默认视图文件，待物化视图方法的调用
                fout = open(viewfilename, 'w+')
                fout.write(str(self.colNum) + " " + str(temp))
                fout.close()
                # 结束计算后，统计信息并输出到主进程
                msg = u"数据计算结束!"
                wx.CallAfter(self.window.LogMessage, msg)
                OutGrids = u"常规数据计算结束时间:"
                wx.CallAfter(self.window.GridsMsg, OutGrids, 3)
                OutGrids = u"常规数据计算所用时间:"
                wx.CallAfter(self.window.GridsMsg, OutGrids, 4)
                OutGrids = u"计算结果为:" + str(temp)
                wx.CallAfter(self.window.GridsMsg, OutGrids)
            elif(self.flag == 1):
                OutGrids = u"物化视图计算开始时间:"
                wx.CallAfter(self.window.GridsMsg, OutGrids, 2)
                msg = u"开始使用物化视图方法进行数据计算!"
                wx.CallAfter(self.window.LogMessage, msg)
                ffout = open(viewfilename, 'r+')  # 默认视图文件是view.txt
                view = ffout.readline().split(' ')
                if(self.colNum >= int(view[0])):  # 判断是否当前打开的视图信息是可用视图
                    msg = u"找到可用视图!"
                    wx.CallAfter(self.window.GridsMsg, msg)
                    wx.CallAfter(self.window.LogMessage, msg)
                    # 打开传入子线程的文件，并读取文件的数据
                    fout = open(self.filePath)
                    contents = fout.readlines()[:self.colNum]
                    # temp存入计算后的结果，i则为了显示计算过程设置的千位数，物化视图的i从开始计算的数据行数开始
                    temp = 0
                    otemp = float(view[1])  # 视图信息中第一列为已经保存的计算数据行数
                    onum = int(view[0])  # 视图信息中第二列为已经保存的对应计算数据行数的计算结果
                    i = onum
                    # 计算过程，以掉线率计算为模板
                    for content in contents[onum:]:
                        if (i % 1000 == 0):
                            msg = u"正在计算第" + str(i / 1000 + 1) + u"千行数据！"
                            wx.CallAfter(self.window.LogMessage, msg)
                        data = content.rsplit(" ")
                        diaoxian = (float(data[1]) - float(data[2])) / \
                            (float(data[3]) - float(data[4].rstrip("\n")))
                        temp += diaoxian
                        i += 1
                    temp += onum * otemp
                    temp /= self.colNum
                    # 物化视图计算之后的信息也将更新默认视图文件
                    fout = open(viewfilename, 'w+')
                    fout.write(str(self.colNum) + " " + str(temp))
                    fout.close()
                    # 结束计算后，统计信息并输出到主进程
                    msg = u"数据计算结束!使用物化视图计算方法！"
                    wx.CallAfter(self.window.LogMessage, msg)
                    OutGrids = u"物化视图计算结束时间:"
                    wx.CallAfter(self.window.GridsMsg, OutGrids, 3)
                    OutGrids = u"物化视图计算所用时间:"
                    wx.CallAfter(self.window.GridsMsg, OutGrids, 4)
                    OutGrids = u"计算结果为:" + str(temp)
                    wx.CallAfter(self.window.GridsMsg, OutGrids)
                else:
                    msg = u"未找到可用视图!"
                    wx.CallAfter(self.window.GridsMsg, msg)
                    wx.CallAfter(self.window.LogMessage, msg)
                    # 打开传入子线程的文件，并读取文件的数据
                    fout = open(self.filePath)
                    contents = fout.readlines()[:self.colNum]
                    # temp存入计算后的结果，i则为了显示计算过程设置的千位数
                    temp = 0
                    i = 0
                    # 计算过程，以掉线率计算为模板
                    for content in contents:
                        if(i % 1000 == 0):
                            msg = u"正在计算第" + str(i / 1000 + 1) + u"千行数据！"
                            wx.CallAfter(self.window.LogMessage, msg)
                        data = content.rsplit(" ")
                        diaoxian = (float(data[1]) - float(data[2])) / \
                            (float(data[3]) - float(data[4].rstrip("\n")))
                        temp += diaoxian
                        i += 1
                    temp /= self.colNum
                    # 每次常规计算后都将计算结果存入默认视图文件，待物化视图方法的调用
                    fout = open(viewfilename, 'w+')
                    fout.write(str(self.colNum) + " " + str(temp))
                    fout.close()
                    # 结束计算后，统计信息并输出到主进程
                    msg = u"数据计算结束!未查找到视图，使用常规计算方法！"
                    wx.CallAfter(self.window.LogMessage, msg)
                    OutGrids = u"常规数据计算结束时间:"
                    wx.CallAfter(self.window.GridsMsg, OutGrids, 3)
                    OutGrids = u"常规数据计算所用时间:"
                    wx.CallAfter(self.window.GridsMsg, OutGrids, 4)
                    OutGrids = u"计算结果为:" + str(temp)
                    wx.CallAfter(self.window.GridsMsg, OutGrids)
        except:
            msg = u"计算出现错误，请重新操作！"
            wx.CallAfter(self.window.LogMessage, msg)


class Screen(threading.Thread):
    '''
    筛选异常用户数据子线程
    '''

    def __init__(self, filePath, window):
        threading.Thread.__init__(self)
        self.filePath = filePath
        self.window = window
        # 初始化实例时即开始此子线程，若要控制开始子线程需将此语句移入主线程进行调用
        self.start()

    def run(self):
        OutGrids = u"当前处理文件:" + self.filePath + "\n"
        wx.CallAfter(self.window.GridsMsg, OutGrids, 1)
        try:
            # 尝试打开所给文件，若打不开，则输出此文件不存在到主窗口
            OutGrids = u"异常用户数据筛选开始时间:"
            wx.CallAfter(self.window.GridsMsg, OutGrids, 2)
            msg = u"异常用户数据筛选开始!"
            wx.CallAfter(self.window.LogMessage, msg)
            file = open(self.filePath)
            contents = file.readlines()
            contentNum = len(contents)
            i = 0
            erroruserNum = 0
            for content in contents:
                if (i % 1000 == 0):
                    msg = u"正在筛选第" + str(i / 1000 + 1) + u"千行数据！"
                    wx.CallAfter(self.window.LogMessage, msg)
                temp = content.split(',')
                aoa = int(temp[32])
                ta = int(temp[33])
                if(aoa > 700 or aoa < 30 or ta == 0 or
                   ta == 361 or ta == 65535):
                    erroruserNum += 1
                i += 1
                # count = count + 1
                # keepGoing = dialog.Update(count)
            # 每次常规计算后都将计算结果存入默认视图文件，待物化视图方法的调用
            # 结束计算后，统计信息并输出到主进程
            msg = u"异常用户数据筛选结束!"
            wx.CallAfter(self.window.LogMessage, msg)
            OutGrids = u"异常用户数据筛选结束时间:"
            wx.CallAfter(self.window.GridsMsg, OutGrids, 3)
            OutGrids = u"异常用户数据筛选所用时间:"
            wx.CallAfter(self.window.GridsMsg, OutGrids, 4)
            OutGrids = u"\n 筛选结果:" + "\n" + u"共获取到" + \
                str(contentNum) + u"个用户数据" + "\n" + \
                u"筛选出" + str(erroruserNum) + u"个异常用户"
            wx.CallAfter(self.window.GridsMsg, OutGrids)
        except:
            msg = u"此文件不存在或打开错误！"
            wx.CallAfter(self.window.LogMessage, msg)


class Detect(threading.Thread):
    '''
    盲点检测子线程
    '''

    def __init__(self, filePath, window):
        threading.Thread.__init__(self)
        self.filePath = filePath
        self.window = window
        # 初始化实例时即开始此子线程，若要控制开始子线程需将此语句移入主线程进行调用
        self.start()

    def run(self):
        OutGrids = u"当前处理文件:" + self.filePath + "\n"
        wx.CallAfter(self.window.GridsMsg, OutGrids, 1)
        try:
            # 尝试打开所给文件，若打不开，则输出此文件不存在到主窗口
            OutGrids = u"盲点检测开始时间:"
            wx.CallAfter(self.window.GridsMsg, OutGrids, 2)
            msg = u"盲点检测开始!"
            wx.CallAfter(self.window.LogMessage, msg)
            file = open(self.filePath)
            contents = file.readlines()
            contentNum = len(contents)
            i = 0
            erroruserNum = 0
            MuserNum = 0
            for content in contents:
                if (i % 1000 == 0):
                    msg = u"正在检测第" + str(i / 1000 + 1) + u"千行数据！"
                    wx.CallAfter(self.window.LogMessage, msg)
                temp = content.split(',')
                aoa = int(temp[32])
                ta = int(temp[33])
                receive = int(temp[29])
                if(aoa > 700 or aoa < 30 or ta == 0 or
                   ta == 361 or ta == 65535):
                    erroruserNum += 1
                elif(receive < 46 - self.window.MNum * 2):
                    MuserNum += 1
                i += 1
                # count = count + 1
                # keepGoing = dialog.Update(count)
            # 每次常规计算后都将计算结果存入默认视图文件，待物化视图方法的调用
            # 结束计算后，统计信息并输出到主进程
            msg = u"盲点检测结束!"
            wx.CallAfter(self.window.LogMessage, msg)
            OutGrids = u"盲点检测结束时间:"
            wx.CallAfter(self.window.GridsMsg, OutGrids, 3)
            OutGrids = u"盲点检测所用时间:"
            wx.CallAfter(self.window.GridsMsg, OutGrids, 4)
            OutGrids = u"\n 检测简略结果:" + "\n" + u"共获取到" + \
                str(contentNum - erroruserNum) + u"个有效用户数据" + \
                "\n" + u"共检测" + str(MuserNum) + u"个盲点用户"
            wx.CallAfter(self.window.GridsMsg, OutGrids)
        except:
            msg = u"此文件不存在或打开错误！"
            wx.CallAfter(self.window.LogMessage, msg)


class OpenFile(threading.Thread):
    """
    This open bigdata file thread.
    """

    def __init__(self, filePath, colNum, window):
        threading.Thread.__init__(self)
        self.filePath = filePath
        self.window = window
        self.colNum = colNum
        self.messageDelay = 0.1 + 2.0 * random.random()
        # 初始化实例时即可开始run
        self.start()

    def run(self):
        try:
            # 开始读取数据
            msg = u"数据读取开始!"
            wx.CallAfter(self.window.LogMessage, msg)
            # 打开传入子线程的文件，并读入数据
            file = open(self.filePath)
            contentList = file.readlines()
            self.contentSelected = []
            content = ''
            # 如果给定的读取行数大于数据文件的自身行数，则最多只能读取自身行数
            if self.colNum > len(contentList):
                self.colNum = len(contentList)
            for i in range(self.colNum):
                if(i % 1000 == 0):
                    msg = u"正在读取第" + str(i / 1000 + 1) + u"千行数据！"
                    wx.CallAfter(self.window.LogMessage, msg)
                content = content + contentList[i]
                self.contentSelected.append(contentList[i])
            # print content
            # print len(self.contentSelected)
            sample = self.contentSelected[0].split(',')[:-1]
            contentlist = [x.split(',')[:-1] for x in self.contentSelected]
            if(len(sample) > 5):
                contentlist.insert(0, [(u"列" + str(i))
                                       for i in range(len(sample))])
                wx.CallAfter(self.window.DataPanelShow, contentlist)
            else:
                # self.contentlist.insert(0, [u"行数", u"eNodeB请求释放上下文数",
                #     u"正常的eNodeB请求释放上下文数", u"初始上下文建立成功次数",
                #     u"用户不活动原因eNodeB请求释放上下文数"])
                wx.CallAfter(self.window.Set_grids, content.decode('utf-8'))
            # print self.contentlist
            # print self.contetnlist

            file.close()
            # 数据读取结束，输出相应信息到主进程
            msg = u"数据读取结束!"
            wx.CallAfter(self.window.LogMessage, msg)
            msg = u"当前处理文件：" + self.filePath + \
                "\t" + u"显示行数：" + str(self.colNum)
            wx.CallAfter(self.window.LogMessage, msg)
        except:
            msg = u"未进行显示数据操作！"
            wx.CallAfter(self.window.LogMessage, msg)


class Demo(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1,
                          title=u"基于用户组的网络性能分析系统",
                          size=(1200, 1000),
                          style=wx.DEFAULT_FRAME_STYLE | wx.TRANSPARENT_WINDOW)
        self.Centre()
        self.Bind(wx.EVT_CLOSE, self.OnClose)  # 绑定关闭窗口函数
        self.SetMaxSize((1200, 1000))
        self.SetMinSize((1200, 1000))
        self.List = []  # 控制case 1,2两个应用中的图片显示，若显示了图片则将其bitmap添加进list
        f = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL, False, face=u"华文新魏")

        # 河白 #FFFFFF rgb(255, 255, 255)
        # 杏仁黄 #FAF9DE rgb(250, 249, 222)
        # 秋叶褐 #FFF2E2 rgb(255, 242, 226)
        # 胭脂红 #FDE6E0 rgb(253, 230, 224)
        # 青草绿 #E3EDCD rgb(227, 237, 205)
        # 海天蓝 #DCE2F1 rgb(220, 226, 241)
        # 葛巾紫 #E9EBFE rgb(233, 235, 254)
        # 极光灰 #EAEAEF rgb(234, 234, 239)
        # self.SetBackgroundColour('#DCE2F1')#海天蓝
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        # self.Cflag = 0#折叠功能标志
        # 设置四个panel，分别为功能模块选择面板，功能模块内含按钮面板，输出面板以及状态栏面板
        # self.SetBackgroundColour("White")
        self.Panel1 = wx.Panel(self, -1)
        self.Panel1.Bind(wx.EVT_PAINT, self.OnPaint)
        # self.Panel1.SetBackgroundColour('#FFF2E2')
        # self.Centre()

        self.Panel2 = wx.Panel(self)
        self.Panel2.Bind(wx.EVT_PAINT, self.OnPaint2)
        self.Panel2.SetBackgroundColour('#DCE2F1')
        # self.Panel2.SetBackgroundColour('Green')

        self.Panel3 = wx.Panel(self)
        # self.Panel3.SetBackgroundColour('Blue')
        # self.Panel3.SetBackgroundColour('#DCE2F1')
        self.Panel3.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Panel3.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        # self.Panel3.Bind(wx.EVT_MOTION, self.OnMotion)

        self.Panel4 = wx.Panel(self)
        # self.Panel4.SetBackgroundColour('Yellow')
        self.Panel1.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackgroundPanel)
        # self.Panel2.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        # ***************panel 1******功能模块面板内含信息初始化****************************
        IndexSystemButton = wx.Button(
            self.Panel1, label=u'       新型KPI分析      ')
        IndexSystemButton.Bind(wx.EVT_BUTTON, self.IndexSystem)

        BigDataAnalysisButton = wx.Button(self.Panel1, label=u'大数据计算效率演示')
        BigDataAnalysisButton.Bind(wx.EVT_BUTTON, self.BigDataAnalysis)

        CaseShowButton = wx.Button(self.Panel1, label=u'功能')
        CaseShowButton.Bind(wx.EVT_BUTTON, self.CaseShow)

        CaseOneButton = wx.Button(self.Panel1, label=u'盲点检测')
        CaseOneButton.Bind(wx.EVT_BUTTON, self.CaseOne)
        CaseTwoButton = wx.Button(self.Panel1, label=u'用户密度预测')
        CaseTwoButton.Bind(wx.EVT_BUTTON, self.CaseTwo)
        CaseThreeButton = wx.Button(self.Panel1, label=u'网络异常分析')
        CaseThreeButton.Bind(wx.EVT_BUTTON, self.CaseThree)

        IndexSystemButton.SetBackgroundColour('#E9EBFE')  # 葛巾紫
        BigDataAnalysisButton.SetBackgroundColour('#E9EBFE')  # 葛巾紫
        CaseShowButton.SetBackgroundColour('#E9EBFE')  # 葛巾紫
        CaseOneButton.SetBackgroundColour('#E9EBFE')  # 葛巾紫
        CaseTwoButton.SetBackgroundColour('#E9EBFE')  # 葛巾紫
        CaseThreeButton.SetBackgroundColour('#E9EBFE')  # 葛巾紫
        # ***************panel 1**********************************************
        # ***************panel 2  part 1********功能面板--指标体系内含信息初始化**************
        self.sampleList1 = {
            u"接入类指标": 0,
            u"保持类指标": 1,
            u"信道类指标": 2,
            u"用户分布类指标": 3,
            u"用户感知类指标": 4,
            u"其他类指标": 5
        }
        self.sampleList2 = [
            [u"业务请求时延", u"加密时延", u"身份识别时延", u"TMSI重分配时延", u"语音寻呼时延"],
            [u"剔除UI的无线掉线率"],
            [u"阴影效应", u"多普勒效应", u"远近效应"],
            [u"用户密度", u"用户密度对通信质量影响"],
            [u"低接通用户数劣化指标", u"高掉线用户数劣化指标", u"高流量用户时延劣化指标",
             u"高信道质量掉线劣化指标", u"高流量用户接通劣化指标", u"高时延用户数劣化指标"],
            [u"上行业务质量", u"上行噪声影响", u"上行干扰对弱覆盖的影响", u"下行业务弱覆盖影响"]
        ]
        self.sampleList1_2 = [u"微域级", u"小区级", u"区域级"]

        self.indexRegion = wx.StaticText(
            self.Panel2, -1, u"指标小区选择:", style=wx.ALIGN_CENTER)
        self.sampleList_IR = [u"华科部分小区"]
        self.choices_IR = wx.Choice(
            self.Panel2, -1, choices=self.sampleList_IR, style=wx.ALIGN_CENTER)

        self.sample = wx.StaticText(
            self.Panel2, -1, u"指标类型:", style=wx.ALIGN_CENTER)
        self.choices1 = wx.Choice(self.Panel2, -1,
                                  choices=self.sampleList1.keys(),
                                  style=wx.ALIGN_CENTER)

        self.indexname = wx.StaticText(
            self.Panel2, -1, u"指标名称:", style=wx.ALIGN_CENTER)
        # self.choices2 = wx.Choice(self.Panel2, -1,
        #                           choices=self.sampleList2[0],
        #                           style=wx.ALIGN_CENTER)
        self.choices2 = wx.Choice(self.Panel2, -1, style=wx.ALIGN_CENTER)

        self.name1_2 = wx.StaticText(
            self.Panel2, -1, u"指标域级:", style=wx.ALIGN_CENTER)
        self.choices1_2 = wx.Choice(
            self.Panel2, -1, choices=self.sampleList1_2, style=wx.ALIGN_CENTER)

        self.DXImportButton = wx.Button(self.Panel2, label=u'数据导入')
        self.DXImportButton.Bind(wx.EVT_BUTTON, self.DXImport)
        self.DXComputeButton = wx.Button(self.Panel2, label=u'指标计算')
        self.DXComputeButton.Bind(wx.EVT_BUTTON, self.DXCompute)
        # 增添一个数据显示面板的测试按钮
        self.datapaneltestButton = wx.Button(self.Panel2, label=u"测试数据显示面板")
        self.datapaneltestButton.Bind(wx.EVT_BUTTON, self.DataPanelTest)

        self.DXFile = ''

        self.choices1.Bind(wx.EVT_CHOICE, self.UpdateC2)
        self.choices2.Bind(wx.EVT_CHOICE, self.UpdateC1)
        # ***************panel 2  part 1***************************************
        # ***************panel 2  part 2**功能面板--大数据分析内含信息初始化*******************
        self.methods = wx.StaticText(
            self.Panel2, -1, u"计算方法:", style=wx.ALIGN_CENTER)
        self.sampleList3 = [u"常规方法", u"物化视图"]
        self.choices3 = wx.Choice(
            self.Panel2, -1, choices=self.sampleList3, style=wx.ALIGN_CENTER)

        self.InputBigDataButton = wx.Button(self.Panel2, label=u'添加数据源')
        self.InputBigDataButton.Bind(wx.EVT_BUTTON, self.InputBigData)
        # init opend file list of BigDataAnalysis
        self.BigDataAnalysisFileList = []

        self.ShowDataButton = wx.Button(self.Panel2, label=u'导入并显示数据')
        self.ShowDataButton.Bind(wx.EVT_BUTTON, self.ShowData)

        self.DataProcessButton = wx.Button(self.Panel2, label=u'数据操作')
        self.DataProcessButton.Bind(wx.EVT_BUTTON, self.DataProcess)

        self.ComputingButton = wx.Button(self.Panel2, label=u'开始计算并统计')
        self.ComputingButton.Bind(wx.EVT_BUTTON, self.Computing)
        # ***************panel 2  part 2***************************************
        # ***************panel 2  part 3 --case 1**功能面板--盲点检测内含信息初始化***********
        self.InputMDataButton = wx.Button(self.Panel2, label=u'添加数据源')
        self.InputMDataButton.Bind(wx.EVT_BUTTON, self.InputMData)
        # init opend file list of MDatadetect
        self.MDataAnalysisFileList = []

        self.ShowMDataButton = wx.Button(self.Panel2, label=u'数据显示')
        self.ShowMDataButton.Bind(wx.EVT_BUTTON, self.ShowMData)

        self.ScreenDataButton = wx.Button(self.Panel2, label=u'筛选异常用户数据')
        self.ScreenDataButton.Bind(wx.EVT_BUTTON, self.ScreenData)

        self.MSelectUserRegionButton = wx.Button(self.Panel2, label=u'用户区域选择')
        self.MSelectUserRegionButton.Bind(
            wx.EVT_BUTTON, self.MselectUserRegion)
        self.times1 = wx.StaticText(
            self.Panel2, -1, u"时段选择:", style=wx.ALIGN_CENTER)
        self.sampleList6 = [u"时段1：早上", u"时段2：下午", u"时段3：晚上", u"整合图"]
        self.choices6 = wx.Choice(
            self.Panel2, -1, choices=self.sampleList6, style=wx.ALIGN_CENTER)
        self.pig1_1 = wx.StaticText(
            self.Panel2, -1, u"图型选择:", style=wx.ALIGN_CENTER)
        self.sampleList6_1 = [u"平面图", u"卫星图"]
        self.choices6_1 = wx.Choice(
            self.Panel2, -1, choices=self.sampleList6_1, style=wx.ALIGN_CENTER)
        # self.choices6_1.Bind(wx.EVT_CHOICE, self.ShowC61)

        self.BlindspotMonitorButton = wx.Button(self.Panel2, label=u'盲点检测')
        self.BlindspotMonitorButton.Bind(wx.EVT_BUTTON, self.BlindspotMonitor)

        self.ResultOutputButton = wx.Button(self.Panel2, label=u'结果输出')
        self.ResultOutputButton.Bind(wx.EVT_BUTTON, self.ResultOutput)
        # ***************panel 2  part 3 --case 1******************************
        # ***************panel 2  part 4 --case 2******功能面板--用户预测内含信息初始化*******
        self.InputPDataButton = wx.Button(self.Panel2, label=u'添加数据源')
        self.InputPDataButton.Bind(wx.EVT_BUTTON, self.InputUserData)
        # init opend file list of MDatadetect
        self.PDataAnalysisFileList = []

        self.ShowPDataButton = wx.Button(self.Panel2, label=u'数据显示')
        self.ShowPDataButton.Bind(wx.EVT_BUTTON, self.ShowPData)

        # 用户预测的异常用户筛选复用应用1盲点检测中的异常用户检测
        self.ScreenUserDataButton = wx.Button(self.Panel2, label=u'筛选异常用户数据')
        self.ScreenUserDataButton.Bind(wx.EVT_BUTTON, self.ScreenData)

        self.SelectUserRegionButton = wx.Button(self.Panel2, label=u'用户区域选择')
        self.SelectUserRegionButton.Bind(wx.EVT_BUTTON, self.selectUserRegion)
        # 注释部分为下拉框选择用户区域
        # self.regions = wx.StaticText(self.Panel2, -1,
        #                              u"用户区域选择:", style=wx.ALIGN_CENTER)
        # self.sampleList4 = [u"区域1：图书馆",
        #                     u"区域2：韵苑食堂", u"区域3：主校区操场"]
        # self.choices4 = wx.Choice(self.Panel2, -1,
        # choices=self.sampleList4, style=wx.ALIGN_CENTER)

        self.times2 = wx.StaticText(
            self.Panel2, -1, u"预测时间:", style=wx.ALIGN_CENTER)
        self.sampleList5 = [u"10分钟", u"20分钟", u"30分钟", u"60分钟", u"整合图"]
        self.choices5 = wx.Choice(
            self.Panel2, -1, choices=self.sampleList5, style=wx.ALIGN_CENTER)

        self.UserPredictButton = wx.Button(self.Panel2, label=u'用户密度预测')
        self.UserPredictButton.Bind(wx.EVT_BUTTON, self.UserPredict)
        # ***************panel 2  part 4 --case 2******************************

        # ***************panel 2  part 4 --case 3 功能面板 应用3 异常信令事件分析************
        self.regionSelectButton = wx.Button(self.Panel2, label=u'选择区域')
        self.regionSelectButton.Bind(wx.EVT_BUTTON, self.RegionSelect)

        self.ImportMatrixButton = wx.Button(self.Panel2, label=u'导入数据源')
        self.ImportMatrixButton.Bind(wx.EVT_BUTTON, self.ImportMatrix)

        self.InitMatrixButton = wx.Button(self.Panel2, label=u'初始化矩阵表')
        self.InitMatrixButton.Bind(wx.EVT_BUTTON, self.InitMatrix)

        self.AddMatrixButton = wx.Button(self.Panel2, label=u'自动扩充矩阵表')
        self.AddMatrixButton.Bind(wx.EVT_BUTTON, self.ImportZDMatrix)

        self.HAddMatrixButton = wx.Button(self.Panel2, label=u'手动扩充矩阵表')
        self.HAddMatrixButton.Bind(wx.EVT_BUTTON, self.HAddMatrix)

        # self.ShowMatrixButton = wx.Button(self.Panel2, label=u'显示当前矩阵表')
        # self.ShowMatrixButton.Bind(wx.EVT_BUTTON, self.ShowMatrix)

        self.Problem = wx.StaticText(
            self.Panel2, -1, u"故障:", style=wx.ALIGN_CENTER)
        self.sampleListP = {}
        self.choicesP = wx.Choice(self.Panel2,
                                  id=-1,
                                  choices=self.sampleListP.keys(),
                                  style=wx.ALIGN_CENTER)

        self.MatrixFile = ''
        self.ZDMatrixFile = ''

        self.ProblemSolButton = wx.Button(self.Panel2, label=u'问题诊断')
        self.ProblemSolButton.Bind(wx.EVT_BUTTON, self.ProblemSol)
        # ***************panel 2  part 4 --case 3******************************
        # ***************panel 3*****输出信息面板初始化*********************************
        self.grids = wx.TextCtrl(
            self.Panel3, -1, style=wx.TE_MULTILINE | wx.TE_RICH2)
        self.grids.SetFont(
            wx.Font(18, wx.ROMAN, wx.NORMAL, wx.NORMAL, False))
        # ***************panel 3**********************************************

        # ***************panel 3*****数据显示面板---ListCtrl初始化**********************
        self.datapanel = wx.ListCtrl(
            self.Panel3, style=wx.LC_REPORT)  # 当前风格支持多列
        self.datapanel.SetFont(
            wx.Font(18, wx.ROMAN, wx.NORMAL, wx.NORMAL, False))
        # ***************panel 3**********************************************

        # ***************panel 3*****图片结果显示面板---StaticBitmap 初始化***************
        # self.SSB = wx.StaticBitmap()
        # ***************panel 3**********************************************

        # ***************panel 4*******状态栏面板初始化********************************
        # 状态栏
        self.bar = wx.StaticText(
            self.Panel4, style=wx.TE_MULTILINE | wx.TE_RICH2)
        # f = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL, False)
        # self.bar.SetFont(f)
        self.bar.SetMinSize((1168, 49))
        self.posText = wx.StaticText(self.Panel4, -1, u"中心经纬度:")
        self.posCtrl_1 = wx.StaticText(self.Panel4, -1, " ")
        self.posText_n = wx.StaticText(self.Panel4, -1, u"区域:")
        self.posCtrl_n = wx.StaticText(self.Panel4, -1, " ")
        # ***************panel 4**********************************************

        # ***************panel 1 box set****功能模块内含信息boxsizer设置*****************
        self.CSTbox = wx.BoxSizer(wx.VERTICAL)
        self.CSTbox.Add(CaseOneButton, proportion=0,
                        flag=wx.LEFT | wx.TOP, border=25)
        self.CSTbox.Add(CaseTwoButton, proportion=0,
                        flag=wx.LEFT | wx.TOP, border=25)
        self.CSTbox.Add(CaseThreeButton, proportion=0,
                        flag=wx.LEFT | wx.TOP, border=25)

        self.ISBbox = wx.BoxSizer(wx.VERTICAL)
        self.ISBbox.Add(IndexSystemButton, proportion=0,
                        flag=wx.TOP, border=25)

        self.BDAbox = wx.BoxSizer(wx.VERTICAL)
        self.BDAbox.Add(BigDataAnalysisButton, proportion=0,
                        flag=wx.TOP, border=50)

        self.CSSbox = wx.BoxSizer()
        self.CSSbox.Add(CaseShowButton, proportion=0,
                        flag=wx.TOP, border=20)

        self.CSbox = wx.BoxSizer(wx.VERTICAL)
        self.CSbox.Add(self.CSSbox, proportion=0,
                       flag=wx.LEFT, border=50)
        self.CSbox.Add(self.CSTbox, proportion=0, flag=wx.TOP, border=10)
        # self.CSbox.Hide(self.CSTbox) //折叠功能，与CaseShow函数中的注释内容对应

        self.hbox = wx.BoxSizer(wx.VERTICAL)
        self.hbox.Add(self.ISBbox, proportion=15, flag=wx.ALL, border=10)
        self.hbox.Add(self.CSbox, proportion=50, flag=wx.ALL, border=10)
        self.hbox.Add(self.BDAbox, proportion=30, flag=wx.ALL, border=10)

        self.vbox = wx.BoxSizer()
        self.vbox.Add(self.hbox, proportion=0,
                      flag=wx.ALL | wx.EXPAND, border=0)

        self.Panel1.SetSizer(self.vbox)
        # ***************panel 1 box set***************************************

        # ***************panel 2  part 1 box set***功能面板--指标体系内含信息设置************
        self.Hbox = wx.BoxSizer()
        self.Hbox.Add(self.name1_2, proportion=0, flag=wx.ALL, border=15)
        self.Hbox.Add(self.choices1_2, proportion=0, flag=wx.ALL, border=10)

        self.Labox = wx.BoxSizer()

        self.Lbbox = wx.BoxSizer()

        self.Lbbox.Add(self.indexRegion, proportion=0, flag=wx.ALL, border=15)
        self.Lbbox.Add(self.choices_IR, proportion=0, flag=wx.ALL, border=10)
        self.Lbbox.Add(self.sample, proportion=0, flag=wx.ALL, border=15)
        self.Lbbox.Add(self.choices1, proportion=0, flag=wx.ALL, border=10)
        self.Lbbox.Add(self.indexname, proportion=0, flag=wx.ALL, border=15)
        self.Lbbox.Add(self.choices2, proportion=0, flag=wx.ALL, border=10)

        self.Lcbox = wx.BoxSizer()
        self.Lcbox.Add(self.DXImportButton, proportion=0,
                       flag=wx.ALL, border=10)
        self.Lcbox.Add(self.DXComputeButton, proportion=0,
                       flag=wx.ALL, border=10)
        self.Lcbox.Add(self.Hbox, proportion=0, flag=wx.ALL, border=0)
        self.Lcbox.Add(self.datapaneltestButton,
                       proportion=0, flag=wx.ALL, border=10)

        self.Ldbox = wx.BoxSizer(wx.VERTICAL)
        self.Ldbox.Add(self.Lbbox, proportion=0, flag=wx.ALL, border=0)
        self.Ldbox.Add(self.Lcbox, proportion=0, flag=wx.ALL, border=0)

        self.Labox.Add(self.Ldbox, proportion=0, flag=wx.ALL, border=0)
        # ***************panel 2 part 1 box set********************************
        # ***************panel 2 part 2 box set*****功能面板--大数据分析内含信息设置**********
        self.DPbox = wx.BoxSizer(wx.VERTICAL)

        self.DPBbox = wx.BoxSizer()
        self.DPBbox.Add(self.methods, proportion=0, flag=wx.ALL, border=20)
        self.DPBbox.Add(self.choices3, proportion=0, flag=wx.ALL, border=10)

        self.DPAbox = wx.BoxSizer()
        self.DPAbox.Add(self.InputBigDataButton,
                        proportion=0, flag=wx.LEFT, border=10)
        self.DPAbox.Add(self.ShowDataButton, proportion=0,
                        flag=wx.LEFT, border=10)
        self.DPAbox.Add(self.DataProcessButton, proportion=0,
                        flag=wx.LEFT, border=10)
        self.DPAbox.Add(self.ComputingButton, proportion=0,
                        flag=wx.LEFT, border=10)

        self.DPbox.Add(self.DPBbox, proportion=0, flag=wx.ALL, border=0)
        self.DPbox.Add(self.DPAbox, proportion=0, flag=wx.ALL, border=0)
        # ***************panel 2 part 2 box set********************************
        # ***************panel 2 part 3 box set********功能面板--盲点检测内含信息设置********
        self.IDbox = wx.BoxSizer(wx.VERTICAL)
        self.IDbox.Add(self.InputMDataButton, proportion=0,
                       flag=wx.LEFT, border=0)

        self.MDbox = wx.BoxSizer(wx.VERTICAL)
        self.MDbox.Add(self.ShowMDataButton, proportion=0,
                       flag=wx.LEFT, border=0)

        self.SDbox = wx.BoxSizer(wx.VERTICAL)
        self.SDbox.Add(self.ScreenDataButton, proportion=0,
                       flag=wx.LEFT, border=0)

        self.BMbox = wx.BoxSizer(wx.VERTICAL)
        self.BMbox.Add(self.BlindspotMonitorButton,
                       proportion=0, flag=wx.LEFT, border=0)

        self.RObox = wx.BoxSizer(wx.VERTICAL)
        self.RObox.Add(self.ResultOutputButton,
                       proportion=0, flag=wx.LEFT, border=0)

        self.Bhbox = wx.BoxSizer()
        self.Bhbox.Add(self.IDbox, proportion=0, flag=wx.ALL, border=10)
        self.Bhbox.Add(self.MDbox, proportion=0, flag=wx.ALL, border=10)
        self.Bhbox.Add(self.SDbox, proportion=0, flag=wx.ALL, border=10)
        self.Bhbox.Add(self.BMbox, proportion=0, flag=wx.ALL, border=10)

        self.Bhbbox = wx.BoxSizer()
        self.Bhbbox.Add(self.MSelectUserRegionButton,
                        proportion=0, flag=wx.ALL, border=10)
        self.Bhbbox.Add(self.times1, proportion=0, flag=wx.ALL, border=15)
        self.Bhbbox.Add(self.choices6, proportion=0, flag=wx.ALL, border=10)
        self.Bhbbox.Add(self.pig1_1, proportion=0, flag=wx.ALL, border=15)
        self.Bhbbox.Add(self.choices6_1, proportion=0, flag=wx.ALL, border=10)
        self.Bhbbox.Add(self.RObox, proportion=0, flag=wx.ALL, border=10)

        self.Bvbox = wx.BoxSizer(wx.VERTICAL)
        self.Bvbox.Add(self.Bhbox, proportion=0, flag=wx.ALL, border=0)
        self.Bvbox.Add(self.Bhbbox, proportion=0, flag=wx.ALL, border=0)
        # ***************panel 2 part 3 box set********************************
        # ***************panel 2 part 4 box set*********功能面板--用户预测内含信息设置*******
        self.UPAbox = wx.BoxSizer()
        self.UPAbox.Add(self.InputPDataButton, proportion=0,
                        flag=wx.ALL, border=10)
        self.UPAbox.Add(self.ShowPDataButton, proportion=0,
                        flag=wx.ALL, border=10)
        self.UPAbox.Add(self.ScreenUserDataButton,
                        proportion=0, flag=wx.ALL, border=10)
        self.UPBbox = wx.BoxSizer()
        self.UPBbox.Add(self.SelectUserRegionButton,
                        proportion=0, flag=wx.ALL, border=10)
        # 注释部分为下拉框选择用户区域
        # self.UPBbox.Add(self.regions, proportion=0, flag=wx.ALL, border=15)
        # self.UPBbox.Add(self.choices4, proportion=0, flag=wx.ALL, border=10)
        self.UPBbox.Add(self.times2, proportion=0, flag=wx.ALL, border=15)
        self.UPBbox.Add(self.choices5, proportion=0, flag=wx.ALL, border=10)
        self.UPBbox.Add(self.UserPredictButton,
                        proportion=0, flag=wx.ALL, border=10)

        self.UPbox = wx.BoxSizer(wx.VERTICAL)
        self.UPbox.Add(self.UPAbox, proportion=0, flag=wx.ALL, border=0)
        self.UPbox.Add(self.UPBbox, proportion=0, flag=wx.ALL, border=0)
        # ***************panel 2 part 4 box set********************************
        # ***************panel 2 part 5 box set*********功能面板--异常信令分析内含信息设置*****
        self.PPAbox = wx.BoxSizer()
        self.PPAbox.Add(self.regionSelectButton,
                        proportion=0, flag=wx.ALL, border=10)
        self.PPAbox.Add(self.ImportMatrixButton,
                        proportion=0, flag=wx.ALL, border=10)
        self.PPAbox.Add(self.InitMatrixButton, proportion=0,
                        flag=wx.ALL, border=10)
        self.PPAbox.Add(self.AddMatrixButton, proportion=0,
                        flag=wx.ALL, border=10)
        self.PPBbox = wx.BoxSizer()
        self.PPBbox.Add(self.HAddMatrixButton, proportion=0,
                        flag=wx.ALL, border=10)
        # self.PPBbox.Add(self.ShowMatrixButton, proportion=0,
        #                 flag=wx.ALL, border=10)
        self.PPBbox.Add(self.Problem, proportion=0, flag=wx.ALL, border=15)
        self.PPBbox.Add(self.choicesP, proportion=0, flag=wx.ALL, border=10)
        self.PPBbox.Add(self.ProblemSolButton, proportion=0,
                        flag=wx.ALL, border=10)

        self.PPbox = wx.BoxSizer(wx.VERTICAL)
        self.PPbox.Add(self.PPAbox, proportion=0, flag=wx.ALL, border=0)
        self.PPbox.Add(self.PPBbox, proportion=0, flag=wx.ALL, border=0)
        # ***************panel 2 part 4 box set********************************
        # ***************panel 2 box set**************功能面板整合所有功能设置*************
        self.P2box = wx.BoxSizer(wx.VERTICAL)
        self.P2box.Add(self.Labox, proportion=0, flag=wx.ALL, border=0)
        self.P2box.Add(self.DPbox, proportion=0, flag=wx.ALL, border=0)
        self.P2box.Add(self.Bvbox, proportion=0, flag=wx.ALL, border=0)
        self.P2box.Add(self.UPbox, proportion=0, flag=wx.ALL, border=0)
        self.P2box.Add(self.PPbox, proportion=0, flag=wx.ALL, border=0)

        self.P2box.Hide(self.Labox)
        self.P2box.Hide(self.DPbox)
        self.P2box.Hide(self.Bvbox)
        self.P2box.Hide(self.UPbox)
        self.P2box.Hide(self.PPbox)

        self.Panel2.SetSizer(self.P2box)
        # ***************panel 2 box set***************************************
        # ***************panel 3 box set*****************输出信息面板设置**************
        self.P3abox = wx.BoxSizer(wx.VERTICAL)
        self.P3abox.Add(self.grids, proportion=1,
                        flag=wx.EXPAND | wx.ALL, border=0)
        self.P3abox.Add(self.datapanel, proportion=1,
                        flag=wx.EXPAND | wx.ALL, border=0)
        self.P3abox.Hide(self.datapanel)

        self.Panel3.SetSizer(self.P3abox)
        # ***************panel 3 box set***************************************

        # ***************panel 4 box set******************状态栏面板设置**************
        self.box_P41 = wx.BoxSizer()
        self.box_P41.Add(self.posText, proportion=1, flag=wx.ALL, border=10)
        self.box_P41.Add(self.posCtrl_1, proportion=2, flag=wx.ALL, border=10)
        self.box_P41.Add(self.posText_n, proportion=1, flag=wx.ALL, border=10)
        self.box_P41.Add(self.posCtrl_n, proportion=2, flag=wx.ALL, border=10)

        self.P4abox = wx.BoxSizer(wx.VERTICAL)
        self.P4abox.Add(self.bar, proportion=0,
                        flag=wx.EXPAND | wx.ALL, border=0)
        self.P4abox.Add(self.box_P41, proportion=0,
                        flag=wx.EXPAND | wx.ALL, border=0)

        self.P4abox.Hide(self.box_P41)
        self.Panel4.SetSizer(self.P4abox)
        # ***************panel 4 box set***************************************

        # ***************window box set*******************主窗口设置****************
        self.mbox = wx.BoxSizer(wx.VERTICAL)
        self.mbox.Add(self.Panel2, proportion=4,
                      flag=wx.ALL | wx.EXPAND, border=0)
        self.mbox.Add(self.Panel3, proportion=27,
                      flag=wx.ALL | wx.EXPAND, border=0)

        self.tbox = wx.BoxSizer()
        self.tbox.Add(self.Panel1, proportion=10,
                      flag=wx.ALL | wx.EXPAND, border=10)
        self.tbox.Add(self.mbox, proportion=42,
                      flag=wx.ALL | wx.EXPAND, border=10)

        self.wbox = wx.BoxSizer(wx.VERTICAL)
        self.wbox.Add(self.tbox, proportion=12,
                      flag=wx.ALL | wx.EXPAND, border=10)
        self.wbox.Add(self.Panel4, proportion=1,
                      flag=wx.ALL | wx.EXPAND, border=10)

        self.SetSizer(self.wbox)

        for i in self.Panel1.GetChildren():
            i.SetFont(f)
        f = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL, False)
        for i in self.Panel2.GetChildren():
            i.SetFont(f)
        for i in self.Panel4.GetChildren():
            i.SetFont(f)
        f1 = wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                     wx.FONTWEIGHT_NORMAL, False, face=u"华文新魏")
        CaseShowButton.SetFont(f1)
        # ***************window box set****************************************

    def DataPanelShow(self, data):
        if(len(data) == 0):  # 如果当前数据为空，则直接返回
            return
        # 数据显示面板进行显示送进来的数据，以列表形式，第一行为表头，其他的每一行分别为数据元素值
        # 隐藏panel3的文本域，将数据显示面板打开
        self.P3abox.Hide(self.grids)
        self.P3abox.Show(self.datapanel)
        self.wbox.Layout()
        # 清除当前数据表中存储的数据
        self.datapanel.ClearAll()
        # 第一行为表头，插入每一列的表头
        for i, title in enumerate(data[0]):
            self.datapanel.InsertColumn(i, title)
        # 之后每一行为数据内容，插入数据，以字符串数据插入
        for rowdata in data[1:]:
            self.datapanel.Append(rowdata)

    def DataPanelTest(self, evt):
        self.P3abox.Hide(self.grids)
        self.P3abox.Show(self.datapanel)
        self.wbox.Layout()
        # 插入三列，变成多行三列的列表
        self.datapanel.InsertColumn(0, "Artist")
        self.datapanel.InsertColumn(1, "Title", wx.LIST_FORMAT_LEFT)
        self.datapanel.InsertColumn(2, "Genreasdasdsadsadasdsadsadsad")

        # 添加三行
        # list.Append(["asa1", "asa2", "asa3", "asa4"])  # 超过当前的列数，触发中断错误
        self.datapanel.Append(["asa1", "asa2", "asa3"])
        self.datapanel.Append(["asb1", "asb2", "asb3"])
        self.datapanel.Append(["asc1", "asc2", "asc3"])

    def OnEraseBackground(self, evt):
        # print type(evt)
        print "Call the OnEraseBackground!"
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        # dc.Clear()
        bmp = wx.Bitmap(curFilePath + "\\" + "bg1.jpg")
        dc.DrawBitmap(bmp, 0, 0)

    def OnEraseBackgroundPanel(self, evt):
        # print type(evt)
        print "Call the OnEraseBackgroundPanel!"
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap(curFilePath + "\\" + "bgP1.jpg")
        dc.DrawBitmap(bmp, 0, 0)

    def EmptyFunc(self, evt):
        return

    def OnPaint(self, event):
        print "Call the OnPaint1 !"
        # 河白 #FFFFFF rgb(255, 255, 255)
        # 杏仁黄 #FAF9DE rgb(250, 249, 222)
        # 秋叶褐 #FFF2E2 rgb(255, 242, 226)
        # 胭脂红 #FDE6E0 rgb(253, 230, 224)
        # 青草绿 #E3EDCD rgb(227, 237, 205)
        # 海天蓝 #DCE2F1 rgb(220, 226, 241)
        # 葛巾紫 #E9EBFE rgb(233, 235, 254)
        # 极光灰 #EAEAEF rgb(234, 234, 239)
        dc = wx.PaintDC(self.Panel1)
        dc.SetBrush(wx.Brush("#DCE2F1"))
        dc.SetPen(wx.Pen('#4c4c4c', 3, wx.SOLID))
        dc.DrawRectangle(7, 17, 214, 70)
        dc.DrawRectangle(7, 120, 214, 350)
        dc.DrawRectangle(7, 606, 218, 100)

    def OnPaint2(self, event):
        print "Call the OnPaint2 !"
        # 河白 #FFFFFF rgb(255, 255, 255)
        # 杏仁黄 #FAF9DE rgb(250, 249, 222)
        # 秋叶褐 #FFF2E2 rgb(255, 242, 226)
        # 胭脂红 #FDE6E0 rgb(253, 230, 224)
        # 青草绿 #E3EDCD rgb(227, 237, 205)
        # 海天蓝 #DCE2F1 rgb(220, 226, 241)
        # 葛巾紫 #E9EBFE rgb(233, 235, 254)
        # 极光灰 #EAEAEF rgb(234, 234, 239)
        dc = wx.PaintDC(self.Panel2)
        dc.SetBrush(wx.Brush("#DCE2F1"))
        dc.SetPen(wx.Pen('#EEEEEE', 3, wx.SOLID))
        dc.DrawLine(0, 50, 1200, 50)

        # 当所有的图片，和图形都绘制完毕，将Paint、EraseBackGround事件都绑定到空函数上
        # 防止重复操作
        self.Panel1.Bind(wx.EVT_ERASE_BACKGROUND, self.EmptyFunc)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.EmptyFunc)
        self.Panel1.Bind(wx.EVT_PAINT, self.EmptyFunc)
        # self.Panel2.Bind(wx.EVT_PAINT, self.EmptyFunc)

    def IndexSystem(self, evt):

        self.ClearList()
        # 指标体系按钮事件
        self.P2box.Hide(self.Bvbox)
        self.P2box.Hide(self.DPbox)
        self.P2box.Hide(self.UPbox)
        self.P2box.Hide(self.PPbox)
        self.P2box.Show(self.Labox)
        # print self.Panel3.GetChildren()
        # self.P3abox.Hide(self.grids)
        self.wbox.Layout()
        self.ShowIndex()

    def ShowIndex(self):
        fou = open(u"指标体系\label.txt", 'r+')
        date = fou.readlines()  # [Ln].split(' ')
        fou.close()
        temp = u'                                                  新型KPI指标分析体系\n\n   新型用户级KPI，主要分' \
               u'为接入类指标、保持类指标、信道类指标、用户分布类指标、用户感知类指标以及其他指标六大类。\n\n'  # 送入输出信息面板显示的指标详情信息
        for i in date:
            data = i.split(' ')
            # 指标名称的显示
            name = data[0].decode("gbk")
            temp += u"指标名称：" + name + "\n"
            # 指标名称对应的定义显示
            definition = data[1].decode("gbk")
            temp += u"指标说明：" + definition + "\n"
            # 指标名称对应的计算公式
            comput = data[2].decode("gbk")
            temp += u"指标定义与计算：" + comput + "\n"
            if (len(data) == 6):
                # 指标细分，划分三种监控区域
                temp += u"按照监控区域细分如下：" + "\n"
                weiyu = data[3].decode("gbk")
                temp += u"微域级：" + weiyu + "\n"
                xiaoqu = data[4].decode("gbk")
                temp += u"小区级：" + xiaoqu + "\n"
                quyu = data[5].decode("gbk")
                temp += u"区域级：" + quyu + "\n"
                # 送入输出信息面板显示
        self.Set_grids(temp)

    def BigDataAnalysis(self, evt):
        self.ClearList()
        # 大数据分析按钮事件
        self.P2box.Hide(self.Labox)
        self.P2box.Hide(self.Bvbox)
        self.P2box.Hide(self.UPbox)
        self.P2box.Hide(self.PPbox)
        self.P2box.Show(self.DPbox)
        self.wbox.Layout()
        temp = u'本模块为大数据计算效率演示模块：\n\n' \
               u'---针对软硬采海量数据的情况，使用数据库相关技术来提升数据查询和刷新的效率，' \
               u'以保证对KPI指标的异动情况进行及时的' \
               u'分析。在数据处理方面拟引入物化视图技术，评估数据处理效率相比引入前能够提升80 %；同时保留良好扩展性，可和其他' \
               u'分布式运行框架（比如HADOOP技术和MPP技术）等结合，以进一步提升数据处理效率。\n\n本模块共包含两种方法：\n1、常' \
               u'规方法\n2、物化视图\n\n---将通过对比此两种方法对数据处理所使用时间来展示计算效率的提高。'
        self.Set_grids(temp)

    def CaseShow(self, evt):
        self.ClearList()
        temp = u'本模块为功能模块，共具有三个功能模块：\n\n1、盲点检测功能模块 ---主要进行盲点检测，关联指标进行筛选盲点用户；\n\n' \
               u'2、用户密度预测模块 ---针对指定区域进行用户筛选并预测一定时间内用户数量的变化；\n\n' \
               u'3、网络异常分析模块 ---建立异常问题矩阵数据库，针对导入数据库进行分析，给出相应的问题分析原因及解决方案。'
        self.Set_grids(temp)
        # 应用展示按钮事件，点击显示三个应用按钮
        '''if(self.Cflag == 0):
            self.CSbox.Show(self.CSTbox)
            self.vbox.Layout()
            self.Cflag = 1
        else:
            self.CSbox.Hide(self.CSTbox)
            self.vbox.Layout()
            self.Cflag = 0'''

    def CaseOne(self, evt):
        self.ClearList()
        # 应用1：盲点检测展示按钮事件
        self.P2box.Hide(self.Labox)
        self.P2box.Hide(self.DPbox)
        self.P2box.Hide(self.UPbox)
        self.P2box.Hide(self.PPbox)
        self.P2box.Show(self.Bvbox)
        self.wbox.Layout()

        temp = u'本模块为盲点检测功能模块 \n\n---主要进行盲点检测，关联指标进行筛选盲点用户。'
        self.Set_grids(temp)
        # self.grids.CanScroll(False)

    def CaseTwo(self, evt):
        self.ClearList()
        # 应用2：用户预测展示按钮事件
        self.P2box.Hide(self.Labox)
        self.P2box.Hide(self.DPbox)
        self.P2box.Hide(self.Bvbox)
        self.P2box.Hide(self.PPbox)
        self.P2box.Show(self.UPbox)
        self.wbox.Layout()
        temp = u'本模块为用户密度预测模块\n\n ---针对指定区域进行用户筛选并预测一定时间内用户数量的变化。'
        self.Set_grids(temp)

    def CaseThree(self, evt):
        self.ClearList()
        # 应用3：用户预测展示按钮事件
        self.P2box.Hide(self.Labox)
        self.P2box.Hide(self.DPbox)
        self.P2box.Hide(self.Bvbox)
        self.P2box.Hide(self.UPbox)
        self.P2box.Show(self.PPbox)
        self.wbox.Layout()
        temp = u'本模块为网络异常分析模块\n\n ---建立异常问题矩阵数据库。针对导入数据库进行分析，给出相应的问题分析原因及解决方案。'

        self.Set_grids(temp)

    def ImportZDMatrix(self, evt):
        # 故障矩阵的导入数据功能对话框
        # path111 = cur_file_dir()
        dlg = wx.FileDialog(
            self, message=u"选择一个文件",
            defaultFile=curFilePath,
            wildcard=wildcard1,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            # paths = dlg.GetPaths()
            paths = dlg.GetPaths()
            temp = paths[0]
            if (len(paths) > 1):
                self.Show_Content("Only open one file each time!")
                return False
            tem = temp.split('.')
            if (tem[-1] != 'txt'):
                self.Show_Content("Only open .txt file!")
                return False
            self.ZDMatrixFile = temp
            self.AddMatrix()
        dlg.Destroy()

    def ImportMatrix(self, evt):
        # 故障矩阵的导入数据功能对话框
        # path111 = cur_file_dir()
        dlg = wx.FileDialog(
            self, message=u"选择一个文件",
            defaultFile=curFilePath,
            wildcard=wildcard1,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            # paths = dlg.GetPaths()
            paths = dlg.GetPaths()
            temp = paths[0]
            if (len(paths) > 1):
                self.Show_Content("Only open one file each time!")
                return False
            tem = temp.split('.')
            if (tem[-1] != 'txt'):
                self.Show_Content("Only open .txt file!")
                return False
            self.MatrixFile = temp
            self.Set_grids(u"成功导入故障矩阵初始文件：" + temp + u"！")
        dlg.Destroy()

    def DXImport(self, evt):
        # 掉线率数据的导入数据功能对话框
        # path111 = cur_file_dir()
        dlg = wx.FileDialog(
            self, message=u"选择一个文件",
            defaultFile=curFilePath,
            wildcard=wildcard1,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            # paths = dlg.GetPaths()
            paths = dlg.GetPaths()
            temp = paths[0]
            if (len(paths) > 1):
                self.Show_Content("Only open one file each time!")
                return False
            tem = temp.split('.')
            if (tem[-1] != 'txt'):
                self.Show_Content("Only open .txt file!")
                return False
            self.DXFile = temp
            self.Show_Content(u"成功导入数据文件：" + temp + u"！")
        dlg.Destroy()

    def DXCompute(self, evt):
        if(self.DXFile == ''):
            self.Show_Content(u"未导入数据，请重新导入！")
        else:
            temp = open(self.DXFile, 'r+').readlines()
            num = 0
            for i in range(500000):
                data = temp[i].split(",")
                diaoxian = (float(data[1]) - float(data[2])) / \
                    (float(data[3]) - float(data[4].rstrip("\n")))
                num += diaoxian
            num /= 500000
            self.Set_grids(u"当前计算文件:" + self.DXFile + "\n\n" +
                           u"前500000行数据掉线率计算结果为:" + str(num))

    def InputBigData(self, evt):
        # 大数据模块的导入数据功能对话框
        # path111 = cur_file_dir()
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultFile=curFilePath,
            wildcard=wildcard1,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            # paths = dlg.GetPaths()
            paths = dlg.GetPaths()
            temp = paths[0]
            if (len(paths) > 1):
                self.Show_Content("Only open one file each time!")
                return False
            tem = temp.split('.')
            if (tem[-1] != 'txt'):
                self.Show_Content("Only open .txt file!")
                return False
            self.BigDataAnalysisFileList.append(temp)
            self.Show_Content(u"已成功导入大数据分析数据集：" + temp)
            # print self.BigDataAnalysisFileList
        dlg.Destroy()

    def InputMData(self, evt):
        # 盲点检测导入数据对话框
        # path111 = cur_file_dir()
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultFile=curFilePath,
            wildcard=wildcard1,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            # paths = dlg.GetPaths()
            paths = dlg.GetPaths()
            temp = paths[0]
            if (len(paths) > 1):
                self.Show_Content("Only open one file each time!")
                return False
            tem = temp.split('.')
            if (tem[-1] != 'txt'):
                self.Show_Content("Only open .txt file!")
                return False
            self.MDataAnalysisFileList.append(temp)
            self.Show_Content(u"已成功导入盲点检测数据集：" + temp)
        dlg.Destroy()

    def InputUserData(self, evt):
        # 用户预测导入数据对话框
        # path111 = cur_file_dir()
        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultFile=curFilePath,
            wildcard=wildcard1,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            # paths = dlg.GetPaths()
            paths = dlg.GetPaths()
            temp = paths[0]
            if (len(paths) > 1):
                self.Show_Content("Only open one file each time!")
                return False
            tem = temp.split('.')
            # print tem
            if (tem[-1] != 'txt'):
                self.Show_Content("Only open .txt file!")
                return False
            self.PDataAnalysisFileList.append(temp)
            self.Show_Content(u"已成功导入用户预测数据集：" + temp)
            # print self.PDataAnalysisFileList
        dlg.Destroy()

    def DataProcess(self, evt):
        # 大数据模块的数据操作对话框，设置进行操作的类型
        ds = DataProcessDialog(self)
        ds.Show()

    def ComputingSetting(self, operationNum):
        # 未知功能，待注释,估计是数据操作设置
        self.ComputingSet = operationNum
        # print self.ComputingSet

    def ShowData(self, evt):
        # 打开大数据模块的显示数据对话框
        ds = BigDataShowDialog(self)
        ds.Show()

    def ShowGrid(self, filePath, colNum):
        # 大数据模块的显示数据对话框的返回值来进行调用相应的线程
        '''
        show content according to DataShowDialog
        filePath: file path to read
        colNum: lines to show
        '''
        self.filePath = filePath
        self.colNum = colNum
        # 实例化导入数据对象
        OpenFile(self.filePath, self.colNum, self)

    def Computing(self, evt):
        # 大数据计算接口，根据选择的方法，来进行对应的计算
        try:
            self.selected = self.choices3.GetSelection()
            # print type(self.selected)
            # print self.selected
            if(self.selected == 0):
                Computing(self.filePath, self.colNum, 0, self)
            elif(self.selected == 1):
                Computing(self.filePath, self.colNum, 1, self)
            else:
                self.Show_Content("Error!", 1)
        except:
            self.Show_Content("Error!", 1)

    def ShowMData(self, evt):
        # 打开盲点检测的显示数据对话框
        ds = MDataShowDialog(self)
        ds.Show()

    def ShowMPot(self, MfilePath, McolNum):
        # 盲点检测显示数据对话框返回后进行此操作
        # 用户预测模块复用此功能进行显示数据子线程
        '''
            show content according to MDataShowDialog
            MfilePath: Mfile path to read
        '''
        self.MfilePath = MfilePath
        self.McolNum = McolNum
        # 实例化导入数据对象
        OpenFile(self.MfilePath, self.McolNum, self)

    def ScreenData(self, evt):
        self.P3abox.Show(self.grids)
        self.P3abox.Hide(self.datapanel)
        self.wbox.Layout()
        # 异常数据筛选
        Screen(self.MfilePath, self)

    def BlindspotMonitor(self, evt):
        # 应用1盲点检测盲点检测按钮事件,打开盲点检测对话框进行关联指标设置
        self.MNum = 0
        md = MDataDetect(self)
        md.Show()

    def BlindspotDetect(self):
        # 应用1盲点检测关联指标设置完毕后进行盲点检测子线程
        Detect(self.MfilePath, self)

    def Judging(self, a, b0, b1):  # 判断二元点a是否在以b0为左上顶点，b1为右下顶点的矩形之内
        if(a.x >= b0[0] and a.x <= b1[0] and a.y >= b0[1] and a.y <= b1[1]):
            return True
        return False

    def OnLeftDown(self, event):
        # 获取鼠标位置
        # print "Down"
        self.pos = event.GetPosition()
        # print self.pos
        if self.Judging(self.pos, (171, 210), (210, 237)):
            self.posCtrl_1.SetLabel("%f, %f" % (30.518514, 114.413668))
            self.posCtrl_n.SetLabel(u"1--船池附近")
        elif self.Judging(self.pos, (51, 329), (86, 352)):
            self.posCtrl_1.SetLabel("%f, %f" % (30.514974, 114.413053))
            self.posCtrl_n.SetLabel(u"2--华科附幼附近")
        elif self.Judging(self.pos, (47, 488), (91, 520)):
            self.posCtrl_1.SetLabel("%f, %f" % (30.513419, 114.410407))
            self.posCtrl_n.SetLabel(u"3--东七附近")
        elif self.Judging(self.pos, (131, 360), (174, 391)):
            self.posCtrl_1.SetLabel("%f, %f" % (30.516379, 114.410371))
            self.posCtrl_n.SetLabel(u"4--集贤楼附近")
        elif self.Judging(self.pos, (227, 378), (273, 404)):
            self.posCtrl_1.SetLabel("%f, %f" % (30.515482, 114.415212))
            self.posCtrl_n.SetLabel(u"5--东三区")
        elif self.Judging(self.pos, (401, 238), (443, 261)):
            self.posCtrl_1.SetLabel("%f, %f" % (30.51807, 114.419718))
            self.posCtrl_n.SetLabel(u"6--喻园23/24栋")
        elif self.Judging(self.pos, (646, 386), (684, 412)):
            self.posCtrl_1.SetLabel("%f, %f" % (30.515331, 114.426141))
            self.posCtrl_n.SetLabel(u"7--韵苑足球场")
        elif self.Judging(self.pos, (734, 296), (783, 326)):
            self.posCtrl_1.SetLabel("%f, %f" % (30.416923, 114.428664))
            self.posCtrl_n.SetLabel(u"8--韵苑20栋附近")
        elif self.Judging(self.pos, (220, 419), (253, 443)):
            self.posCtrl_1.SetLabel("%f, %f" % (30.51574, 114.412668))
            self.posCtrl_n.SetLabel(u"9--东五附近")
        else:
            # self.posCtrl_1.SetLabel("%f, %f" % (30.51574, 114.412668))
            print self.posCtrl_n.SetLabel(u"未知区域")
        # self.posCtrl_1.SetLabel("%d, %d" % (self.pos.x, self.pos.y))

    def OnLeftUp(self, evt):
        pass

    def OnLeftDownMUP(self, event):
        self.pos = event.GetPosition()
        if (self.Judging(self.pos, (628, 287), (872, 410))):
            self.Show_Content(u"已选择区域：华中科技大学。", 0)
        else:
            self.Show_Content(u"已选择区域：未知区域", 0)

    def OnLeftDownUP(self, event):
        self.c4 = -1
        self.pos = event.GetPosition()
        print self.pos
        if(self.Judging(self.pos, (628, 287), (872, 410)) and not self.UPflag):
            # path111 = cur_file_dir()
            jpg = wx.Image(curFilePath + "\\" + "map\\map2.jpg",
                           wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
            self.SSB = wx.StaticBitmap(self.Panel3, -1, jpg, style=wx.CENTER)
            self.List.append(self.SSB)
            self.Show_Content(u"已选择区域：华中科技大学。", 0)
            self.UPflag = 1
        else:
            # self.posCtrl_1.SetLabel("%f, %f" % (30.51574, 114.412668))
            print self.posCtrl_n.SetLabel(u"未知区域")
        if(self.UPflag):
            if(self.Judging(self.pos, (747, 418), (815, 468))):
                self.Show_Content(u"已选择区域：东校区图书馆。", 0)
                self.c4 = 0
            elif(self.Judging(self.pos, (701, 283), (747, 333))):
                self.Show_Content(u"已选择区域：韵苑食堂。", 0)
                self.c4 = 1
            elif(self.Judging(self.pos, (332, 453), (370, 510))):
                self.Show_Content(u"已选择区域：主校区操场。", 0)
                self.c4 = 2
            else:
                self.Show_Content(u"已选择区域：未知区域", 0)
                self.c4 = -1

    def OnMotion(self, event):
        pos = event.GetPosition()
        self.posCtrl_1.SetLabel("%d, %d" % (pos.x, pos.y))
        event.Skip()

    def ResultOutput(self, evt):
        # 应用1盲点检测结果输出按钮事件,显示已经检测好的8张图，包含3个时段，两种图型
        # print self.choices6.GetSelection()
        # print self.choices6_1.GetSelection()
        if(self.choices6.GetSelection() == 3 and self.choices6_1.GetSelection() == 1):
            self.P3abox.Hide(self.grids)
            self.P4abox.Hide(self.bar)
            self.P4abox.Show(self.box_P41)
            self.wbox.Layout()
            # print self.Panel3.GetSize()
            jpg = wx.Image(MDataPicPath[self.choices6.GetSelection()][
                           self.choices6_1.GetSelection()], wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
            self.MSB = wx.StaticBitmap(self.Panel3, -1, jpg)

            # self.MSB.Bind(wx.EVT_MOTION, self.OnMotion)#滑动选项
            self.List.append(self.MSB)
        else:
            self.P3abox.Hide(self.grids)
            self.P4abox.Show(self.bar)
            self.P4abox.Hide(self.box_P41)
            self.wbox.Layout()
            # print self.Panel3.GetSize()
            jpg = wx.Image(MDataPicPath[self.choices6.GetSelection()][
                           self.choices6_1.GetSelection()], wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
            self.MSB = wx.StaticBitmap(self.Panel3, -1, jpg)
            # self.MSB.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
            # self.MSB.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
            # self.MSB.Bind(wx.EVT_MOTION, self.OnMotion)#滑动选项
            self.List.append(self.MSB)
        self.MSB.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.MSB.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)

    def ShowPData(self, evt):
        # 应用2用户预测显示数据对话框
        ds = PDataShowDialog(self)
        ds.Show()

    def MselectUserRegion(self, evt):
        self.P3abox.Hide(self.grids)
        self.P3abox.Hide(self.datapanel)
        # self.P4abox.Hide(self.bar)
        # self.P4abox.Show(self.box_P41)
        self.wbox.Layout()
        # print self.choices4.GetSelection()
        # print self.Panel3.GetSize()
        # path111 = cur_file_dir()
        jpg = wx.Image(curFilePath + "\\" + "map\\map1.jpg",
                       wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.SSB = wx.StaticBitmap(self.Panel3, -1, jpg, style=wx.CENTER)
        self.SSB.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDownMUP)
        self.List.append(self.SSB)

    def selectUserRegion(self, evt):
        self.P3abox.Hide(self.grids)
        self.P3abox.Hide(self.datapanel)
        # self.P4abox.Hide(self.bar)
        # self.P4abox.Show(self.box_P41)
        self.wbox.Layout()
        self.UPflag = 0
        # print self.choices4.GetSelection()
        # print self.Panel3.GetSize()
        jpg = wx.Image(curFilePath + "\\" + "map\\map1.jpg",
                       wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        self.SSB = wx.StaticBitmap(self.Panel3, -1, jpg, style=wx.CENTER)
        self.SSB.Bind(wx.EVT_MOTION, self.OnMotion)
        self.SSB.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDownUP)
        self.List.append(self.SSB)

    def UserPredict(self, evt):
        # 应用2用户预测筛选用户密度预测按钮事件
        '''
        # 使用下拉框选择区域
        if (self.choices4.GetSelection() == -1):
            self.Set_grids(u"未选定区域！")
        else:
            self.P3abox.Hide(self.grids)
            self.wbox.Layout()
            # print self.choices4.GetSelection()
            # print self.Panel3.GetSize()
            jpg = wx.Image(PDataPicPath[self.choices4.GetSelection()][self.choices5.GetSelection()],
                           wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
            self.USB = wx.StaticBitmap(self.Panel3, -1, jpg, style=wx.CENTER)
            self.List.append(self.USB)
            '''
        if (self.c4 == -1):
            self.Set_grids(u"未选定区域！")
        else:
            # self.ClearList()
            self.SSB.DestroyChildren()
            self.P3abox.Hide(self.grids)
            self.wbox.Layout()
            # print self.choices4.GetSelection()
            # print self.Panel3.GetSize()
            jpg = wx.Image(PDataPicPath[self.c4][self.choices5.GetSelection()],
                           wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
            self.USB = wx.StaticBitmap(self.Panel3, -1, jpg, style=wx.CENTER)
            self.List.append(self.USB)

    def RegionSelect(self, evt):
        # 异常信令分析的用户区域选择按钮对应的事件函数
        text = u"当前选择区域： 武汉\n"
        text += u"当前选择时间段： 2016年5月7日14:00-16:00\n"
        text += u"当前小区： 光谷金融港ZLH-1\n"
        self.Set_grids(text)

    def InitMatrix(self, evt):
        self.MatrixName = ['故障名称', '故障指标项', '故障次数', '原因分析', '解决方案推荐']
        self.Matrix = [
            [],  # 存储故障名称
            [],  # 存储故障指标项
            [],  # 存储对应故障次数
            [],  # 存储对应原因分析
            []  # 存储对应解决方案
        ]
        if(self.MatrixFile == ''):
            self.Show_Content(u"未导入故障矩阵初始数据，请重新导入！")
        else:
            fou = open(self.MatrixFile)
            contents = fou.readlines()
            for content in contents:
                temp = content.split(' ')
                if(len(temp) == 5):
                    if(not self.sampleListP.has_key(temp[0])):
                        self.sampleListP[temp[0]] = 1
                    else:
                        self.sampleListP[temp[0]] += 1
                    self.Matrix[0].append(temp[0])
                    self.Matrix[1].append(temp[1])
                    self.Matrix[2].append(temp[2])
                    self.Matrix[3].append(temp[3])
                    self.Matrix[4].append(temp[4])
            # print self.Matrix
            self.choicesP.Set(self.sampleListP.keys())
            self.P2box.Layout()
            # print self.sampleListP
            self.Show_Content(u"初始化矩阵表成功！")
            self.ShowMatrix()

    def AddMatrix(self):
        try:
            fou = open(self.ZDMatrixFile, 'r+')
            contents = fou.readlines()
            for content in contents:
                temp = content.split(' ')
                if (len(temp) == 5):
                    if (not self.sampleListP.has_key(temp[0])):
                        self.sampleListP[temp[0]] = 1
                    else:
                        self.sampleListP[temp[0]] += 1
                    self.Matrix[0].append(temp[0])
                    self.Matrix[1].append(temp[1])
                    self.Matrix[2].append(temp[2])
                    self.Matrix[3].append(temp[3])
                    self.Matrix[4].append(temp[4])
            # print self.Matrix
            self.choicesP.Set(self.sampleListP.keys())
            self.P2box.Layout()
            # print self.sampleListP
            self.Show_Content(u"自动添加矩阵表成功！")
            self.ShowMatrix()
        except:
            self.Show_Content(u"未初始化矩阵表！")

    def HAddMatrix(self, evt):
        try:
            ds = HAddMatrixDialog(self)
            ds.Show()
            self.Show_Content(u"手动添加矩阵表成功！")
            self.ShowMatrix()
        except:
            self.Show_Content(u"未初始化矩阵表！")

    def ShowMatrix(self):
        temp = u"当前矩阵表简况:" + "\n"

        temp += u"共录入" + str(len(self.Matrix[0])) + u"条数据，"

        temp += u"其中录入" + str(len(self.sampleListP.keys())
                              ) + u"种故障，其中每种故障对应数据条数:" + "\n\n"
        for i in self.sampleListP.keys():
            temp += i.decode('gbk') + u":共" + \
                str(self.sampleListP[i]) + u"条数据" + "\n"
        self.Set_grids(temp)

    def ProblemSol(self, evt):
        total = 0
        self.problem = self.choicesP.GetStringSelection()
        self.result = []
        for i in range(len(self.Matrix[0])):
            if(self.Matrix[0][i].decode('gbk') == self.problem):
                # total += int(self.Matrix[2][i])
                self.result.append(self.Matrix[3][i].decode('gbk'))
        # print self.result,1
        self.BeSelected = {}
        ds = ProblemSolDialog(self)
        ds.Show()

    def OnClose(self, evt):
        evt.Skip()
        # # 定义右上角关闭按钮的事件
        # ret = wx.MessageBox(u'确认关闭?', u'关闭', wx.OK | wx.CANCEL)
        # if ret == wx.OK:
        #     # do something here...
        #     evt.Skip()

    def ClearList(self):
        self.P4abox.Show(self.bar)
        self.P4abox.Hide(self.box_P41)
        if(self.List == 0):
            return 1
        else:
            for i in self.List:
                i.Destroy()
            self.List = []
            self.P3abox.Show(self.grids)
            self.P3abox.Hide(self.datapanel)
            self.grids.SetValue(" ")

    def UpdateC2(self, evt):
        # 指标体系模块显示，根据第一个指标类型选择来定义第二个指标名称的选择
        self.choices2.Set(self.sampleList2[self.sampleList1[
                          self.choices1.GetStringSelection()]])
        self.P2box.Layout()

    def UpdateC1(self, evt):
        # 指标体系模块显示，根据第二个指标名称的选择来进行相应的指标详情的显示
        self.Set_grids('')  # 更新指标详情的时候先将输出信息面板清空
        # 定位所选择的具体指标
        a = self.sampleList1[self.choices1.GetStringSelection()]
        if(a == 2):
            self.Lcbox.Hide(self.Hbox)
            self.wbox.Layout()
        else:
            self.Lcbox.Show(self.Hbox)
            self.wbox.Layout()
        b = self.choices2.GetSelection()
        # 找到指标详情中的对应行数
        Ln = 0
        for i in range(a):
            Ln += len(self.sampleList2[i])
        Ln += b
        print Ln
        # 打开指标详情文件
        # path111 = cur_file_dir()
        fou = open(curFilePath + "\\" + u"指标体系\label.txt", 'r+')
        data = fou.readlines()[Ln].split(' ')
        fou.close()
        temp = ''  # 送入输出信息面板显示的指标详情信息
        # 指标名称的显示
        name = data[0].decode("gbk")
        temp += u"指标名称：" + name + "\n\n"
        # 指标名称对应的定义显示
        definition = data[1].decode("gbk")
        temp += u"指标说明：" + definition + "\n\n"
        # 指标名称对应的计算公式
        comput = data[2].decode("gbk")
        temp += u"指标定义与计算：" + comput + "\n\n"
        if(len(data) == 6):
            # 指标细分，划分三种监控区域
            temp += u"按照监控区域细分如下：" + "\n"
            weiyu = data[3].decode("gbk")
            temp += u"微域级：" + weiyu + "\n"
            xiaoqu = data[4].decode("gbk")
            temp += u"小区级：" + xiaoqu + "\n"
            quyu = data[5].decode("gbk")
            temp += u"区域级：" + quyu + "\n"
            # 送入输出信息面板显示
        self.Set_grids(temp)

    def Set_grids(self, con):
        # 设置panel面板多行文本控件显示
        self.grids.SetValue(con)
        self.grids.SetInsertionPoint(0)
        f = wx.Font(18, wx.ROMAN, wx.NORMAL, wx.NORMAL, False)
        self.grids.SetStyle(0, self.grids.GetLastPosition(),
                            wx.TextAttr("black", "white", f))

    def Show_Content(self, con, flag=0):
        # 更新状态栏显示，flag=0表示直接在当前状态栏后面添加文字与时间，flag=1 重置状态栏并设置文字
        if(flag == 0):
            ISOTIMEFORMAT = '%Y-%m-%d %X'
            cc = datetime.datetime.now().strftime(ISOTIMEFORMAT)
            self.bar.SetLabel(con + "\n" + cc)
            # self.bar.AppendText("   " + cc + "\n")
            # f = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL, False)
            # self.bar.SetFont(f)
        else:
            self.bar.SetLabel(con)
            # self.bar.SetInsertionPoint(0)

    def show_time(self):
        # 显示当前时间，调试使用
        ISOTIMEFORMAT = '%Y-%m-%d %X'
        print time.strftime(ISOTIMEFORMAT, time.localtime())
        return time.strftime(ISOTIMEFORMAT, time.localtime())

    def GridsMsg(self, msg, flag=0):
        # 大数据分析模块实时反馈信息并添加时间信息
        ISOTIMEFORMAT = '%Y-%m-%d %X'
        time = datetime.datetime.now()
        if(flag == 1):  # 清空grids并显示msg
            self.grids.SetValue(" ")
            cc = " "
        elif(flag == 2):  # 设置开始时间
            self.BeginTime = time
            self.sTime = self.BeginTime
            cc = self.sTime.strftime(ISOTIMEFORMAT)
            print flag, "  ", cc
        elif(flag == 3):  # 设置结束时间
            self.EndTime = time
            self.sTime = self.EndTime
            cc = self.sTime.strftime(ISOTIMEFORMAT)
            print flag, "  ", cc
        elif(flag == 4):  # 计算时间跨度
            self.time = self.EndTime - self.BeginTime
            self.sTime = self.time
            cc = str(self.sTime)
            print flag, "  ", cc
        else:
            cc = " "
        self.grids.SetValue(self.grids.GetValue() + "\n" + msg + "\n" + cc)
        # self.bar.SetInsertionPoint(0)

    def LogMessage(self, msg):  # 子线程与主窗口状态栏交互接口
        # self.bar.AppendText(msg)
        ISOTIMEFORMAT = '%Y-%m-%d %X'
        cc = datetime.datetime.now().strftime(ISOTIMEFORMAT)
        self.bar.SetLabel(msg + "\n" + cc)
        # self.bar.SetInsertionPoint(0)
        # f = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL, False)
        # self.bar.SetFont(f)


class BigDataShowDialog(wx.Dialog):  # 大数据分析数据显示设置对话框

    def __init__(self, parent):
        super(BigDataShowDialog, self).__init__(
            parent, title=u"大数据分析-数据显示", size=(700, 300))
        self.parent = parent

        # get file list from parent
        self.fileList = parent.BigDataAnalysisFileList

        self.Panel_ds = wx.Panel(self)
        # self.Panel_ds.SetBackgroundColour('Red')

        self.Panel_ds1 = wx.Panel(self)
        # self.Panel_ds1.SetBackgroundColour('Green')

        self.Panel_ds2 = wx.Panel(self)
        # self.Panel_ds2.SetBackgroundColour('Blue')

        self.title = wx.StaticText(
            self.Panel_ds1, -1, u"大数据平台数据显示设置:", style=wx.ALIGN_CENTER)

        self.DataSource = wx.StaticText(
            self.Panel_ds, -1, u"数据源选择:", style=wx.ALIGN_CENTER)
        self.choices = wx.Choice(
            self.Panel_ds, -1, choices=self.fileList, style=wx.ALIGN_CENTER)

        self.datacols = wx.StaticText(
            self.Panel_ds, -1, u"数据行数:", style=wx.ALIGN_CENTER)
        self.DataCols = wx.TextCtrl(self.Panel_ds, -1, r'500000')

        self.SetButton = wx.Button(self.Panel_ds2, label=u'确定')
        self.SetButton.Bind(wx.EVT_BUTTON, self.Set)
        self.exitbutton = wx.Button(self.Panel_ds2, label=u'退出')
        self.exitbutton.Bind(wx.EVT_BUTTON, self.exit_out)
        # boxSizer set*********************************

        self.P1box = wx.BoxSizer()
        self.P1box.Add(self.title, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds1.SetSizer(self.P1box)

        self.P2box = wx.BoxSizer(wx.VERTICAL)
        self.P2box.Add(self.SetButton, proportion=0, flag=wx.ALL, border=10)
        self.P2box.Add(self.exitbutton, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds2.SetSizer(self.P2box)

        self.P221box = wx.BoxSizer()
        self.P221box.Add(self.DataSource, proportion=0, flag=wx.ALL, border=10)
        self.P221box.Add(self.choices, proportion=0, flag=wx.ALL, border=10)
        self.P222box = wx.BoxSizer()
        self.P222box.Add(self.datacols, proportion=0, flag=wx.ALL, border=10)
        self.P222box.Add(self.DataCols, proportion=0, flag=wx.ALL, border=10)

        self.P22box = wx.BoxSizer(wx.VERTICAL)
        self.P22box.Add(self.P221box, proportion=0, flag=wx.ALL, border=10)
        self.P22box.Add(self.P222box, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds.SetSizer(self.P22box)

        self.P3box = wx.BoxSizer()
        self.P3box.Add(self.Panel_ds, proportion=0, flag=wx.ALL, border=10)
        self.P3box.Add(self.Panel_ds2, proportion=0, flag=wx.ALL, border=10)

        self.Pbox = wx.BoxSizer(wx.VERTICAL)
        self.Pbox.Add(self.Panel_ds1, proportion=0, flag=wx.ALL, border=10)
        self.Pbox.Add(self.P3box, proportion=0, flag=wx.ALL, border=10)

        self.SetSizer(self.Pbox)

    def Set(self, evt):
        self.selected = self.choices.GetSelection()
        filePath = self.fileList[self.selected]
        self.Show(False)
        self.parent.ShowGrid(filePath, int(self.DataCols.GetValue()))

    def exit_out(self, event):
        self.Show(False)

    def OnClose(self, evt):
        evt.Skip()


class DataProcessDialog(wx.Dialog):  # 大数据分析模块数据显示处理对话框

    def __init__(self, parent):
        super(DataProcessDialog, self).__init__(
            parent, title=u"大数据分析-数据显示", size=(500, 300))
        self.parent = parent

        self.Panel_ds = wx.Panel(self)
        # self.Panel_ds.SetBackgroundColour('Red')

        self.Panel_ds1 = wx.Panel(self)
        # self.Panel_ds1.SetBackgroundColour('Green')

        self.Panel_ds2 = wx.Panel(self)
        # self.Panel_ds2.SetBackgroundColour('Blue')

        self.typeList = [u'求和', u'累乘', u'掉线率计算', u"业务请求时延", u"加密时延", u"身份识别时延", u"TMSI重分配时延",
                         u"语音寻呼时延", u"剔除UI的无线掉线率", u"阴影效应", u"多普勒效应", u"远近效应", u"用户密度",
                         u"用户密度对通信质量影响", u"低接通用户数劣化指标", u"高掉线用户数劣化指标",
                         u"高流量用户时延劣化指标", u"高信道质量掉线劣化指标", u"高流量用户接通劣化指标",
                         u"高时延用户数劣化指标", u"上行业务质量", u"上行噪声影响", u"上行干扰对弱覆盖的影响",
                         u"下行业务弱覆盖影响"]

        self.title = wx.StaticText(
            self.Panel_ds1, -1, u"大数据平台数据操作设置:", style=wx.ALIGN_CENTER)

        self.DataSource = wx.StaticText(
            self.Panel_ds, -1, u"数据操作类型选择:", style=wx.ALIGN_CENTER)
        self.choices = wx.Choice(
            self.Panel_ds, -1, choices=self.typeList, style=wx.ALIGN_CENTER)

        self.SetButton = wx.Button(self.Panel_ds2, label=u'确定')
        self.SetButton.Bind(wx.EVT_BUTTON, self.Set)
        self.exitbutton = wx.Button(self.Panel_ds2, label=u'退出')
        self.exitbutton.Bind(wx.EVT_BUTTON, self.exit_out)
        # boxSizer set*********************************

        self.P1box = wx.BoxSizer()
        self.P1box.Add(self.title, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds1.SetSizer(self.P1box)

        self.P2box = wx.BoxSizer(wx.VERTICAL)
        self.P2box.Add(self.SetButton, proportion=0, flag=wx.ALL, border=10)
        self.P2box.Add(self.exitbutton, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds2.SetSizer(self.P2box)

        self.P221box = wx.BoxSizer()
        self.P221box.Add(self.DataSource, proportion=0, flag=wx.ALL, border=10)
        self.P221box.Add(self.choices, proportion=0, flag=wx.ALL, border=10)
        self.P222box = wx.BoxSizer()

        self.P22box = wx.BoxSizer(wx.VERTICAL)
        self.P22box.Add(self.P221box, proportion=0, flag=wx.ALL, border=10)
        self.P22box.Add(self.P222box, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds.SetSizer(self.P22box)

        self.P3box = wx.BoxSizer()
        self.P3box.Add(self.Panel_ds, proportion=0, flag=wx.ALL, border=10)
        self.P3box.Add(self.Panel_ds2, proportion=0, flag=wx.ALL, border=10)

        self.Pbox = wx.BoxSizer(wx.VERTICAL)
        self.Pbox.Add(self.Panel_ds1, proportion=0, flag=wx.ALL, border=10)
        self.Pbox.Add(self.P3box, proportion=0, flag=wx.ALL, border=10)

        self.SetSizer(self.Pbox)

    def Set(self, evt):
        self.selected = self.choices.GetSelection()
        self.parent.ComputingSetting(self.typeList[self.selected])
        print self.typeList[self.selected]
        self.parent.bar.SetLabel(
            u"当前选择计算：" + self.typeList[self.selected] + "\n")
        # f = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL, False)
        # self.parent.bar.SetFont(f)
        self.Show(False)

    def exit_out(self, event):
        self.Show(False)

    def OnClose(self, evt):
        evt.Skip()


class MDataShowDialog(wx.Dialog):  # 盲点检测数据显示设置对话框

    def __init__(self, parent):
        super(MDataShowDialog, self).__init__(
            parent, title=u"盲点检测-数据显示", size=(700, 300))
        self.parent = parent

        # get file list from parent
        self.fileList = parent.MDataAnalysisFileList

        self.Panel_ds = wx.Panel(self)
        # self.Panel_ds.SetBackgroundColour('Red')

        self.Panel_ds1 = wx.Panel(self)
        # self.Panel_ds1.SetBackgroundColour('Green')

        self.Panel_ds2 = wx.Panel(self)
        # self.Panel_ds2.SetBackgroundColour('Blue')

        self.title = wx.StaticText(
            self.Panel_ds1, -1, u"盲点检测数据显示设置:", style=wx.ALIGN_CENTER)

        self.DataSource = wx.StaticText(
            self.Panel_ds, -1, u"数据源选择:", style=wx.ALIGN_CENTER)
        self.choices = wx.Choice(
            self.Panel_ds, -1, choices=self.fileList, style=wx.ALIGN_CENTER)
        self.choices.SetMinSize((300, 50))

        self.datacols = wx.StaticText(
            self.Panel_ds, -1, u"数据行数:", style=wx.ALIGN_CENTER)
        self.DataCols = wx.TextCtrl(self.Panel_ds, -1, r'200')

        self.SetButton = wx.Button(self.Panel_ds2, label=u'确定')
        self.SetButton.Bind(wx.EVT_BUTTON, self.Set)
        self.exitbutton = wx.Button(self.Panel_ds2, label=u'退出')
        self.exitbutton.Bind(wx.EVT_BUTTON, self.exit_out)
        # boxSizer set*********************************

        self.P1box = wx.BoxSizer()
        self.P1box.Add(self.title, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds1.SetSizer(self.P1box)

        self.P2box = wx.BoxSizer(wx.VERTICAL)
        self.P2box.Add(self.SetButton, proportion=0, flag=wx.ALL, border=10)
        self.P2box.Add(self.exitbutton, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds2.SetSizer(self.P2box)

        self.P221box = wx.BoxSizer()
        self.P221box.Add(self.DataSource, proportion=0, flag=wx.ALL, border=10)
        self.P221box.Add(self.choices, proportion=0, flag=wx.ALL, border=10)
        self.P222box = wx.BoxSizer()
        self.P222box.Add(self.datacols, proportion=0, flag=wx.ALL, border=10)
        self.P222box.Add(self.DataCols, proportion=0, flag=wx.ALL, border=10)

        self.P22box = wx.BoxSizer(wx.VERTICAL)
        self.P22box.Add(self.P221box, proportion=0, flag=wx.ALL, border=10)
        self.P22box.Add(self.P222box, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds.SetSizer(self.P22box)

        self.P3box = wx.BoxSizer()
        self.P3box.Add(self.Panel_ds, proportion=0, flag=wx.ALL, border=10)
        self.P3box.Add(self.Panel_ds2, proportion=0, flag=wx.ALL, border=10)

        self.Pbox = wx.BoxSizer(wx.VERTICAL)
        self.Pbox.Add(self.Panel_ds1, proportion=0, flag=wx.ALL, border=10)
        self.Pbox.Add(self.P3box, proportion=0, flag=wx.ALL, border=10)

        self.SetSizer(self.Pbox)

    def Set(self, evt):
        self.selected = self.choices.GetSelection()
        filePath = self.fileList[self.selected]
        self.Show(False)
        self.parent.ShowMPot(filePath, int(self.DataCols.GetValue()))

    def exit_out(self, event):
        self.Show(False)

    def OnClose(self, evt):
        evt.Skip()


class MDataDetect(wx.Dialog):  # 盲点检测设置对话框

    def __init__(self, parent):
        super(MDataDetect, self).__init__(
            parent, title=u"盲点检测-盲点检测设置", size=(400, 300))
        self.parent = parent
        self.Num = 0
        # get file list from parent
        self.fileList = parent.BigDataAnalysisFileList

        self.Panel_ds = wx.Panel(self)
        # self.Panel_ds.SetBackgroundColour('Red')

        self.Panel_ds1 = wx.Panel(self)
        # self.Panel_ds1.SetBackgroundColour('Green')

        self.Panel_ds2 = wx.Panel(self)
        # self.Panel_ds2.SetBackgroundColour('Blue')

        self.title = wx.StaticText(
            self.Panel_ds1, -1, u"盲点检测-关联指标设置:", style=wx.ALIGN_CENTER)

        self.Box1 = wx.CheckBox(self.Panel_ds, -1, u"UE发射功率余量")
        self.Box2 = wx.CheckBox(self.Panel_ds, -1, u"上行信噪比")
        self.Box3 = wx.CheckBox(self.Panel_ds, -1, u"SINR")

        self.SetButton = wx.Button(self.Panel_ds2, label=u'确定')
        self.SetButton.Bind(wx.EVT_BUTTON, self.Set)
        self.exitbutton = wx.Button(self.Panel_ds2, label=u'退出')
        self.exitbutton.Bind(wx.EVT_BUTTON, self.exit_out)
        # boxSizer set*********************************

        self.P1box = wx.BoxSizer()
        self.P1box.Add(self.title, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds1.SetSizer(self.P1box)

        self.P2box = wx.BoxSizer(wx.VERTICAL)
        self.P2box.Add(self.SetButton, proportion=0, flag=wx.ALL, border=10)
        self.P2box.Add(self.exitbutton, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds2.SetSizer(self.P2box)

        '''
        self.P221box = wx.BoxSizer()
        self.P221box.Add(self.DataSource, proportion=0, flag=wx.ALL, border=10)
        self.P221box.Add(self.choices, proportion=0, flag=wx.ALL, border=10)
        self.P222box = wx.BoxSizer()
        self.P222box.Add(self.datacols, proportion=0, flag=wx.ALL, border=10)
        self.P222box.Add(self.DataCols, proportion=0, flag=wx.ALL, border=10)
        '''
        self.P22box = wx.BoxSizer(wx.VERTICAL)
        self.P22box.Add(self.Box1, proportion=0, flag=wx.ALL, border=10)
        self.P22box.Add(self.Box2, proportion=0, flag=wx.ALL, border=10)
        self.P22box.Add(self.Box3, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds.SetSizer(self.P22box)

        self.P3box = wx.BoxSizer()
        self.P3box.Add(self.Panel_ds, proportion=0, flag=wx.ALL, border=10)
        self.P3box.Add(self.Panel_ds2, proportion=0, flag=wx.ALL, border=10)

        self.Pbox = wx.BoxSizer(wx.VERTICAL)
        self.Pbox.Add(self.Panel_ds1, proportion=0, flag=wx.ALL, border=10)
        self.Pbox.Add(self.P3box, proportion=0, flag=wx.ALL, border=10)

        self.SetSizer(self.Pbox)

    def Set(self, evt):
        if(self.Box1.GetValue()):
            self.parent.MNum += 1
        if (self.Box2.GetValue()):
            self.parent.MNum += 1
        if (self.Box3.GetValue()):
            self.parent.MNum += 1
        print self.parent.MNum
        self.Show(False)
        self.parent.BlindspotDetect()

    def exit_out(self, event):
        self.Show(False)

    def OnClose(self, evt):
        evt.Skip()


class PDataShowDialog(wx.Dialog):  # 用户预测数据显示设置对话框

    def __init__(self, parent):
        super(PDataShowDialog, self).__init__(
            parent, title=u"用户预测-数据显示", size=(700, 300))
        self.parent = parent

        # get file list from parent
        self.fileList = parent.PDataAnalysisFileList

        self.Panel_ds = wx.Panel(self)
        # self.Panel_ds.SetBackgroundColour('Red')

        self.Panel_ds1 = wx.Panel(self)
        # self.Panel_ds1.SetBackgroundColour('Green')

        self.Panel_ds2 = wx.Panel(self)
        # self.Panel_ds2.SetBackgroundColour('Blue')

        self.title = wx.StaticText(
            self.Panel_ds1, -1, u"用户预测数据显示设置:", style=wx.ALIGN_CENTER)

        self.DataSource = wx.StaticText(
            self.Panel_ds, -1, u"数据源选择:", style=wx.ALIGN_CENTER)
        self.choices = wx.Choice(
            self.Panel_ds, -1, choices=self.fileList, style=wx.ALIGN_CENTER)
        self.choices.SetMaxSize((300, 50))

        self.datacols = wx.StaticText(
            self.Panel_ds, -1, u"数据行数:", style=wx.ALIGN_CENTER)
        self.DataCols = wx.TextCtrl(self.Panel_ds, -1, r'200')

        self.SetButton = wx.Button(self.Panel_ds2, label=u'确定')
        self.SetButton.Bind(wx.EVT_BUTTON, self.Set)
        self.exitbutton = wx.Button(self.Panel_ds2, label=u'退出')
        self.exitbutton.Bind(wx.EVT_BUTTON, self.exit_out)
        # boxSizer set*********************************

        self.P1box = wx.BoxSizer()
        self.P1box.Add(self.title, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds1.SetSizer(self.P1box)

        self.P2box = wx.BoxSizer(wx.VERTICAL)
        self.P2box.Add(self.SetButton, proportion=0, flag=wx.ALL, border=10)
        self.P2box.Add(self.exitbutton, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds2.SetSizer(self.P2box)

        self.P221box = wx.BoxSizer()
        self.P221box.Add(self.DataSource, proportion=0, flag=wx.ALL, border=10)
        self.P221box.Add(self.choices, proportion=0, flag=wx.ALL, border=10)
        self.P222box = wx.BoxSizer()
        self.P222box.Add(self.datacols, proportion=0, flag=wx.ALL, border=10)
        self.P222box.Add(self.DataCols, proportion=0, flag=wx.ALL, border=10)

        self.P22box = wx.BoxSizer(wx.VERTICAL)
        self.P22box.Add(self.P221box, proportion=0, flag=wx.ALL, border=10)
        self.P22box.Add(self.P222box, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds.SetSizer(self.P22box)

        self.P3box = wx.BoxSizer()
        self.P3box.Add(self.Panel_ds, proportion=0, flag=wx.ALL, border=10)
        self.P3box.Add(self.Panel_ds2, proportion=0, flag=wx.ALL, border=10)

        self.Pbox = wx.BoxSizer(wx.VERTICAL)
        self.Pbox.Add(self.Panel_ds1, proportion=0, flag=wx.ALL, border=10)
        self.Pbox.Add(self.P3box, proportion=0, flag=wx.ALL, border=10)

        self.SetSizer(self.Pbox)

    def Set(self, evt):
        # 复用盲点检测中的显示数据子线程
        self.selected = self.choices.GetSelection()
        filePath = self.fileList[self.selected]
        self.Show(False)
        self.parent.ShowMPot(filePath, int(self.DataCols.GetValue()))

    def exit_out(self, event):
        self.Show(False)

    def OnClose(self, evt):
        evt.Skip()


class HAddMatrixDialog(wx.Dialog):  # 手动扩充矩阵表对话框

    def __init__(self, parent):
        super(HAddMatrixDialog, self).__init__(
            parent, title=u"矩阵表-手动扩充对话框", size=(700, 300))
        self.parent = parent

        self.Panel_ds = wx.Panel(self)
        # self.Panel_ds.SetBackgroundColour('Red')

        self.Panel_ds1 = wx.Panel(self)
        # self.Panel_ds1.SetBackgroundColour('Green')

        self.Panel_ds2 = wx.Panel(self)
        # self.Panel_ds2.SetBackgroundColour('Blue')

        self.title = wx.StaticText(
            self.Panel_ds1, -1, u"矩阵表-手动扩充:", style=wx.ALIGN_CENTER)

        self.Problem = wx.StaticText(
            self.Panel_ds, -1, u"故障名称:", style=wx.ALIGN_CENTER)
        self.ProblemT = wx.TextCtrl(self.Panel_ds, -1, u'RRC接入失败')
        self.P2 = wx.StaticText(
            self.Panel_ds, -1, u"故障关联指标项:", style=wx.ALIGN_CENTER)
        self.P2TC = wx.TextCtrl(
            self.Panel_ds, -1, u'流控导致的发送RRC Connection Reject消息次数')
        self.P3 = wx.StaticText(
            self.Panel_ds, -1, u"故障关联指标项计数:", style=wx.ALIGN_CENTER)
        self.P3TC = wx.TextCtrl(self.Panel_ds, -1, r'5')
        self.P4 = wx.StaticText(
            self.Panel_ds, -1, u"诊断问题:", style=wx.ALIGN_CENTER)
        self.P4TC = wx.TextCtrl(self.Panel_ds, -1, u'流控设置问题或CP负荷过高')
        self.P5 = wx.StaticText(
            self.Panel_ds, -1, u"解决方案:", style=wx.ALIGN_CENTER)
        self.P5TC = wx.TextCtrl(self.Panel_ds, -1, u'检查流控设置，或考虑板卡扩容/升级')

        self.SetButton = wx.Button(self.Panel_ds2, label=u'确定')
        self.SetButton.Bind(wx.EVT_BUTTON, self.Set)
        self.exitbutton = wx.Button(self.Panel_ds2, label=u'退出')
        self.exitbutton.Bind(wx.EVT_BUTTON, self.exit_out)
        # boxSizer set*********************************

        self.P1box = wx.BoxSizer()
        self.P1box.Add(self.title, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds1.SetSizer(self.P1box)

        self.P2box = wx.BoxSizer(wx.VERTICAL)
        self.P2box.Add(self.SetButton, proportion=0, flag=wx.ALL, border=10)
        self.P2box.Add(self.exitbutton, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds2.SetSizer(self.P2box)

        self.P221box = wx.BoxSizer()
        self.P221box.Add(self.Problem, proportion=0, flag=wx.ALL, border=0)
        self.P221box.Add(self.ProblemT, proportion=0, flag=wx.ALL, border=0)
        self.P222box = wx.BoxSizer()
        self.P222box.Add(self.P2, proportion=2, flag=wx.ALL, border=0)
        self.P222box.Add(self.P2TC, proportion=11,
                         flag=wx.ALL | wx.EXPAND, border=0)
        self.P223box = wx.BoxSizer()
        self.P223box.Add(self.P3, proportion=0, flag=wx.ALL, border=0)
        self.P223box.Add(self.P3TC, proportion=0, flag=wx.ALL, border=0)
        self.P224box = wx.BoxSizer()
        self.P224box.Add(self.P4, proportion=2, flag=wx.ALL, border=0)
        self.P224box.Add(self.P4TC, proportion=14, flag=wx.ALL, border=0)
        self.P225box = wx.BoxSizer()
        self.P225box.Add(self.P5, proportion=2, flag=wx.ALL, border=0)
        self.P225box.Add(self.P5TC, proportion=14, flag=wx.ALL, border=0)

        self.P22box = wx.BoxSizer(wx.VERTICAL)
        self.P22box.Add(self.P221box, proportion=0, flag=wx.ALL, border=2)
        self.P22box.Add(self.P222box, proportion=0, flag=wx.ALL, border=2)
        self.P22box.Add(self.P223box, proportion=0, flag=wx.ALL, border=2)
        self.P22box.Add(self.P224box, proportion=0, flag=wx.ALL, border=2)
        self.P22box.Add(self.P225box, proportion=0, flag=wx.ALL, border=2)
        self.Panel_ds.SetSizer(self.P22box)

        self.P3box = wx.BoxSizer()
        self.P3box.Add(self.Panel_ds, proportion=5,
                       flag=wx.ALL | wx.EXPAND, border=10)
        self.P3box.Add(self.Panel_ds2, proportion=1, flag=wx.ALL, border=10)

        self.Pbox = wx.BoxSizer(wx.VERTICAL)
        self.Pbox.Add(self.Panel_ds1, proportion=0, flag=wx.ALL, border=10)
        self.Pbox.Add(self.P3box, proportion=0, flag=wx.ALL, border=10)

        self.SetSizer(self.Pbox)

    def Set(self, evt):
        try:
            pro = self.ProblemT.GetValue().encode('gbk')
            print pro
            self.parent.Matrix[0].append(pro)
            self.parent.Matrix[1].append(self.P2TC.GetValue().encode('gbk'))
            self.parent.Matrix[2].append(self.P3TC.GetValue())
            self.parent.Matrix[3].append(self.P4TC.GetValue().encode('gbk'))
            self.parent.Matrix[4].append(self.P5TC.GetValue().encode('gbk'))
            if (not self.parent.sampleListP.has_key(pro)):
                self.parent.sampleListP[pro] = 1
            else:
                self.parent.sampleListP[pro] += 1
            self.Show(False)
        except:
            self.parent.Set_grids(u"手动添加失败，未初始化矩阵表！")
            self.Show(False)

    def exit_out(self, event):
        self.Show(False)

    def OnClose(self, evt):
        evt.Skip()


class ProblemSolDialog(wx.Dialog):  # 问题诊断设置对话框

    def __init__(self, parent):
        super(ProblemSolDialog, self).__init__(
            parent, title=u"异常信令事件分析-问题诊断", size=(500, 300))
        self.parent = parent

        # get file list from parent
        self.result = parent.result
        print self.result
        self.Panel_ds = wx.Panel(self)
        # self.Panel_ds.SetBackgroundColour('Red')

        self.Panel_ds1 = wx.Panel(self)
        # self.Panel_ds1.SetBackgroundColour('Green')

        self.Panel_ds2 = wx.Panel(self)
        # self.Panel_ds2.SetBackgroundColour('Blue')

        self.title = wx.StaticText(
            self.Panel_ds1, -1, u"问题诊断设置:", style=wx.ALIGN_CENTER)

        self.CBox = []
        for key in self.result:
            self.CBox.append(wx.CheckBox(self.Panel_ds, -1, key))
        f = wx.Font(15, wx.ROMAN, wx.NORMAL, wx.NORMAL, False)

        self.SetButton = wx.Button(self.Panel_ds2, label=u'确定')
        self.SetButton.Bind(wx.EVT_BUTTON, self.Set)
        self.exitbutton = wx.Button(self.Panel_ds2, label=u'退出')
        self.exitbutton.Bind(wx.EVT_BUTTON, self.exit_out)
        # boxSizer set*********************************

        self.P1box = wx.BoxSizer()
        self.P1box.Add(self.title, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds1.SetSizer(self.P1box)

        self.P2box = wx.BoxSizer(wx.VERTICAL)
        self.P2box.Add(self.SetButton, proportion=0, flag=wx.ALL, border=10)
        self.P2box.Add(self.exitbutton, proportion=0, flag=wx.ALL, border=10)
        self.Panel_ds2.SetSizer(self.P2box)

        self.P22box = wx.BoxSizer(wx.VERTICAL)
        for temp in self.CBox:
            temp.SetFont(f)
            self.P22box.Add(temp, proportion=0, flag=wx.TOP, border=10)
        self.Panel_ds.SetSizer(self.P22box)

        self.P3box = wx.BoxSizer()
        self.P3box.Add(self.Panel_ds, proportion=3, flag=wx.ALL, border=10)
        self.P3box.Add(self.Panel_ds2, proportion=1, flag=wx.ALL, border=10)

        self.Pbox = wx.BoxSizer(wx.VERTICAL)
        self.Pbox.Add(self.Panel_ds1, proportion=0, flag=wx.ALL, border=10)
        self.Pbox.Add(self.P3box, proportion=0, flag=wx.ALL, border=10)

        self.SetSizer(self.Pbox)

    def Set(self, evt):
        # 设置需要分析的原因,并根据选择来进行计算诊断结果
        total = 0
        temp = ''
        mmm = self.parent.BeSelected
        for tttt in self.CBox:
            if(tttt.IsChecked()):
                mmm[tttt.GetLabel()] = 0
        # print mmm
        # print mmm.keys(), 2
        for i in range(len(self.parent.Matrix[0])):
            if (mmm.has_key(self.parent.Matrix[3][i].decode('gbk'))):
                total += int(self.parent.Matrix[2][i])
        # print total, 3
        temp = u"当前诊断问题为：" + self.parent.problem + "\n\n" + u"分析矩阵得出如下结果：" + "\n"
        for i in range(len(self.parent.Matrix[0])):
            if (mmm.has_key(self.parent.Matrix[3][i].decode('gbk'))):
                temp += u"原因：" + self.parent.Matrix[3][i].decode('gbk') + u"   概率:" + str(
                    100 * float(self.parent.Matrix[2][i]) / float(total)) + "%\n"
                temp += u"解决方案推荐：" + \
                    self.parent.Matrix[4][i].decode('gbk') + "\n"
        self.parent.Set_grids(temp)
        self.Show(False)

    def exit_out(self, event):
        self.Show(False)

    def OnClose(self, evt):
        evt.Skip()


class log(wx.Frame):  # 登陆界面，调试时进行隐藏

    def __init__(self):
        wx.Frame.__init__(self, None, -1,
                          title=u"登陆",
                          size=(1024, 597),
                          style=wx.DEFAULT_FRAME_STYLE)
        self.Centre()
        self.SetMaxSize((1024, 597))
        self.SetMinSize((1024, 597))
        self.Panel1 = wx.Panel(self)
        self.Panel1.SetBackgroundColour('#1E90FF')
        # self.Panel1.SetTransparent(1)  # 设置透明
        self.Panel2 = wx.Panel(self)
        self.Panel2.SetBackgroundColour('#FFFFFF')

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        account = wx.StaticText(self.Panel2, -1, u"用户名:")
        password = wx.StaticText(self.Panel2, -1, u"密码:")

        self.Act = wx.TextCtrl(self.Panel2, -1, "admin")
        self.paw = wx.TextCtrl(self.Panel2, -1, "12345", style=wx.TE_PASSWORD)

        log_inbutton = wx.Button(self.Panel2, label=u'登陆')
        log_inbutton.Bind(wx.EVT_BUTTON, self.log_in)

        exitbutton = wx.Button(self.Panel2, label=u'退出')
        exitbutton.Bind(wx.EVT_BUTTON, self.exit_out)

        hbox = wx.BoxSizer()
        hbox.Add(account, proportion=0, flag=wx.ALL, border=10)
        hbox.Add(self.Act, proportion=0, flag=wx.ALL, border=6)
        hbox.Add(password, proportion=0, flag=wx.ALL, border=10)
        hbox.Add(self.paw, proportion=0, flag=wx.ALL, border=6)
        hbox.Add(log_inbutton, proportion=0, flag=wx.ALL, border=5)
        hbox.Add(exitbutton, proportion=0, flag=wx.ALL, border=5)
        # vbox = wx.BoxSizer(wx.VERTICAL)
        # vbox.Add(hbox, proportion=0, flag=wx.EXPAND|wx.ALL, border=10)
        # vbox.Add(contents, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.BOTTOM|wx.RIGHT, border=10)
        self.vbox = wx.BoxSizer()
        self.vbox.Add(hbox, proportion=0, flag=wx.LEFT, border=230)
        self.xbox = wx.BoxSizer()
        self.xbox.Add(self.vbox, proportion=0, flag=wx.BOTTOM, border=50)
        self.Panel2.SetSizer(self.xbox)

        self.tbox = wx.BoxSizer(wx.VERTICAL)
        self.tbox.Add(self.Panel1, proportion=10, flag=wx.ALL, border=0)
        self.tbox.Add(self.Panel2, proportion=1, flag=wx.ALL, border=10)

        self.SetSizer(self.tbox)

    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        bmp = wx.Bitmap("start.jpg")
        dc.DrawBitmap(bmp, 0, 0)

    def log_in(self, event):
        if self.Act.GetValue() == 'admin' and self.paw.GetValue() == "12345":
            self.Show(False)
            now = Demo()
            now.Show()
        else:
            error_now = error()
            error_now.Show()

    def exit_out(self, event):
        self.Show(False)

    def OnClose(self, evt):
        evt.Skip()


class error(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1,
                          title="error",
                          size=(300, 200),
                          style=wx.DEFAULT_FRAME_STYLE)
        b = wx.Button(self, -1, u"登陆信息有误！\n请重新输入！", (50, 50))
        self.Bind(wx.EVT_BUTTON, self.OnButton, b)

    def OnButton(self, event):
        self.Show(False)


class MySplashScreen(wx.SplashScreen):
    """
    Create a splash screen widget, make our startup UI layout.
    欢迎界面
    """

    def __init__(self, parent=None):
        # This is a recipe to a the screen.
        # Modify the following variables as necessary.
        aBitmap = wx.Image(name="start.jpg").ConvertToBitmap()
        splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
        splashDuration = 2000  # 欢迎界面停留时间，之后转到登陆界面
        # milliseconds to control the startup UI show time
        # Call the constructor with the above arguments in exactly the
        # following order.
        wx.SplashScreen.__init__(self, aBitmap, splashStyle,
                                 splashDuration, parent)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        wx.Yield()
#----------------------------------------------------------------------#

    def OnExit(self, evt):
        self.Hide()
        # MyFrame is the main frame.
        MyFrame = log()
        MyFrame.Show(True)
        # The program will freeze without this line.
        evt.Skip()  # Make sure the default handler runs too...
#----------------------------------------------------------------------#

# 打印时间


def show_time():
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    print time.strftime(ISOTIMEFORMAT, time.localtime())
app = wx.App()
# frame = MySplashScreen()#欢迎界面，调试时可注释
frame = log()  # 调试时跳过登陆界面
# frame = Demo()
frame.Show()

app.MainLoop()
