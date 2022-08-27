from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
import base64
from math import log10, sqrt
import cv2
import numpy as np
from collections import Counter
from multiprocessing import Pool
import shutil
import time


#this function injects the browser so it can retrieve the bytes of the image.
def get_file_content_chrome(driver, uri):
  result = driver.execute_async_script("""
    var uri = arguments[0];
    var callback = arguments[1];
    var toBase64 = function(buffer){for(var r,n=new Uint8Array(buffer),t=n.length,a=new Uint8Array(4*Math.ceil(t/3)),i=new Uint8Array(64),o=0,c=0;64>c;++c)i[c]="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".charCodeAt(c);for(c=0;t-t%3>c;c+=3,o+=4)r=n[c]<<16|n[c+1]<<8|n[c+2],a[o]=i[r>>18],a[o+1]=i[r>>12&63],a[o+2]=i[r>>6&63],a[o+3]=i[63&r];return t%3===1?(r=n[t-1],a[o]=i[r>>2],a[o+1]=i[r<<4&63],a[o+2]=61,a[o+3]=61):t%3===2&&(r=(n[t-2]<<8)+n[t-1],a[o]=i[r>>10],a[o+1]=i[r>>4&63],a[o+2]=i[r<<2&63],a[o+3]=61),new TextDecoder("ascii").decode(a)};
    var xhr = new XMLHttpRequest();
    xhr.responseType = 'arraybuffer';
    xhr.onload = function(){ callback(toBase64(xhr.response)) };
    xhr.onerror = function(){ callback(xhr.status) };
    xhr.open('GET', uri);
    xhr.send();
    """, uri)
  if type(result) == int :
    raise Exception("Request failed with status %s" % result)
  return base64.b64decode(result)

#this is the first function that validates if the image if it's noise or not by comparing it to an example from the archive.
def PSNR(comp, tested):
    mse = np.mean((comp - tested) ** 2)
    if(mse == 0):

        return 100
    max_pixel = 255.0
    psnr = 20 * log10(max_pixel / sqrt(mse))
    return psnr

#these two function calculates the entropy of the image, the higher the more likely it's just noise.
def calcIJ(img_patch):
    total_p = img_patch.shape[0] * img_patch.shape[1]
    if total_p % 2 != 0:
        tem = img_patch.flatten()
        center_p = tem[int(total_p / 2)]
        mean_p = (sum(tem) - center_p) / (total_p - 1)
        return (center_p, mean_p)
    else:
        print("modify patch size")


def calcEntropy2d(img, win_w=3, win_h=3, threadNum=6):
    height = img.shape[0]
    width = img.shape[1]

    ext_x = int(win_w / 2)
    ext_y = int(win_h / 2)

    ext_h_part = np.zeros([height, ext_x], img.dtype)
    tem_img = np.hstack((ext_h_part, img, ext_h_part))
    ext_v_part = np.zeros([ext_y, tem_img.shape[1]], img.dtype)
    final_img = np.vstack((ext_v_part, tem_img, ext_v_part))

    new_width = final_img.shape[1]
    new_height = final_img.shape[0]

    patches = []
    for i in range(ext_x, new_width - ext_x):
        for j in range(ext_y, new_height - ext_y):
            patch = final_img[j - ext_y:j + ext_y + 1, i - ext_x:i + ext_x + 1]
            patches.append(patch)

    pool = Pool(processes=threadNum)
    IJ = pool.map(calcIJ, patches)
    pool.close()
    pool.join()

    Fij = Counter(IJ).items()

    Pij = []
    for item in Fij:
        Pij.append(item[1] * 1.0 / (new_height * new_width))

    H_tem = []
    for item in Pij:
        h_tem = -item * (np.log(item) / np.log(2))
        H_tem.append(h_tem)

    H = sum(H_tem)
    return H


if __name__ == '__main__':
	#this option only let the browser run in a headless mode, so you can't see the chrome window.
	options = Options()
	options.add_argument('--headless')

	#this is the path for the chromedriver that controls chrome if you don't have, install it from https://chromedriver.chromium.org/ and replace the path.
	chromep = Service(r"C:\Program Files (x86)\chromedriver.exe")
	driver = webdriver.Chrome(service=chromep, options=options)

	driver.get("https://babelia.libraryofbabel.info/slideshow.html")
	time.sleep(1)

	f = driver.find_element("id","palette")
	while f.get_attribute("src") == "https://babelia.libraryofbabel.info/img/white.jpg":
		pass

	f1 = driver.find_element("id","loc")

	imgsrc = f.get_attribute("src")
	print(imgsrc)

	imgloc = f1.text.replace("babelia #","")
	print(imgloc)

	#this is where the files get written to the imgholder folder where it holds the images until they're analysed.
	bytes = get_file_content_chrome(driver, imgsrc)
	img = open("imgholder\\"+imgloc+".jpg","wb")
	img.write(bytes)
	img.close()

	comp = cv2.imread("babelia 6004745726753998.jpg")
	test = cv2.imread("imgholder\\"+imgloc+".jpg", 1)
	test2 = cv2.imread("imgholder\\"+imgloc+".jpg", cv2.IMREAD_GRAYSCALE)

	value = PSNR(comp, test)
	entropyvalue = calcEntropy2d(test2, 3, 3)

	print(value)
	print(entropyvalue)

	#after some tests, I found that thes values are the correct values to see if the image is just noise or not.
	if value >= 27.9 or entropyvalue >= 16:
		print("this image is just noise.")
		shutil.move("imgholder\\"+imgloc+".jpg","noise\\"+imgloc+".jpg")
	else:
		print("this isn't noise.")
		shutil.move("imgholder\\"+imgloc+".jpg","not noise\\"+imgloc+".jpg")

	#this checks for images that appear on the slideshow.
	while True:
		imgsrc1 = f.get_attribute("src")
		imgloc1 = f1.text.replace("babelia #","")
		if imgsrc1 == imgsrc:
			pass
		else:
			imgsrc = ""
			imgsrc += imgsrc1
			print(imgsrc)

			imgloc = ""
			imgloc += imgloc1
			print(imgloc)

			bytes = get_file_content_chrome(driver, imgsrc)
			img = open("imgholder\\"+imgloc+".jpg","wb")
			img.write(bytes)
			img.close()

			comp = cv2.imread("babelia 6004745726753998.jpg")
			test = cv2.imread("imgholder\\"+imgloc+".jpg", 1)
			test2 = cv2.imread("imgholder\\"+imgloc+".jpg", cv2.IMREAD_GRAYSCALE)

			value = PSNR(comp, test)
			entropyvalue = calcEntropy2d(test2, 3, 3)

			print(value)
			print(entropyvalue)

			if value >= 27.9 or entropyvalue >= 16:
				print("this image is just noise.")
				shutil.move("imgholder\\"+imgloc+".jpg","noise\\"+imgloc+".jpg")
			else:
				print("this isn't noise.")
				shutil.move("imgholder\\"+imgloc+".jpg","not noise\\"+imgloc+".jpg")



