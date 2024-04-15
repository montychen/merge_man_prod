import os
from PIL import Image

from typing import Union

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static") # 假设你的 static 目录在项目根目录下

templates = Jinja2Templates(directory="static")    # 声明 模板文件放在 static 目录下





def fill_body_com_list() -> list:
    # 收集：身体部件的目录名  和 它下面的png文件。   ["头",[这里会包含这个目录下所有的png文件名]] 
    # [['头', "head", ['27_head.png', '19_head.png', 'head.png', '31_head.png', '30_head.png']]]
    body_com_list = [["发型", "hair", []], ["头", "head", []],  ["表情", "expression", []],  ["身体", "body", []],  
                     ["左手", "left_hand", []], ["右手", "right_hand", []],  ["左腿", "left_leg", []],  ["右腿", "right_leg", []]  ]  
    cur_dir = os.getcwd()   # 获取当前目录
    for item in body_com_list:
        file_dir = os.path.join(cur_dir, "static/body_com", item[0])
        # print(file_dir)

        files =  os.listdir(file_dir)
        png_files = [f for f in files if f.endswith(".png")]
        sorted_files = sorted(png_files) # 对文件列表进行排序

        for filename in sorted_files:
            if filename.lower().endswith(".png"):
                item[2].append(filename)
        # print( len(item[1]), "\n", item[1])
    return body_com_list

def get_body_com_url_pre() -> str:  # "http://127.0.0.1:8000/static/body_com/头/19_head.png"
    return "static/body_com"


@app.get("/", response_class=HTMLResponse)  # response_class=HTMLResponse 指明响应是一个 HTML
async def home_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"body_com_list": fill_body_com_list(), "body_com_url_pre": get_body_com_url_pre()}
    )

class Body_Component(BaseModel):   # 接收客户端 Post请求发过来的参数
    hair: str = 'hair1.png'
    head: str = '0head.png'
    expression: str = '普通表情_1-1.png'

    body: str = '10_body.png'

    left_hand: str = '10_hand2.png'   # 左手
    right_hand: str = '10_hand1.png'   # 右手
    left_leg: str = '10_foot2.png'   # 左腿
    right_leg: str = '10_foot1.png'   # 右腿


def get_selected_img(body_select):    
    # 加载所有选择的图片
    cwd = os.getcwd()

    selected_images = {
        "hair": Image.open(os.path.join(cwd, "static/body_com/发型", body_select.hair)),
        "head": Image.open(os.path.join(cwd, "static/body_com/头", body_select.head)),
        "expression": Image.open(os.path.join(cwd, "static/body_com/表情", body_select.expression)),
        "body": Image.open(os.path.join(cwd, "static/body_com/身体", body_select.body)),
        "left_hand": Image.open(os.path.join(cwd, "static/body_com/左手", body_select.left_hand)),
        "right_hand": Image.open(os.path.join(cwd, "static/body_com/右手", body_select.right_hand)),
        "left_leg": Image.open(os.path.join(cwd, "static/body_com/左腿", body_select.left_leg)),
        "right_leg": Image.open(os.path.join(cwd, "static/body_com/右腿", body_select.right_leg)),
    }
    return selected_images




def result_man_width_height(images):   
    # man_width = (left_hand + body + right_hand)的width之和
    # man_height = (hair + head + body + left_leg)的height之和
    man_width = images['left_hand'].size[0] + images['body'].size[0] + images['right_hand'].size[0] 
    man_height = images['hair'].size[1] + images['head'].size[1] + images['body'].size[1] + images['left_leg'].size[1] 

    print(man_width, "\t", man_height)
    return man_width, man_height


# images = get_selected_img()
# man_width, man_height = result_man_width_height(images)

HEAD_SHIFT_DOWN = 20 # 头下移，预留位置给头发
# HAIR_LARGER_THAN_HEAD = 0.06 # 头发比头大 10%
HAIR_LARGER_THAN_HEAD =  0.22 # 头发比头大 10%

# 先确定头的位置， 后续身体部件的位置，都是以头的位置作为参考
def head_left_top_pos(images):       # pil 坐标的原点在 左上角
    # head_top_center = left_hand.width + body.width/2
    head_top_center_x = images["left_hand"].size[0] + images["body"].size[0] // 2
    head_left_top_x = head_top_center_x - images["head"].size[0] // 2
    head_left_top_y = HEAD_SHIFT_DOWN
    return head_left_top_x, head_left_top_y


def resize_hair(images):
    hair_widge = images["hair"].size[0]
    head_widge = images["head"].size[0]
    factor = head_widge/hair_widge + HAIR_LARGER_THAN_HEAD  # new_hair = hair * head_widge/hair_widge
    return resize_img(images["hair"], factor)

def hair_top_pos(images):   # pil 坐标的原点在 左上角
    hair_x, hair_y = head_left_top_pos(images)

    HAIR_LEFT_SHIFT_THAN_HEAD = HAIR_LARGER_THAN_HEAD/2 # 头发起始位置比头的位置往左偏移一点

    hair_x = hair_x - round(images["head"].size[0] * HAIR_LEFT_SHIFT_THAN_HEAD)
    hair_y = hair_y - HEAD_SHIFT_DOWN
    return hair_x, hair_y

def expression_left_top_pos(images):  # pil 坐标的原点在 左上角
    head_x, head_y = head_left_top_pos(images)
    head_width, head_height = images["head"].size
    head_center_x, head_center_y = (head_x + head_width//2, head_y + head_height // 2)

    EXPRESSION_INTO_FACE_X = -15
    EXPRESSION_INTO_FACE_Y = 25

    new_expression_img = expression_adapt_to_width_of_head(images)

    expression_left_top_x = head_center_x - new_expression_img.size[0] // 2 + EXPRESSION_INTO_FACE_X
    expression_left_top_y = head_center_y - new_expression_img.size[1] // 2 + EXPRESSION_INTO_FACE_Y
    print(images["head"].size, images["expression"].size )

    return expression_left_top_x, expression_left_top_y

def expression_adapt_to_width_of_head(images): # 表情的宽度适配成头的大小   pil 坐标的原点在 左上角 
    ADAPT_TO_WIDTH_OF_HEAD = 1.1    #  定义适配成头的比例 

    head_width= images["head"].size[0]
    expression_width = images["expression"].size[0]
    factor = ADAPT_TO_WIDTH_OF_HEAD * head_width / expression_width  #  expression_width * factor = ADAPT_TO_WIDTH_OF_HEAD * head_width
    new_expression_img =  resize_img(images["expression"], factor)
    return new_expression_img


def body_left_top_pos(images):  # pil 坐标的原点在 左上角
    BODY_LEFT_SHIFT = 10  
    BODY_INTO_HEAD = 28     # 头要压在脖子上面

    head_x, head_y = head_left_top_pos(images)
    head_width, head_height = images["head"].size
    head_center_x, head_center_y = (head_x + head_width//2, head_y + head_height // 2)

    body_left_top_x = head_center_x - images["body"].size[0] // 2 - BODY_LEFT_SHIFT
    body_left_top_y = head_center_y + head_height // 2

    return body_left_top_x, body_left_top_y - BODY_INTO_HEAD

def left_hand_top_pos(images):
    body_x, body_y = body_left_top_pos(images)
    hand_weight = images["left_hand"].size[0]
    body_weight, body_height = images["body"].size

    LEFT_HAND_INTO_BODY_PERCENT_X = 43  # 左手进入身体百分比
    LEFT_HAND_INTO_BODY_PERCENT_Y = 18  

    LEFT_HAND_INTO_BODY_X = round(body_weight * LEFT_HAND_INTO_BODY_PERCENT_X / 100)   # 75
    LEFT_HAND_INTO_BODY_Y = round(body_height * LEFT_HAND_INTO_BODY_PERCENT_Y / 100)   # 38

    left_hand_x = body_x - hand_weight + LEFT_HAND_INTO_BODY_X
    left_hand_y = body_y + LEFT_HAND_INTO_BODY_Y
    return left_hand_x, left_hand_y

def right_hand_top_pos(images):
    RIGHT_HAND_INTO_BODY_X = -30   #  500
    RIGHT_HAND_INTO_BODY_Y = 45    # 350

    body_x, body_y = body_left_top_pos(images)
    body_width, body_height = images["body"].size

    right_hand_x = body_x + body_width + RIGHT_HAND_INTO_BODY_X
    right_hand_y = body_y + RIGHT_HAND_INTO_BODY_Y
    return right_hand_x, right_hand_y

def leg_weight_percent_half_body_weight(images, is_left_leg=True, percent = 95):  # 默认是半个身体宽带的 90%
    body_width, body_height = images["body"].size
    leg_img = images["left_leg"] if  is_left_leg else images["right_leg"]

    if images["left_leg"].size[0] > (body_width * percent/100) // 2 or images["right_leg"].size[0] > (body_width * percent/100) // 2 :  # 左脚或右脚 大于一半身体
        return resize_img(leg_img, percent/100)   # 左脚或右脚 都缩小 percent
    else:
        return leg_img

    # new_leg_width = 0.5 * body_width * percent / 100
    # new_leg = resize_img(leg_img, new_leg_width/leg_width)
    # print("=====\t is_left_leg", is_left_leg, "\t", new_leg_width, "\t====", leg_width)


def left_leg_pos(images, resize_leg_to_half_body_percent=False):  # 还要添加代码：保证 腿不能比半个身体大。
    body_x, body_y = body_left_top_pos(images)
    body_width, body_height = images["body"].size
    leg_img = leg_weight_percent_half_body_weight(images, is_left_leg=True) if resize_leg_to_half_body_percent else images["left_leg"] 

    LEG_RIGHT_SHIFT_BODY_PERCENT_X = 10
    LEG_DOWN_SHIFT_BODY_CENTER_PERCENT_Y = 50 
    LEFT_LEG_INTO_BODY_X = round(body_width * LEG_RIGHT_SHIFT_BODY_PERCENT_X / 100) # 20
    LEFT_LEG_INTO_BODY_Y = round(0.5 * body_height + 0.5 * body_height * LEG_DOWN_SHIFT_BODY_CENTER_PERCENT_Y / 100)   # 从身体中间 往下移 身体一半的百分之几 

    # delta_x = round((0.5 * body_width - leg_img.size[0])/2)    # 左腿比 一半身体 小多少
    delta_x = round((0.5 * body_width - leg_img.size[0])/2/2)    # 左腿比 一半身体 小多少


    left_leg_x = body_x + LEFT_LEG_INTO_BODY_X  + delta_x
    left_leg_y = body_y + LEFT_LEG_INTO_BODY_Y
    return left_leg_x, left_leg_y

def right_leg_pos(images, resize_leg_to_half_body_percent=False):   # 还要添加代码：保证 腿不能比半个身体大。
    body_x, body_y = body_left_top_pos(images)
    body_width, body_height = images["body"].size

    leg_img = leg_weight_percent_half_body_weight(images, is_left_leg=False) if resize_leg_to_half_body_percent else images["right_leg"] 
    leg_width, leg_height = leg_img .size

    LEG_LEFT_SHIFT_BODY_PERCENT_X = 1
    LEG_DOWN_SHIFT_BODY_CENTER_PERCENT_Y = 50 
    RIGHT_LEG_INTO_BODY_X = round(body_width * LEG_LEFT_SHIFT_BODY_PERCENT_X / 100) # 20
    RIGHT_LEG_INTO_BODY_Y = round(0.5 * body_height + 0.5 * body_height * LEG_DOWN_SHIFT_BODY_CENTER_PERCENT_Y / 100)   # 从身体中间 往下移 身体一半的百分之几 

    delta_x = round((0.5 * body_width - leg_width)/2)    # 右腿比 一半身体 小多少

    right_leg_x = body_x + body_width - RIGHT_LEG_INTO_BODY_X - delta_x - leg_width
    right_leg_y = body_y + RIGHT_LEG_INTO_BODY_Y
    return right_leg_x, right_leg_y


def resize_img(img, factor = 2.0):  # 放大图片，默认放大2倍
    width, height = round(img.width * factor), round(img.height * factor)
    return img.resize((width, height))



def merge_man(images, have_hair = True, have_left_leg = True):   # pil 坐标的原点在 左上角
    man_width, man_height = result_man_width_height(images)

    # 创建一个新的图像，背景透明
    result_image = Image.new('RGBA', (man_width, man_height))

   
    result_image.paste(leg_weight_percent_half_body_weight(images, is_left_leg=True), left_leg_pos(images, True), mask=leg_weight_percent_half_body_weight(images, is_left_leg=True))  # 左脚
    # result_image.paste(images['left_leg'], left_leg_pos(images), mask=images['left_leg'])  # 左脚

    result_image.paste(leg_weight_percent_half_body_weight(images, is_left_leg=False), right_leg_pos(images, True), mask=leg_weight_percent_half_body_weight(images, is_left_leg=False))  # 右脚
    # result_image.paste(images['right_leg'], right_leg_pos(images), mask=images['right_leg'])  # 右脚

    result_image.paste(images['left_hand'], left_hand_top_pos(images), mask=images['left_hand'])  # 左手
    result_image.paste(images['body'], body_left_top_pos(images), mask=images['body'])  # 身体
    result_image.paste(images['head'], head_left_top_pos(images), mask=images['head'])  # 头

    # 默认提供的表情图片太小，先放大
    # result_image.paste(images['expression'], expression_left_top_pos(images), mask=images['expression'])  # 表情
    # result_image.paste(expression_adapt_to_width_of_head(images), expression_left_top_pos(images), mask=expression_adapt_to_width_of_head(images))  # 表情

    if have_hair: 
        result_image.paste(resize_hair(images), hair_top_pos(images), mask=resize_hair(images))  # 头发

    result_image.paste(images['right_hand'], right_hand_top_pos(images), mask=images['right_hand'])  # 右手

    # 保存结果图像
    result_image.save(os.path.join(os.getcwd(), 'static/result_image.png'))
              


@app.post("/merge", response_class=PlainTextResponse)
def merge(body_com: Body_Component):
    print(f"\n{body_com}\n")
    selected_images = get_selected_img(body_com)
    merge_man(selected_images, have_hair=body_com.hair != "0_NO.png", have_left_leg=body_com.left_leg != "0_NO.png")
    return "static/result_image.png"



@app.get("/test", response_class=HTMLResponse)
def test():
    cur_dir = os.getcwd()   # 获取当前目录
    return FileResponse(f"{cur_dir}/static/test.html", media_type="text/html")



@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
