import requests
from django.http import JsonResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from django.views.decorators.csrf import csrf_exempt

from api.chaojiying import Chaojiying_Client


@csrf_exempt
def verify(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if username and password:
        session = requests.session()
        cookies = get_cookie()
        str_url = 'http://yitjw.minghuaetc.com/yjlgxy/Logon.do?method=logon&flag=sess'
        data_str = session.post(str_url, cookies=cookies).text
        scode = data_str.split('#')[0]
        sxh = data_str.split('#')[1]
        code = username + '%%%' + password
        encoded = ''
        for i in range(len(code)):
            if i < 20:
                encoded += code[i] + scode[:int(sxh[i])]
                scode = scode[int(sxh[i]):]
            else:
                encoded += code[i:]
                break
        captcha_url = 'http://yitjw.minghuaetc.com/yjlgxy/verifycode.servlet'
        img = session.get(captcha_url, cookies=cookies).content
        # 保存验证码图片
        with open('1.png', 'wb') as f:
            f.write(img)
        chaojiying = Chaojiying_Client('daxueshiguang', 'dxsg666666', '901221')
        im = open('1.png', 'rb').read()
        # 调用接口识别
        res = chaojiying.PostPic(im, 1902)
        # 识别结果
        pic_str = res['pic_str']
        login_url = 'http://yitjw.minghuaetc.com/yjlgxy/Logon.do?method=logon'
        data = {
            'view': '0',
            'useDogCode': '',
            'encoded': encoded,
            'RANDOMCODE': pic_str
        }
        resp = session.post(login_url, cookies=cookies, data=data)
        if '验证码错误' in resp.text:
            return JsonResponse({'data': '验证码识别错误',
                                 'msg': 'error',
                                 'status': 400})
        elif '密码错误' in resp.text:
            return JsonResponse({'data': '帐号或密码错误',
                                 'msg': 'error',
                                 'status': 400})
        else:
            return JsonResponse({'data': '帐号、密码正确',
                                 'msg': 'ok',
                                 'status': 200})
    else:
        return JsonResponse({'data': '缺少参数',
                             'msg': 'error',
                             'status': 400})


def get_cookie():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get('http://yitjw.minghuaetc.com/yjlgxy/')
    cookies_dict = driver.get_cookies()[0]
    cookies = {
        cookies_dict['name']: cookies_dict['value']
    }
    return cookies
