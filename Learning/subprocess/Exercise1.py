import subprocess
from time import sleep

subprocess.Popen(["calc.exe"])

print("Calculator opened!")
sleep(3)
subprocess.run(r"taskkill /IM CalculatorApp.exe /F")