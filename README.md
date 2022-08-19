  <div align="center"><p><em>🗂️思源笔记数据云备份工具</em></p></div>



siyuanBackUp，可实现自动打包数据到阿里云盘或本地。

## 支持

- [x] 触发方式
  - [x] API网关触发器
  - [x] 定时触发器

## 部署

### 一、创建思源docker

首先创建一个工作空间目录，用于映射思源的workspace

> 目录位置可以自定义，后面用到的地方自行替换

```bash
mkdir -p /myapps/siyuan/workspace
```



然后运行一个docker容器，用来拷贝我们后面需要用的原文件

```bash
docker run --name=siyuan -u 1000:1000 b3log/siyuan:v2.1.6 --workspace=/siyuan/workspace/
```



Ctrl + C，把运行思源进程停掉

拷贝容器中前端的js目录

```bash
docker cp siyuan:/opt/siyuan/stage/build/desktop /myapps/siyuan/
```

![img](https://m.360buyimg.com/babel/jfs/t1/65240/3/21790/107135/62ff34d1Eb00d68c6/fadc91302870c81a.png)



把这个容器删了，我们运行一个新的容器，并映射本地workspace和desktop这两个目录

> 运行容器之前给这两个目录设上权限，不然容器起不来

```bash
docker rm siyuan
chown -R 1000:1000 /myapps/siyuan/workspace
chown -R 1000:1000 /myapps/siyuan/desktop
```

我指定的端口是6807，也可以自定义，后面iptables规则和mitmproxy程序中的端口需要改成一样的

```bash
docker run --name=siyuan-2.1.6 -v /myapps/siyuan/workspace:/siyuan/workspace -v /myapps/siyuan/desktop:/opt/siyuan/stage/build/desktop -p 6807:6806 -u 1000:1000 b3log/siyuan:v2.1.6 --workspace=/siyuan/workspace/
```

![](https://m.360buyimg.com/babel/jfs/t1/102889/35/32125/101700/62ff35abE9e8fbe63/b9e796cd5c2c16ed.png)



通过测试，在网页上正常访问

![](https://m.360buyimg.com/babel/jfs/t1/100403/25/32063/45617/62ff3629E383653dc/92083b736bbf59c0.png)







### 二、部署aliyunpan

想要在Linux上操作阿里云盘，有一个很好用的开源工具aliyunpan，用于我们备份工作的上传

**apt安装**

适用于apt包管理器的系统，例如**Ubuntu**，**国产deepin深度操作系统**等。目前只支持amd64和arm64架构的机器。

```bash
sudo curl -fsSL http://file.tickstep.com/apt/pgp | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/tickstep-packages-archive-keyring.gpg > /dev/null && echo "deb [signed-by=/etc/apt/trusted.gpg.d/tickstep-packages-archive-keyring.gpg] http://file.tickstep.com/apt aliyunpan main" | sudo tee /etc/apt/sources.list.d/tickstep-aliyunpan.list > /dev/null && sudo apt-get update && sudo apt-get install -y aliyunpan
```



**rpm安装**

适用于rpm包管理器的系统，例如**CentOS**、**RockyLinux**等。目前只支持amd64和arm64架构的机器。

```bash
sudo curl -fsSL http://file.tickstep.com/rpm/aliyunpan/aliyunpan.repo | sudo tee /etc/yum.repos.d/tickstep-aliyunpan.repo > /dev/null && sudo yum install aliyunpan -y
```



安装完成后用命令行登录阿里云盘

```bash
aliyunpan login
```

然后需要输入RefreshToken，获取这个RefreshToken需要进到阿里云盘官网并登录，按照下方图片操作

![](https://m.360buyimg.com/babel/jfs/t1/161649/38/30954/216372/62ff3674E7fea87fb/dfb78ab25ba40da6.png)

获取到后，复制下来，粘贴到终端回车，登录成功

> 把RefreshToken记下来，等会自动化脚本还要用到这个

![](https://m.360buyimg.com/babel/jfs/t1/62015/19/20893/24177/62ff3698E9c7f514e/074ffbf89e259b16.png)







### 三、部署mitmproxy流量监控

> 运行siyuanBackUp需要机器中有Python3支持，没有环境可以`yum install python36`快速安装

克隆siyuanBackUp，克隆的位置可以任意，我选择和之前的目录放在了一起`cd /myapps/siyuan`

```bash
git clone https://gitclone.com/github.com/aqz236/siyuanBackUp.git
```

如果使用访问国外github克隆速度较慢，也可以克隆下面gitee的仓库

```bash
git clone https://gitee.com/FSHOU/siyuanBackUp.git
```



进入siyuanBackUp，创建虚拟环境，并在虚拟环境中安装项目依赖

```bash
cd siyuanBackUp/
python3 -m venv siyuanEnv
source siyuanEnv/bin/activate
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```



安装完成后需要简单填写一下配置

编辑`backup.sh`，如果你之前没有对映射位置做过自定义的修改，那么这里只需要填写RefreshToken

![](https://m.360buyimg.com/babel/jfs/t1/114758/4/28140/68716/62ff36d2E6e24c615/fd96c426bbaf4175.png)



编辑`siyuan_mitm.py`，如果你设置的端口也是6807，则此处不需要做任何修改

![](https://m.360buyimg.com/babel/jfs/t1/150655/10/29446/64763/62ff36f0Ee7e2eae1/4bdae18e5fb0a808.png)



添加两条自定义iptables规则，此处的6807要与创建容器时设置的端口相同，8712是设置的mitmproxy透明代理端口。

```bash
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 6807 -j REDIRECT --to-port 8712
iptables -t nat -A PREROUTING -i eth0 -p udp --dport 6807 -j REDIRECT --to-port 8712
```



然后把当前的iptables配置保存到配置文件中

```bash
iptables-save > /etc/sysconfig/iptables
```



为了让添加的两条规则永久生效，需要执行

```bash
service iptables save
```



如果报错`Failed to restart iptables.service: Unit not found.`,则需要安装iptables-services

```bash
yum install iptables-services -y
```



查看全部的nat规则

```bash
iptables -t nat -L -n --line-numbers
```



在DOCKER链下看见了6807与6806之间的转发，是正在生效的

![](https://m.360buyimg.com/babel/jfs/t1/82040/4/21435/91901/62ff370dE7bd29d3e/0454c6fe470bacbc.png)



把这条规则删除，删除的行号要与查到的对应，想要让删除的规则永久生效，可以看补充1。

> 这种删除方法不是彻底删除，重启iptables或者容器，都会失效，我正好利用这个机制来决定siyuanBackUp的启动与关闭，详细使用操作看后面的补充2

```bash
iptables -t nat -D DOCKER 行号
```

![](https://m.360buyimg.com/babel/jfs/t1/42053/17/18620/88719/62ff3726E69c93f39/810a6eeca7899492.png)



删除规则后，页面刷新一下，已经是打不开了，此时用户访问的流量已经从原来的6807被转发到了8712，如果仍然可访问，解决方法看后面的补充3

![](https://m.360buyimg.com/babel/jfs/t1/209024/35/25609/35269/62ff373bEf5950075/d96c4a08d55de071.png)



然后以透明代理模式启动mitmproxy

```bash
mitmdump -p 8712 --set block_global=false --mode transparent -s siyuan_mitm.py
```



页面正常加载，且mitmproxy成功捕获到了流量

![](https://m.360buyimg.com/babel/jfs/t1/1486/26/20378/169204/62ff3757E7060ad83/c7427e8016db4273.png)



**补充：**

1. 如果需要让6807->6806的docker规则永久删除，可以在配置文件中将这条规则注释掉，这样再重启iptables都不会使其生效了

![img](https://m.360buyimg.com/babel/jfs/t1/210837/35/25506/69039/62ff377aE8c874842/54fd10a0dc938d28.png) 



重启iptables，查看规则，发现只有我们自定义规则了

![img](https://m.360buyimg.com/babel/jfs/t1/45294/12/20755/53618/62ff3794Ea0571730/218df900c69c470f.png) 



不过，如果是重启了容器，规则还是会被覆盖生效，这是无可避免的，除非再写一条规则，把docker映射的6807端口映射到其他端口

![img](https://m.360buyimg.com/babel/jfs/t1/49660/3/21466/89981/62ff37aeE0d807f2a/1a294ecff5076adf.png) 





2. 如果想要停止透明代理，可以直接重启iptables，或者重启容器，想需要再次让6807端口走透明代理就把DOCKER链下的6807->6806的转发规则删除，**删除规则是立即生效的，不需要重启**，下次再像代理，需要再手动把docker的规则删除。





3. 如果添加了规则，并且删了6807->6806的规则，网页仍然可以访问，检查是不是网卡名称的原因，使用`ifconfig`看自己的网卡名称，像我这台虚拟机，网卡名就不是默认的eth0，而是ens33

![img](https://m.360buyimg.com/babel/jfs/t1/209772/7/24499/120587/62ff37caEdb4a8fba/d94e750b423aad81.png) 



这就要修改两个地方，重新添加规则，并且修改siyuan_mitm.py

`vi /etc/sysconfig/iptables`找到添加的两条自定义规则，将两处的eth0改成自己的网卡名

修改`siyuan_mitm.py`中nic的值

修改完后重启iptables







### 四、制作触发器

最后需要做一个触发器，用于触发备份请求，这里的方案是改前端代码，通过制作按钮可以发起备份请求。

> 也可以再额外去写一个crontab，做一个时间触发器，比如每周六晚上十一点做一次备份
>
> 0 23 * * 6 /myapps/siyuan/siyuanShell/backup.sh



时间触发器比较简单，下面说这个手动的怎么弄，进入最开始导出来的desktop目录，有一个叫`main.fcaf89eaf1cee5881c1f.js`的js文件，要修改的就是这个。

直接修改有点困难，这个js是被极限压缩了，得去做代码格式化，这里直接提供修改的快捷方法



vi 编辑文件，然后斜杠向下搜关键字

```javascript
<div id="barSync" class="toolbar
```

搜到的第一个结果就是要改的目标，把id的值改为其他的，我改成了barBackupSelf，也可以自定义其他的

![img](https://m.360buyimg.com/babel/jfs/t1/106314/18/31027/407583/62ff37f3Eb57b3b8a/679aa3d45f223f17.png) 



再继续搜关键词

```javascript
${window.siyuan.config.sync.stat||window.siyuan.languages.syncNow+
```

搜到的第一个结果，把双引号之间的内容改成`立即备份`

![img](https://m.360buyimg.com/babel/jfs/t1/59963/12/21280/404908/62ff3811E143cdc9b/1f587cb662759752.png) 



然后继续vi搜关键词

```javascript
if("barSync"===t.id){if((0,f.needSubscri
```

在**if**的前面插入一段代码，这个`/api/self/backup/alipan`就是我们用于触发上传的api，这里的barBackupSelf要与第一步定义的id相同

```javascript
if("barBackupSelf"===t.id){(0,c.fetchPost)("/api/self/backup/alipan",{}),e.stopPropagation();const i = n(1890);if(true) void(0, i.showMessage)(window.siyuan.languages._kernel[41]);break}
```

![img](https://m.360buyimg.com/babel/jfs/t1/121415/14/29274/410217/62ff3825E24121cb9/dd43978a374e3934.png) 



最后，让mitmproxy跑起来，看一下效果

> 记得把语言改成中文> Settings-->Appearance-->Language

![img](https://m.360buyimg.com/babel/jfs/t1/120850/11/24677/38929/62ff3855Ebc827cef/6a487a6bd84b4883.png) 



上传成功

![img](https://m.360buyimg.com/babel/jfs/t1/165560/15/25795/113272/62ff387bE9d60bb6c/8b6174a2affbc0f0.png) 



 ![img](https://m.360buyimg.com/babel/jfs/t1/84653/1/21595/14243/62ff38a3E3cc58cd3/021ef323191fb5fd.png) 





[思源笔记 - 本地优先的个人知识管理系统，支持 Markdown 排版、块级引用和双向链接 (b3log.org)](https://b3log.org/siyuan/)![思源笔记](https://m.360buyimg.com/babel/jfs/t1/82428/5/21411/111220/62fa14beE54cc5211/8dce70bac9abf7a5.png)



## 问题

有问题请提交[issue](https://github.com/aqz236/siyuanShell/issues)

## 许可

`siyuanBackUp`是在GPL3.0 许可下许可的开源软件。

## 免责声明

* 本程序为免费开源项目，旨在增强对用户文件的可靠性，方便使用者对自己的数据进行备份和恢复以及学习Shell，使用时请遵守相关法律法规，请勿滥用；
* 本程序通过对文件进行压缩，无破坏官方程序、接口行为；
* 本程序仅做程序的压缩、备份到本地或上传到用户自己的云盘，不转发、恶意获取、篡改任何用户数据；
* 在使用本程序之前，你应了解并承担响应的风险，包括但不限于修改修改脚本导致数据丢失、账号被ban、下载限速等，与本程序无关；
* 如有侵权，请通过[邮件](mailto:sun1567888@gmail.com)与我联系，会及时处理