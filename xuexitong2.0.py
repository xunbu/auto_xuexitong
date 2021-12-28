from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import os
import time

datapath=os.path.abspath('./userdata')
if not os.path.exists(datapath):
    os.makedirs(datapath)

option = webdriver.EdgeOptions()
option.add_argument('user-data-dir={}'.format(datapath))
option.add_experimental_option('excludeSwitches', ['enable-logging'])
wd = webdriver.Edge(service=Service('./msedgedriver.exe'),options=option)
wd.implicitly_wait(10)

def main():
    wd.get("https://s.ecust.edu.cn/")
    coursewebsite=input('请输入完整的课程网址(可用鼠标右键复制):')
    wd.get(coursewebsite)
    try:
        # 在课程主页面中寻找未完成的章节
        unfinishedpart=wd.find_element(By.XPATH,"//em[@class='orange']/../../..")
    except NoSuchElementException:
        print('章节已全部完成')
        return 0
    else:
        #点击该未完成的章节（课程主界面）
        unfinishedpart.find_element(By.XPATH,".//a[@href]").click()
    print('进入学生学习页面')
    choosehandle(wd,'学生学习页面')
    ######章数
    global ncelllist
    ncelllist=wd.find_elements(By.XPATH,"//*[@class='ncells']")
    ncellnumber=len(ncelllist)
    print('ncellnumber',ncellnumber)
    #unfinishncell's index
    un_cellindex=[]
    print('正在读取目录，请稍等')
    time.sleep(4)
    wd.implicitly_wait(0.2)
    for i in range(ncellnumber):
        try:
            ncelllist[i].find_element(By.XPATH,".//*[@class='roundpointStudent  orange01 a002 jobCount']")
        except NoSuchElementException:
            continue
        else:
            un_cellindex.append(i)
    print('目录已获取完成')
    print('un_cellindex',un_cellindex)
    wd.implicitly_wait(10)
    for i,list_index in enumerate(un_cellindex):
        print('i:',i,'index:',list_index)
        #每看完一个视频，ncellist会发生变化，故需要重新获得
        ncelllist = wd.find_elements(By.XPATH, "//*[@class='ncells']")
        ####开始观看视频
        watchvideo(list_index)
        ####观看完本章所有视频
        # 点击下一个未完成unfinishedcell
        wd.switch_to.default_content()
        if i <len(un_cellindex)-1:
            wd.execute_script("arguments[0].click();",ncelllist[un_cellindex[i+1]].find_element(By.XPATH,".//*[@href]"))
    print('所有章节已完成')


def watchvideo(list_index):
    print('index',list_index)
    global ncelllist
    # 未完成任务数
    nowcell=ncelllist[list_index]
    un_tasknumber = nowcell.find_element(By.XPATH, ".//span[@class='roundpointStudent  orange01 a002 jobCount']").text
    un_tasknumber = int(un_tasknumber)
    print('未完成任务数：', un_tasknumber)
    ##进入第一层iframe
    wd.switch_to.frame(wd.find_element(By.XPATH, "//iframe"))
    # 生成视频iframe列表对象（有fastforward属性的视为视频iframe）
    videoframelist = wd.find_elements(By.XPATH, "//iframe[@fastforward]")
    videonumber = len(videoframelist)
    print('视频数', videonumber)
    #未完成的视频的index(假设所有视频都是从上看到下）
    un_videoindex=list(range(videonumber - un_tasknumber,videonumber))
    print('un_videoindex',un_videoindex)
    for i,index in enumerate(un_videoindex):
        print('视频index',index)
        # 进入第一个未完成视频的frame里
        wd.switch_to.frame(videoframelist[index])
        startbutton=wd.find_element(By.XPATH,"//button[@title='播放视频']")
        wd.execute_script("arguments[0].click();",startbutton)
        wd.switch_to.default_content()
        while 1:
            try:
                ncelllist = wd.find_elements(By.XPATH, "//*[@class='ncells']")
                nowcell = ncelllist[list_index]
                now_tasknumber=nowcell.find_element(By.XPATH, ".//span[@class='roundpointStudent  orange01 a002 jobCount']").text
            except NoSuchElementException:
                print('小节已完成')
                return 0
            else:
                now_tasknumber=int(now_tasknumber)
                print('现在的任务数为',now_tasknumber)
            if now_tasknumber==un_tasknumber:
                print('视频未完成，等待十秒')
                time.sleep(10)
            else:
                print('切换下一个视频')
                un_tasknumber=now_tasknumber
                break
        #进入第一层frame
        wd.switch_to.frame(wd.find_element(By.XPATH, "//iframe"))

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
    #try:
    main()
    #except:
    #    print('程序已结束。若要再次使用，请关闭该浏览器窗口并重启程序')

