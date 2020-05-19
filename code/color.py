# -----------------colorama模块的一些常量---------------------------  
# Fore: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.  
# Back: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET.  
# Style: DIM, NORMAL, BRIGHT, RESET_ALL  
#  

from colorama import  init, Fore, Back, Style  
init(autoreset=True)  
class Colored(object):  

    #  前景色:红色  背景色:默认  
    def red(self, s):  
        return Fore.RED + s + Fore.RESET  

    #  前景色:黄色  背景色:默认  
    def yellow(self, s):  
        return Fore.YELLOW + s + Fore.RESET  

    #  前景色:洋红色  背景色:默认  
    def magenta(self, s):  
        return Fore.MAGENTA + s + Fore.RESET  

    #  前景色：绿色  背景色:默认  
    def green(self, s):  
        return Fore.GREEN + s + Fore.RESET  

    #  前景色:白色  背景色:绿色  
    def white_green(self, s):  
        return Fore.WHITE + Back.GREEN + s + Fore.RESET + Back.RESET  

def pError(s):
    color = Colored()
    s = '*****'+s+'*****'
    print (color.red(s))

def pDone(s):
    color = Colored()
    s = '-----'+s+'-----'
    print (color.green(s))

def pInfo(s):
    color = Colored()
    print (color.yellow(s))

def pImportant(s):
    color = Colored()
    s= '==='+s+'==='
    print (color.white_green(s))

if __name__=='__main__':
    pImportant('important')
    pInfo('info')
    pDone('done')
    pError('error')