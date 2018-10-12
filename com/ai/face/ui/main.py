#!/usr/bin/python
# -*- coding: UTF-8 -*-
import wx
import cv2
import os
import pymysql
import configparser
from face_collect import Collect
import threading
collect = Collect()
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml");
color = (0, 255, 0)
config = configparser.ConfigParser()
config.read("config.ini")
save_path = config.get("img_save", "save_path")
class Main(wx.Frame):

    def __init__(self, parent, title):
        super(Main, self).__init__(parent, title=title)

        self.InitUI()
        self.Centre()
        self.SetMaxClientSize(wx.Size(578, 525))
        self.SetMinClientSize(wx.Size(578, 525))
        self.Show()

    def InitUI(self):
        self.panel = wx.Panel(self)
        self.panel.SetMaxSize(wx.Size(578, 525))
        self.panel.SetMinSize(wx.Size(578, 525))
        self.sizer = wx.GridBagSizer(0, 0)

        self.noticeLabel = wx.StaticText(self.panel, label="**注意事项：\n"
                                                      "\t1、确保摄像头进行采集的时候，只有1张人脸\n"
                                                      "\t2、请先填写员工工号，用作照片的名称")
        self.noticeLabel.SetFont(wx.Font(12, wx.ROMAN, wx.ITALIC, wx.NORMAL))
        self.noticeLabel.SetForegroundColour((255, 0, 0))
        self.sizer.Add(self.noticeLabel, pos=(0, 0), span=(1, 15), flag=wx.EXPAND | wx.ALL, border=5)

        text1 = wx.StaticText(self.panel, label="输入员工编号：")
        self.sizer.Add(text1, pos=(2, 0), flag=wx.ALL, border=5)
        self.num = wx.TextCtrl(self.panel)
        self.sizer.Add(self.num, pos=(2, 1), span=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)

        text2 = wx.StaticText(self.panel, label="人脸图像采集：")
        self.sizer.Add(text2, pos=(3, 0), flag=wx.EXPAND | wx.ALL, border=5)
        openCamera = wx.Button(self.panel, label="打开摄像头")
        openCamera.Bind(wx.EVT_BUTTON, self.openCamera)
        self.sizer.Add(openCamera, pos=(3, 1), flag=wx.ALL, border=5)

        text4 = wx.StaticText(self.panel, label="采集结果：", style=wx.LC_ALIGN_LEFT)
        self.sizer.Add(text4, pos=(4, 0), flag=wx.ALL, border=5)
        self.face = wx.Image("default.jpg", wx.BITMAP_TYPE_ANY).Scale(309, 309)
        self.bmp = wx.StaticBitmap(self.panel, -1, wx.Bitmap(self.face))
        self.sizer.Add(self.bmp, pos=(4, 1), span=(1, 3), flag=wx.EXPAND | wx.ALL, border=5)

        self.buttonSure = wx.Button(self.panel, label="脸像确定")
        self.buttonSure.Bind(wx.EVT_BUTTON, self.sure)

        self.buttonSave = wx.Button(self.panel, label="保存")
        self.buttonSave.Bind(wx.EVT_BUTTON, self.saveToDb)

        self.sizer.Add(self.buttonSure, pos=(5, 1), flag=wx.ALL, border=5)
        self.sizer.Add(self.buttonSave, pos=(5, 2), flag=wx.ALL, border=5)

        self.panel.SetSizerAndFit(self.sizer)
    def openCamera(self, event):
        threading.Thread(target=self.getFace(event), name="videoThread").start()
    def getFace(self, event):
        self.employeeNo = self.num.GetValue()
        if "" == self.employeeNo:
            wx.MessageBox("请先输入工号!")
            return
        '''
            弹出摄像头后，其他按钮不能点击，文本框不能编辑 
       '''
        self.cap = cv2.VideoCapture(0)
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rect = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=9,
                                                 minSize=(50, 50), flags=cv2.CASCADE_SCALE_IMAGE)
            if len(rect) == 1:
                for x, y, w, h in rect:
                    self.detImg = frame[y:y + h, x:x + w]
                    cv2.rectangle(frame, (x - 10, y - 10), (x + w + 10, y + h + 10), color, 3)
            cv2.imshow("Esc exit", frame)
            key = cv2.waitKey(1)
            if key & 0xff == ord('q') or key == 27:
                break
        self.cap.release()
        cv2.destroyAllWindows()

        event.Skip()

    def sure(self, event):
        if hasattr(self, "detImg") is False:
            wx.MessageBox("您尚未打开摄像头！")
            return
        # 图片存储
        cv2.imwrite(save_path + os.sep + '%s.jpg' % self.employeeNo, self.detImg)
        self.cap.release()
        '''
        人脸采集完毕后，展示给客户端
        '''
        pic = wx.Image(save_path + os.sep + "%s.jpg" % self.employeeNo, wx.BITMAP_TYPE_ANY).Scale(309, 309)
        self.bmp.SetBitmap(pic.ConvertToBitmap())
        self.sizer.Fit(self)
        self.panel.Refresh()
    '''
    将员工编号，特征值保存到数据库
    '''
    def saveToDb(self, event):
        if hasattr(self, "detImg") is False:
            wx.MessageBox("请打开摄像头，进行面部识别！")
            return
        _128 = collect.collect(self.detImg)
        if _128 is None:
            wx.MessageBox("尚未识别到人脸！")
            return
        host = config.get("db", "host")
        port = config.get("db", "port")
        user = config.get("db", "user")
        password = config.get("db", "password")
        db = config.get("db", "db")
        dbdialect = config.get("db", "dbdialect")
        try:
            connection = self.getConnection(dbdialect, host, port, user, password, db)
        except:
            wx.MessageBox("连接数据库失败！")
            return
        try:
            with connection.cursor() as cursor:
                findByNo = "select id from t_face_descriptor where employeeNo='" + self.employeeNo +"'"
                cursor.execute(findByNo)
                result = cursor.fetchone()
                if result is not None:
                    updateSql = "update t_face_descriptor set face_descriptor='" + _128 + "'"
                    cursor.execute(updateSql)
                else:
                    insertSql = "insert into t_face_descriptor(employeeNo, face_descriptor) values('" + self.employeeNo + "','" + _128 +"')"
                    cursor.execute(insertSql)
                connection.commit()
                wx.MessageBox("保存成功!")
        except:
            wx.MessageBox("保存失败！")
        finally:
            connection.close()
        event.Skip()
    def getConnection(self, dbdialect, host, port, user, password, db):
        if "mysql" == dbdialect:
            return pymysql.connect(host=host, port=int(port), user=user, password=password, db=db, charset="utf8mb4",
                                   cursorclass=pymysql.cursors.DictCursor)


app = wx.App()
Main(None, title='员工人脸图像采集')
app.MainLoop()