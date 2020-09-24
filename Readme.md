# ImageTools
- *作者：李钦星* 
- *版本：1.0* 

这是一款图像相关的工具软件，扩展性好。目前集成有镜头计算器、抖动测试工具、看图工具等功能。

---



## （一）镜头计算器

### 主要功能 

#### 1. 景深计算

1. 图像**输出**选择景深

2. 可以选择的**变量**有三种，焦距、光圈和物距，物距就是镜头的对焦距离，这个决定了左侧图像X轴的意义

3. **基础设置**：设置镜头的焦距，光圈，物体对焦距离和sensor尺寸，这四个参数必须准确

4. 高级设置—**sensor尺寸**：由于sensor尺寸用英寸表示，并不准确，这里提供sensor尺寸的微调。

5. 高级设置—**弥散圈直径**：景深就是图像清晰的范围，而弥散圈就是衡量图像清晰的标准。滑块往左拖，弥散圈越小，那么清晰度的标准就越高，景深对应也会越小。

6. **高级设置**：焦距、光圈、对焦范围，是用来调节图像X轴的范围

7. 最后点击**确认**就会输出想要的图像

8. 图像下方有对图像微调的**按钮**

   从左到右的功能分别是还原图像，回退上一步，前进一步，移动图像，图像局部放大，调整图像坐标轴的范围，调整图像坐标轴的名称，另存图像

#### 2. 镜头参数输出 

1. 图像输出选择参数
2. 其余步骤参考景深计算一致
3. 等效焦距：sensor对角线的长度，等效成35mm照相机画幅对角线长度（42.27mm）时，其镜头的实际焦距所对应的35mm照相机镜头的焦距。
4. 超焦距距离：对焦距离越近，前景深越近。而对焦在远处的某一点，使得景深的另一极端恰为”无限远“，此时对焦距离就称作超焦距距离。相机对焦在超焦距距离，可以让景深最大
5. 前景深距离：当前配置下，能看清的最近距离
6. 后景深距离：当前配置下，能看清的最远距离
7. 总景深：当前配置下，清晰的范围

### 计算原理

本文用的方法来自此[论文](https://wenku.baidu.com/view/2191302baf45b307e9719706.html)

---

## （二）防抖检测工具
这是一款用来量化防抖效果的工具。

### 1. 使用方法
1. 拍摄视频，视频的要求：尽量用棋盘格等边缘比较明显的物体，图像中心尽量有明显的特征点
2. 导入振动台上拍摄的视频，可以通过打开文件或者拖动文件到视频预览窗口进行导入
3. 也可以对设备进行在线调试：点击打开设备，然后配置rtsp的用户，密码，IP和端口号。如果是移动执法仪设备的话，只需要确保adb或者kdb能够连接设备，默认设置即可。
4. 点击右下角的开始，会开始对图像进行处理，并会更新实时的结果。点击停止，会停止图像的处理
5. 视频预览会显示每个特征点的运动轨迹，中心的特征点会着重标注出来。确保每个点的轨迹都没有问题。在最终结果那一栏会得出这段时间内的最终结果

### 2. 高级操作
1. ROI上下边界：由于有些视频存在OSD，会干扰到特征点的选取，可以调整上下边界控制特征点的选取范围
2. 跳过帧数：因为有的时候前几帧有干扰的物体，或者效果不佳，可以跳过前几帧，再进行特征点选取。
3. 特征点的数量：如果画面中心没有特征点，那么可以调整此滑块。如果特征点过多，也可以调整此滑块
4. 特征点的运动幅度：如果运动幅度过大，出现跟踪错误的话，就增大特征点的运动幅度
5. 计算间隔（帧）：每多少帧会输出一个实时的结果，确保每次的实时结果都比较正常，再去看最终结果
6. 计算方向：跟最后结果挂钩，只显示某个方向上的结果
7. 去除静止的特征点：可以排除roi等静止的点，优先选用ROI的方式

### 3. 评价标准
- 中心点位移：一段时间内离图像中心最近的特征点的最大像素点位移
- 各点最大位移：检测到的所有特征点中，最大的像素点位移
- 图片扭曲程度：根据所有的特征点的运动轨迹，与中心的差距，算出一个图片的变形程度
- 实时结果是每50帧计算一次，最终结果根据实时结果进行平均或者更新

---
## (三）图片查看工具
这是一款能够对图像进行分析以及简单的处理工具
### 界面
1. 右侧有四个按钮，分为为：打开图像，保存图像，图像处理前后对比，图像统计分析
2. 菜单栏有各种图像处理的模块，目前仅仅做了滤波的相关处理
3. 左下角会显示当前图像鼠标位置像素点的信息，包括RGB值以及缩放比例
### 使用方法
1. 可以通过点击打开图像的按钮或者拖动图片到图像显示框里进行显示
2. 通过菜单栏可以对图像进行简单的处理
3. 通过保存按钮可以保存当前的图像(可是是图像处理前后的)
4. 通过对比按钮可以对比图像处理前后的变化
5. 通过点击图像统计分析按钮可以获取到整幅图像的统计信息，包括直方图，RGB均值与信噪比，转成YUV之后的均值和信噪比，窗口大小，以及RGB增益
6. 统计信息窗口不关闭的情况下，框选图像中的任意一块区域，都可以显示这块区域的统计信息
7. 统计信息窗口中的直方图，显示了RGB和Y通道的直方图，可以通过复选框选择是否显示该通道的直方图

---
## （四）代码拓展与编译
### 1. 扩展方法
1. tools类中增加工具的使用方式和界面
2. ImageTools.py中添加工具的打开方式
3. 如果需要添加图标等资源，就加在Ui的resource文件夹里，并配置resource.qrc

### 2. vscode配置方法
#### UI修改和编译
1. 安装python for QT插件
2. 在设置里面填写designer.exe的路径和pyuic的路径，然后右键ui文件，就可以对文件进行修改或者编译啦。
3. 如果想要在当前目录下生成，修改pyuic的配置为：`pyside2-uic -o ${fileDirname}/${fileBasenameNoExtension}.py`

### 3. 打包方法
运行buildexe.bat, 注意matplotlib版本最好是3.2以下