# TripleX:一个局域网分享工具

> 是这样的张总, 您在家里的电脑上按了ctrl+c，然后在公司的电脑上再按ctrl+v是肯定不行的。即使同一篇文章也不行。不不不，多贵的电脑都不行。

TripleX 就是为了让人再懒一点，可以方便地发送文字和文件给视野可见范围的其他机器。并结合系统自带的剪切板，用户可以在不同电脑上使用‘复制’和‘粘贴’

- 在A电脑和B电脑都装好软件
- 在A电脑Ctrl+c复制后，点击发送
- 在B电脑点击接收
- 要使用时就在B电脑Ctrl+v即可

## 使用步骤

pull down this repo's code:

    git clone git@github.com:vincent770/tripleX.git

install packet from pip:

    pip3 install -r requirements.txt

run with python:
    
    python3 client.py

**notice:A testing server was deployed by the author, you can also use your own one by configuring server info.**

## 如果你要修改项目

### 文件目录

### 打包
    cd tripleX/client
    sudo python3 setup.py py2app -A


