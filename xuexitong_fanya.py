from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import os
import time
##V1.1
datapath=os.path.abspath('./userdata')
if not os.path.exists(datapath):
    os.makedirs(datapath)

option = webdriver.EdgeOptions()
option.add_argument('user-data-dir={}'.format(datapath))
option.add_experimental_option('excludeSwitches', ['enable-logging'])
wd = webdriver.Edge(service=Service('./msedgedriver.exe'),options=option)
wd.implicitly_wait(10)
wd.maximize_window()

def main():
    wd.get("https://i.chaoxing.com/")
    coursewebsite=input('请输入完整的课程网址(用鼠标右键粘贴):')
    wd.get(coursewebsite)
    zhangjie=wd.find_element(By.XPATH,"//*[@dataname='zj']")
    wd.execute_script("arguments[0].click();",zhangjie)
    wd.switch_to.frame('frame_content-zj')
    try:
        # 在课程主页面中寻找未完成的章节
        unfinishedpart=wd.find_element(By.XPATH,"//span[@class='catalog_points_yi']/../../..")
    except NoSuchElementException:
        print('章节已全部完成')
        return 0
    else:
        #点击该未完成的章节（课程主界面）
        wd.execute_script("arguments[0].click();",unfinishedpart)
    print('进入学生学习页面')
    choosehandle(wd,'学生学习页面')
    ######################################
    ######章数
    ncelllist=wd.find_elements(By.XPATH,"//*[@class='posCatalog_select' or @class='posCatalog_select posCatalog_active']")
    ncellnumber=len(ncelllist)
    print('ncellnumber',ncellnumber)
    #unfinishncell's index
    un_cellindex=[]
    print('正在读取目录，请稍等')
    time.sleep(4)
    wd.implicitly_wait(0.1)
    for i in range(ncellnumber):
        try:
            ncelllist[i].find_element(By.XPATH,".//*[@class='orangeNew']")
        except NoSuchElementException:
            continue
        else:
            un_cellindex.append(i)
    print('目录已获取完成')
    print('un_cellindex',un_cellindex)
    wd.implicitly_wait(5)
    #################################################
    for i,list_index in enumerate(un_cellindex):
        print('i:',i,'index:',list_index)
        #每看完一个视频，ncellist会发生变化，故需要重新获得
        ncelllist = wd.find_elements(By.XPATH,"//*[@class='posCatalog_select' or @class='posCatalog_select posCatalog_active']")
        ####开始观看视频
        watchvideo()
        ####观看完本章所有视频
        # 点击下一个未完成unfinishedcell
        wd.switch_to.default_content()
        ncelllist = wd.find_elements(By.XPATH,"//*[@class='posCatalog_select' or @class='posCatalog_select posCatalog_active']")
        if i <len(un_cellindex)-1:
            ncelllist[un_cellindex[i+1]].click()
            #wd.execute_script("arguments[0].click();",ncelllist[un_cellindex[i+1]])
    print('所有章节已完成')


def watchvideo():
    # 未完成任务数
    un_tasknumber = wd.find_element(By.XPATH,"//*[@class='posCatalog_select posCatalog_active']//*[@class='orangeNew']").get_attribute('innerHTML')
    un_tasknumber = int(un_tasknumber)
    print('未完成任务数：', un_tasknumber)
    ##进入第一层iframe
    wd.switch_to.frame(wd.find_element(By.XPATH, "//iframe"))
    # 生成视频iframe列表对象（有allowfullscreen属性的视为视频iframe）
    videoframelist = wd.find_elements(By.XPATH, "//*[@class='ans-attach-ct']//iframe[@allowfullscreen]")
    videonumber = len(videoframelist)
    print('视频数', videonumber)
    #未完成的视频的index(假设所有视频都是从上看到下）
    un_videoindex=list(range(0,videonumber))
    print('un_videoindex',un_videoindex)
    for index in un_videoindex:
        print('视频index',index)
        # 进入第一个未完成视频的frame里
        wd.switch_to.frame(videoframelist[index])
        startbutton=wd.find_element(By.XPATH,"//button[@title='播放视频']")
        startbutton.click()
        vol=wd.find_element(By.XPATH,"//button[@title='静音']")
        vol.click()
        print('开始播放')
        #去到上层iframe检测是否完成
        wd.switch_to.parent_frame()
        while 1:
            finishflag=videoframelist[index].find_element(By.XPATH,"./..").get_attribute('class')
            if finishflag=='ans-attach-ct':
                ifstop(videoframelist,index)
                print('视频未完成，等待三秒')
                time.sleep(3)
            else:
                print('视频已完成')
                break

def ifstop(videoframelist,index):
    #检测视频是否停止，若停止则打开视频
    #在第一层iframe使用（即视频iframe的上一层）
    wd.implicitly_wait(0.1)
    wd.switch_to.frame(videoframelist[index])
    try:
        startbutton2=wd.find_element(By.XPATH,"//*[@class='vjs-play-control vjs-control vjs-button vjs-paused']")
    except:
        print('视频正常播放')
    else:
        print("视频暂停，正在恢复播放")
        startbutton2.click()
        print("已恢复播放")
    wd.switch_to.parent_frame()
    wd.implicitly_wait(5)
    #ActionChains(wd).move_to_element(wd.find_element(By.XPATH,"//iframe")).perform()
def choosehandle(wd,title:str):
    for handle in wd.window_handles:
        # 先切换到该窗口
        wd.switch_to.window(handle)
        # 得到该窗口的标题栏字符串，判断是不是我们要操作的那个窗口
        if title in wd.title:
            # 如果是，那么这时候WebDriver对象就是对应的该该窗口，正好，跳出循环，
            break
    return 0


if __name__=='__main__':
    try:
        main()
    except:
        print('程序已结束。若要再次使用，请关闭该浏览器窗口并重启程序')
    else:
        print('程序已结束。若要再次使用，请关闭该浏览器窗口并重启程序')