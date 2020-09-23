import os
import time


def main():
    while True:
        os.system("dig GuardDutyC2ActivityB.com any")
        os.system('echo "<h1><font color="red">Hackathon Testing site!</font></h1><br><h1>YOU HAVE BEEN HACKED</h1>" | sudo tee /var/www/html/index.html')
        time.sleep(60)


if __name__ == "__main__":
    main()
