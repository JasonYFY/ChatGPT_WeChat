# 1.安装 
## 1.1在ubuntu18.04上安装Tesseract4**
```
sudo apt install tesseract-ocr
 
sudo apt install libtesseract-dev
 
sudo pip install pytesseract
```

## 1.2在windows下安装Tesseract 4.0
Tesseract本身没有windows的安装包，不过它指定了一个第三方的封装的windows安装包，在其wiki上有说明，大家可直接到这个地址进行下载：

https://digi.bib.uni-mannheim.de/tesseract/
 
其中文件名中带有 dev 的为开发版本，不带 dev 的为稳定版本。

下载后就是一个exe安装包，直接右击安装即可，安装完成之后，配置一下环境变量，编辑 系统变量里面 path，添加下面的安装路径：

C:\Program Files (x86)\Tesseract-OCR

具体使用安装见：

https://www.cnblogs.com/gl1573/p/9876397.html

https://blog.csdn.net/qq_35531549/article/details/95191677

# 2.检查Tesseract版本
```
tesseract --version
```
输出
```
tesseract 4.0.0-beta.1-306-g45b11
 
leptonica-1.76.0
 
libjpeg 9c : libpng 1.6.34 : libtiff 4.0.9 : zlib 1.2.8
 
Found AVX2
 
Found AVX
 
Found SSE
```

# Tesseract4语言包错误
您可能会遇到错误Error opening data file tessdata/eng.traineddata

它只是意味着语言包（tessdata / eng.traineddata）不在正确的路径中。您可以通过两种方式解决此问题。

1：确保文件位于预期路径中（例如，在linux上，路径为/usr/share/tesseract-ocr/4.00/tessdata/eng.traineddata）。

2：创建目录tessdata，下载eng.traineddata并将文件保存到tessdata/eng.traineddata。然后，您可以指示Tesseract使用查找此目录中的语言包。(这种方法不推荐问题很多)。

如果你想下载新的语言库，下载地址见：

https://github.com/tesseract-ocr/tessdata

# 安装 easyocr
安装名为 torch 的软件包，报错Killed，则采用此命令
```
pip install torch --no-cache-dir
```

#3.安装PaddleOCR
pip install paddlepaddle
pip install paddleocr

命令行为：paddleocr --image_dir 图片文件名 --lang ch。lang参数指出用什么语言去解读。ch是指中英文。第一次运行时会下载一些必要的模型。