from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import requests
import base64
import pymysql
import traceback
# Create your views here.
KEY = "" #请使用自己申请的key
SECRET = "" #请使用自己申请的key
API = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
EMO_ARR = ('sadness', 'neutral', 'disgust', 'anger', 'surprise', 'fear', 'happiness')
EMOCH_ARR = ('悲伤', '平静', '厌恶', '生气', '惊讶', '害怕', '高兴')
EMOCH_ARR1 = ('吞声忍泪', '若无其事', '鄙夷不屑', '愤愤不平', '目瞪口呆', '提心吊胆', '笑逐颜开')
EMOCH_ARR2 = ('痛心疾首', '心平气和', '反感至极', '怒不可遏', '大吃一惊', '心惊肉跳', '喜上眉梢')
EMOCH_ARR3 = ('悲痛欲绝', '心如止水', '深恶痛绝', '怒发冲冠', '惊慌失措', '丧胆亡魂', '心花怒放')


@csrf_exempt
def get_image(request):
    if request.method == "POST":
        #上传照片至face++
        file = request.FILES['file'].read()
        base64_file = base64.b64encode(file)
        data = {
            'api_key': KEY,
            'api_secret': SECRET,
            'return_attributes': 'gender,age,smiling,emotion,beauty',
            'image_base64': base64_file
        }
        response = requests.post(API, data=data)
        json_data = response.json()

        #错误处理
        if 'error_message' in json_data:
            return HttpResponse(json.dumps({
                "success": -1,
                "msg": json_data['error_message']
            }))
        if json_data['faces'] == []:
            return HttpResponse(json.dumps({
                "success": -1,
                "msg": '未检测到人脸，请换张图片'
            }))

        #数据处理
        attr_data = json_data['faces'][0]['attributes']
        age = attr_data['age']['value']
        sex = attr_data['gender']['value']
        if sex == 'Male':
            sex = '男人'
            beauty = attr_data['beauty']['male_score']
        else:
            sex = '女人'
            beauty = attr_data['beauty']['female_score']
        if age >= 50:
            sex = '老' + sex
        if age <= 20:
            sex = '小' + sex
        age = str(age)
        max_score = 0
        max_index = 0
        for i in range(6):
            emo_type = EMO_ARR[i]
            emo_score = attr_data['emotion'][emo_type]
            if emo_score > max_score:
                max_index = i
                max_score = emo_score
        if max_score <= 50:
            emotion = EMOCH_ARR1[max_index]
        elif max_score <= 75:
            emotion = EMOCH_ARR2[max_index]
        else:
            emotion = EMOCH_ARR3[max_index]
        smile = attr_data['smile']['value']

        # 连接mysql
        db = pymysql.connect("localhost", "root", "19906500", "django", charset='utf8')
        cursor = db.cursor()

        # 查询top100排行
        sql = "SELECT obj.id, obj.mark, @rownum:= @rownum + 1 AS rank, obj.username FROM" \
              " (SELECT id, username, mark FROM ranking ORDER BY mark DESC LIMIT 100)" \
              " AS obj, (SELECT @rownum:= 0) r;"

        try:
            cursor.execute(sql)
            db.commit()
        except:
            f = open("/py/back/face/0.txt", 'w')
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
        in_range = 0
        if count < 100:
            in_range = 1
        elif beauty > results[99][1]:
            in_range = 1

        return HttpResponse(json.dumps({
            "success": 1,
            "age": age,
            "sex": sex,
            "emotion": emotion,
            "smile": smile,
            "beauty": beauty,
            "in_range": in_range
        }))
    return HttpResponse()
