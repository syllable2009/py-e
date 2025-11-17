from __future__ import print_function, unicode_literals
import re, os, sys, time, shutil, signal, tarfile, hashlib, platform, tempfile, traceback
import subprocess as sp

VER = "1.19.20"
SIZE = 1021055
CKSUM = "62fd35aa43068e2bca0a8b73"
STAMP = 1762045928



def main():
    print(sys.argv)
    # if "--versionb" in sys.argv:
    # 	print(VER)

    print(str(sys.version))
    sysver = str(sys.version).replace("\n", "\n" + " " * 18)
    print(sysver)
    pktime = time.strftime("%Y-%m-%d, %H:%M:%S", time.gmtime(STAMP))
    print(pktime)
    arg = ""
    try:
        arg = sys.argv[1]
    except:
        pass
    print(arg)
    name = "pe-copyparty"
    try:
        name += "." + str(os.geteuid())
    except:
        pass
    # name:pe-copyparty.501
    print(f"name:{name}")
    tag = "v" + str(STAMP)
    # /var/folders/db/dwcxr95j08ld056f02yq_p3w0000gn/T
    top = tempfile.gettempdir()
    print(f"top:{top}")
    opj = os.path.join
    ofe = os.path.exists
    final = os.path.join(top, name)
    print(f"final:{final}")
    # san:/var/folders/db/dwcxr95j08ld056f02yq_p3w0000gn/T/pe-copyparty.501/copyparty/up2k.py
    san = os.path.join(final, "copyparty/up2k.py")
    print(f"san:{san}")
    for suf in range(0, 9001):
        withpid = "%s.%d.%s" % (name, os.getpid(), suf)
        mine = os.path.join(top, withpid)
        print(f"mine:{mine}")
        if not os.path.exists(mine):
            break
    # mine:/var/folders/db/dwcxr95j08ld056f02yq_p3w0000gn/T/pe-copyparty.501.32320.0
    tar = os.path.join(mine, "tar")
    print(f"tar:{tar}")

    try:
        if tag in os.listdir(final) and os.path.exists(san):
            print("found early")
    except:
        pass
    sz = 0
    # os.mkdir(mine)
    me = os.path.abspath(os.path.realpath(__file__))
    print(f"me:{me}")
    me = "/Users/jiaxiaopeng/github/mypy/src/mydemo/example/copyparty-sfx.py"
    with open(me, "rb") as f:
        # .rstrip(b"\r\n")：移除文件末尾可能存在的换行符
        buf = f.read().rstrip(b"\r\n")
    # 定义分隔标记
    ptn = b"\n# eof\n#"
    # 在整个文件内容 buf（bytes）中查找 ptn 第一次出现的位置。
    a = buf.find(ptn)
    if a <= 0:
        print("could not find archive marker")
    else:
        print(f"archive marker:{a}")
    # with open(tar, "wb") as f:



if __name__ == "__main__":
	main()
