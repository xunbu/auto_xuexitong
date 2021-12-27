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
    #coursewebsite='http://mooc.s.ecust.edu.cn/mycourse/studentcourse?courseId=441650000011904&clazzid=441650000023515&enc=459c3c9a066bd68deeb06aec2a8f74cd'
    #coursewebsite='http://mooc.s.ecust.edu.cn/mycourse/studentcourse?courseId=441650000007294&clazzid=441650000013676&enc=b6e62362ee72d2456355ab08a52ed05e'
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
    # 选择未完成的章节（视频界面）
    unfinishedsection = wd.find_element(By.XPATH, "//span[@class='roundpointStudent  orange01 a002 jobCount']/../..")
    while 1:
        # 该章节未完成的任务数
        unfinishedtask_number=unfinishedsection.find_element(By.XPATH,".//span[@class='roundpointStudent  orange01 a002 jobCount']").text
        unfinishedtask_number=int(unfinishedtask_number)
        print('未完成任务数：',unfinishedtask_number)
        #点击进入该未完成的章节
        unfinishedsection.find_element(By.XPATH,".//a[@href]").click()
        print('已进入未完成的视频章节')
        #进入第一个iframe
        wd.switch_to.frame(wd.find_element(By.XPATH,"//iframe"))
        #生成视频iframe列表对象（有fastforward属性的视为视频iframe）
        videoframelist=wd.find_elements(By.XPATH,"//iframe[@fastforward]")
        videonumber=len(videoframelist)
        print('视频数',videonumber)
        #进入第一个未完成视频的frame里（假设所有视频都是从上看到下）
        wd.switch_to.frame(videoframelist[videonumber-unfinishedtask_number])
        #播放视频
        starbutton=wd.find_element(By.XPATH,"//button[@title='播放视频']")
        wd.execute_script("arguments[0].click();",starbutton)
        #回到主html
        wd.switch_to.default_content()
        while 1:
            try:
                #监控现在的未完成任务数
                current_unfinishedtask_number=unfinishedsection.find_element(By.XPATH,".//span[@class='roundpointStudent  orange01 a002 jobCount']").text
                print('现在的未完成数',current_unfinishedtask_number)
            except:
                #若找不到未完成任务数说明已经完成
                #似乎一个小节完成时unfinishedsection也会有问题？
                print('小节已完成')
                break
            else:
                current_unfinishedtask_number = int(current_unfinishedtask_number)
            if current_unfinishedtask_number==unfinishedtask_number:
                #如果未完成任务数未改变，则等待十秒
                print('视频未结束，等待十秒')
                time.sleep(10)
            else:
                #完成了一个视频则重新开始
                print('完成了一个视频')
                break
        try:
            # 选择未完成的章节（视频界面）
            unfinishedsection=wd.find_element(By.XPATH,"//span[@class='roundpointStudent  orange01 a002 jobCount']/../..")
        except NoSuchElementException:
            print('视频章节已全部完成')
            return 0


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


