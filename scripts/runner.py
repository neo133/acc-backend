import subprocess
import sys

MASTER_PATH = '/home/frinksacckymore001/acc-backend/scripts'
SLAVE_PATH = '/home/frinksacckymore002/acc-backend/scripts'
TEST_PATH = '/home/poop/frinks/acc/acc-backend/scripts'

try:
    print("my argument", sys.argv[1])
    # 0 means master 1 means slave
    if(sys.argv[1] == '0'):
        subprocess.Popen(
            [f"python3 {MASTER_PATH}/label_bag_tag/label_tag.py"], shell=True)
        subprocess.Popen(
            [f"python3 {MASTER_PATH}/bag_counting/bag_counting.py"], shell=True)
    else:
        subprocess.Popen(
            [f"python3 {SLAVE_PATH}/label_bag_tag/label_tag_slave.py"], shell=True)

except Exception as e:
    print(str(e))
    pass
