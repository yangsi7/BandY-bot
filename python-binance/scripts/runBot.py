import subprocess

def run():
    filename = 'my_python_code_A.py'
    while True:
        """However, you should be careful with the '.wait()'"""
        p = subprocess.Popen('python '+'runYangiBot.py', shell=True).wait()
    
        if p != 0:
            continue
        else:
            break
