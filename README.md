# babel-image-archives-noise-or-not
This project retrieves the images from the site babel image archives and classifies them if they are just a bunch of noise or actually meaningful.

# How To install and use:

first you need to clone the library by executing this command on cmd.
```
git clone https://github.com/youneshlal7/babel-image-archives-noise-or-not.git
```
then change the directory to the folder where the code exists
```
cd babel-image-archives-noise-or-not
```
after that install the requirements to run the script
```
pip install -r requirements.txt
```
run the script ndirscreator.py to create the necessary folders: imgholder, noise and not noise which are necessary to run the program
```
python ndirscreator.py
```
and now you're good to run the main.py which will only run one instance of the program by using this command
```
python main.py
```
if you want to multithread run multiple.py but only if you're pc or laptop can handle it, also you can change the number of programs running by changing the number in the for loop in multiple.py.
```
python multiple.py
```
The final thing is if you don't have the chromedriver on your computer please download it from: https://chromedriver.chromium.org/ which matches your version of chrome your currently running on your computer, and change the path of chromedriver in main.py line 101 of the script and if you done all of these steps successfully, you will see the script running normally on your screen.
