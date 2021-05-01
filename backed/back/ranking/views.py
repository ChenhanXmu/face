#-*-coding:utf-8-*-
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import pymysql
import time
import traceback
from PIL import Image




#图片相似检测hash
def dhash(image, hash_size=8):
    # Grayscale and shrink the image in one step.
    image = image.convert('L').resize(
        (hash_size + 1, hash_size),
        Image.ANTIALIAS,
    )

    pixels = list(image.getdata())

    # Compare adjacent pixels.
    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = image.getpixel((col, row))
            pixel_right = image.getpixel((col + 1, row))
            difference.append(pixel_left > pixel_right)

            # Convert the binary array to a hexadecimal string.
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2 ** (index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0

    return ''.join(hex_string)


@csrf_exempt
def upload(request):
    if request.method == "POST":
        #获取传递数据
        username = request.POST['username']
        mark = request.POST['mark']
        file = request.FILES['file'].read()

        #保存图片
        mytime0 = time.strftime("%Y%m%d%H%M%S", time.localtime())
        mytime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

        img_name = username + '_' + mark + '_' + mytime0 + '.jpg'
        mypath = "/py/back/media/" + img_name
        path = mypath.encode('utf-8')
        f = open(path, 'wb');  # 代开一个文件，准备以二进制写入文件
        f.write(file);  # write并不是直接将数据写入文件，而是先写入内存中特定的缓冲区
        f.flush();  # 将缓冲区的数据立即写入缓冲区，并清空缓冲区
        f.close();  # 关闭文件
        img = Image.open(path)
        #计算hash
        myhash = dhash(img)

        #连接mysql
        db = pymysql.connect("localhost", "root", "19906500", "django", charset='utf8')
        cursor = db.cursor()

        #查询hash
        sql = "SELECT count(*) FROM ranking \
               WHERE hash = '%s'" % myhash
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
            return HttpResponse(json.dumps({
                "success": -1,
                "msg": "数据库查询hash错误"
            }))
        results = cursor.fetchall()
        count = results[0][0]

        #图片重复处理
        if count > 0:
            return HttpResponse(json.dumps({
                "success": -1,
                "msg": "此图片已存在，请上传其他图片"
            }))

        #插入
        sql = "INSERT INTO ranking(username, mark, date, imgpath, hash)" \
              " VALUES ('%s', %.3f, '%s', '%s', '%s');" % \
              (username, float(mark), mytime, img_name, myhash)
        vsql = sql.encode('utf8')
        try:
            cursor.execute(vsql)
            db.commit()
        except:
            f = open("/py/back/ranking/0.txt", 'w')
            traceback.print_exc(file=f)
            f.flush()
            f.close()
            db.rollback()
            return HttpResponse(json.dumps({
                "success": -1,
                "msg": '数据库插入错误'
            }))
        db.close()
        return HttpResponse(json.dumps({
            "success": 1,
            "msg": "上传成功！"
        }))
    return HttpResponse()


@csrf_exempt
def get_all(request):
    if request.method == "GET":
        # 连接mysql
        db = pymysql.connect("localhost", "root", "19906500", "django", charset='utf8')
        cursor = db.cursor()

        # 查询所有排行
        sql = "SELECT obj.id, obj.mark, @rownum:= @rownum + 1 AS rank, obj.username FROM" \
              " (SELECT id, username, mark FROM ranking ORDER BY mark DESC LIMIT 100)" \
              " AS obj, (SELECT @rownum:= 0) r;"

        try:
            cursor.execute(sql)
            db.commit()
        except:
            f = open("/py/back/ranking/0.txt", 'w')
            traceback.print_exc(file=f)
            f.flush()
            f.close()
            db.rollback()
            return HttpResponse(json.dumps({
                "success": -1,
                "msg": "数据库排名查询错误"
            }))
        results = cursor.fetchall()
        listData = []
        for row in results:
            c = dict([('no', row[2]), ('name', row[3]), ('mark', str(row[1]))])
            listData.append(c)

        return HttpResponse(json.dumps({
            "success": 1,
            "listData": listData
        }))
    return


@csrf_exempt
def get_top10(request):
    if request.method == "POST":
        # 获取传递数据
        index = int(request.POST['index'])

        # 连接mysql
        db = pymysql.connect("localhost", "root", "19906500", "django", charset='utf8')
        cursor = db.cursor()

        # 查询top10
        sql = "SELECT obj_new.mark, obj_new.username, obj_new.imgpath, obj_new.rank FROM" \
	          " (SELECT obj.mark, obj.username, obj.imgpath, @rownum:= @rownum + 1 AS rank FROM" \
              " (SELECT username, mark, imgpath FROM ranking ORDER BY mark DESC LIMIT 100)" \
              " AS obj, (SELECT @rownum:= 0) r)" \
              " AS obj_new where rank = '%d'; " % index
        try:
            cursor.execute(sql)
            db.commit()
        except:
            f = open("/py/back/ranking/0.txt", 'w')
            traceback.print_exc(file=f)
            f.flush()
            f.close()
            db.rollback()
            return HttpResponse(json.dumps({
                "success": -1,
                "msg": "数据库排名查询错误"
            }))
        results = cursor.fetchall()
        count = cursor.rowcount
        if count != 0:
            mark = str(results[0][0])
            author = results[0][1]
            path = results[0][2]
            return HttpResponse(json.dumps({
                "success": 1,
                "mark": mark,
                "author": author,
                "url": path
            }))
        else:
            return HttpResponse(json.dumps({
                "success": 1,
                "mark": '',
                "author": '',
                "url": ''
            }))
    return HttpResponse()


@csrf_exempt
def get_my(request):
    if request.method == "POST":
        # 获取传递数据
        username = request.POST['username']

        # 连接mysql
        db = pymysql.connect("localhost", "root", "19906500", "django", charset='utf8')
        cursor = db.cursor()

        # 查询我的排行
        sql = "SELECT obj_new.id, obj_new.mark, obj_new.rank, obj_new.username FROM" \
              " (SELECT obj.id, obj.mark, obj.username, @rownum:= @rownum + 1 AS rank FROM" \
              " (SELECT id, mark, username FROM ranking ORDER BY mark DESC LIMIT 100)" \
              " AS obj, (SELECT @rownum:= 0) r)" \
              " AS obj_new where username = '%s' ORDER BY mark DESC;" % username

        try:
            cursor.execute(sql)
            db.commit()
        except:
            f = open("/py/back/ranking/0.txt", 'w')
            traceback.print_exc(file=f)
            f.flush()
            f.close()
            db.rollback()
            return HttpResponse(json.dumps({
                "success": -1,
                "msg": "数据库排名查询错误"
            }))
        results = cursor.fetchall()
        listData = []
        maxrank = 1000
        for row in results:
            c = dict([('id', row[0]), ('mark', str(row[1])), ('rank', row[2])])
            listData.append(c)
            if int(row[2]) < maxrank:
                maxrank = int(row[2])

        return HttpResponse(json.dumps({
            "success": 1,
            "listData": listData,
            "max": str(maxrank)
        }))
    return HttpResponse()

