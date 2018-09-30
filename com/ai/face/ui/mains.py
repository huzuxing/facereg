import wx
import cv2
import time
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml");
color = (0, 255, 0)
class Main(wx.Frame):
    def __init__(self, parent):
        super(Main, self).__init__(parent)
        self.initUI()
    def initUI(self):
        pannel = MyPanel(self)
        self.Bind(wx.EVT_BUTTON, self.OnButtonClicked)
        self.Bind(wx.EVT_BUTTON, self.OnButtonClicked)
        self.SetTitle('员工人脸采集')
        self.SetClientSize(800, 600)
        self.Centre()
        self.Show(True)
    def OnButtonClicked(self, e):
        print('click event received by frame class')
        e.Skip()
class MyPanel(wx.Panel):
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)
        self.label = wx.StaticText(self, label="输入员工工号：", pos=(100, 100))
        self.text = wx.TextCtrl(self, pos=(200, 100));
        self.button = wx.Button(self, label="人脸采集", pos=(200, 200))
        self.face = wx.Image("E:\\python\\face\\15381926990.jpg", wx.BITMAP_TYPE_ANY).Scale(350, 300)
        self.bmp = wx.StaticBitmap(self, -1, wx.Bitmap(self.face))
        self.button.Bind(wx.EVT_BUTTON, self.getEmployeeNo)
        self.Bind(wx.EVT_BUTTON, self.OnButtonClicked)
    def OnButtonClicked(self, e):
        print('Panel received click event. propagated to Frame class')
        e.Skip()
    def getEmployeeNo(self, e):
        cap = cv2.VideoCapture(0)
        cap.set(3, 480)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rect = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=9,
                                                 minSize=(50, 50), flags=cv2.CASCADE_SCALE_IMAGE)
            if len(rect) == 1:
                for x, y, w, h in rect:
                    roiImg = frame[y:y + h, x:x + w]
                    cv2.rectangle(frame, (x - 10, y - 10), (x + w + 10, y + h + 10), color, 3)
                    shutdown = True
            cv2.imshow("opencut", frame)
            key = cv2.waitKey(1)
            if shutdown:
                time.sleep(1)
                key = 27
            if key & 0xff == ord('q') or key == 27:
                print(frame.shape, ret)
                break
        cap.release()
        e.Skip()
ex = wx.App()
Main(None)
ex.MainLoop()