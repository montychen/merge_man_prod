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

HEAD_SHIFT_DOWN = 30 # 头下余，预留位置给头发
HAIR_LARGER_THAN_HEAD = 0.06 # 头发比头大 10%
# 先确定头的位置， 后续身体部件的位置，都是以头的位置作为参考
def head_left_top_pos(images):       # pil 坐标的原点在 左上角
    # head_top_center = left_hand.width + body.width/2
    head_top_center = images["left_hand"].size[0] + images["body"].size[0] // 2
    head_left_top_x = head_top_center - images["head"].size[0] // 2

    

    head_left_top_y = HEAD_SHIFT_DOWN
    return head_left_top_x, head_left_top_y


def resize_hair(images):
    hair_widge = images["hair"].size[0]
    head_widge = images["head"].size[0]
    return resize_img(images["hair"], factor = head_widge/hair_widge + HAIR_LARGER_THAN_HEAD )

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

    EXPRESSION_INTO_FACE_X = 0
    EXPRESSION_INTO_FACE_Y = 50

    expression_left_top_x = head_center_x - images["expression"].size[0] // 2 + EXPRESSION_INTO_FACE_X
    expression_left_top_y = head_center_y - images["expression"].size[1] // 2 + EXPRESSION_INTO_FACE_Y
    print(images["head"].size, images["expression"].size )

    return expression_left_top_x, expression_left_top_y

def expression_left_top_pos_enlarge(images):  # pil 坐标的原点在 左上角
    head_x, head_y = head_left_top_pos(images)
    head_width, head_height = images["head"].size
    head_center_x, head_center_y = (head_x + head_width//2, head_y + head_height // 2)

    EXPRESSION_INTO_FACE_X = 0
    EXPRESSION_INTO_FACE_Y = 0

    expression_left_top_x = head_center_x - images["expression"].size[0]  + EXPRESSION_INTO_FACE_X
    expression_left_top_y = head_center_y - images["expression"].size[1]*3 // 4  + EXPRESSION_INTO_FACE_Y

    return expression_left_top_x, expression_left_top_y 

def body_left_top_pos(images):  # pil 坐标的原点在 左上角
    head_x, head_y = head_left_top_pos(images)
    head_width, head_height = images["head"].size
    head_center_x, head_center_y = (head_x + head_width//2, head_y + head_height // 2)

    BODY_LEFT_SHIFT = 50

    body_left_top_x = head_center_x - images["body"].size[0] // 2 - BODY_LEFT_SHIFT
    body_left_top_y = head_center_y + head_height // 2

    BODY_INTO_HEAD = 120   # 头要压在脖子上面
    return body_left_top_x, body_left_top_y - BODY_INTO_HEAD

def left_hand_top_pos(images):
    body_x, body_y = body_left_top_pos(images)

    LEFT_HAND_INTO_BODY_X = 80   # 100
    LEFT_HAND_INTO_BODY_Y = 320    # 300

    left_hand_x = body_x - LEFT_HAND_INTO_BODY_X
    left_hand_y = body_y + LEFT_HAND_INTO_BODY_Y
    return left_hand_x, left_hand_y

def right_hand_top_pos(images):
    body_x, body_y = body_left_top_pos(images)
    body_width, body_height = images["body"].size


    RIGHT_HAND_INTO_BODY_X = 50   #  500
    RIGHT_HAND_INTO_BODY_Y = 300    # 350

    right_hand_x = body_x + body_width//3 + RIGHT_HAND_INTO_BODY_X
    right_hand_y = body_y + RIGHT_HAND_INTO_BODY_Y
    return right_hand_x, right_hand_y

def left_leg_pos(images):
    body_x, body_y = body_left_top_pos(images)

    LEFT_LEG_INTO_BODY_X = 40
    LEFT_LEG_INTO_BODY_Y = 110

    left_leg_x = body_x + LEFT_LEG_INTO_BODY_X
    left_leg_y = body_y + images["body"].size[1] - LEFT_LEG_INTO_BODY_Y
    return left_leg_x, left_leg_y

def right_leg_pos(images):
    body_x, body_y = body_left_top_pos(images)

    RIGHT_LEG_INTO_BODY_X = 420
    RIGHT_LEG_INTO_BODY_Y = 110

    right_leg_x = body_x + images["body"].size[0] - RIGHT_LEG_INTO_BODY_X
    right_leg_y = body_y + images["body"].size[1] - RIGHT_LEG_INTO_BODY_Y
    return right_leg_x, right_leg_y


def resize_img(img, factor = 2):  # 放大图片，默认放大2倍
    width, height = round(img.width * factor), round(img.height * factor)
    return img.resize((width, height))




def merge_man(images, have_hair = True):   # pil 坐标的原点在 左上角
    man_width, man_height = result_man_width_height(images)

    # 创建一个新的图像，背景透明
    result_image = Image.new('RGBA', (man_width, man_height))

   
    result_image.paste(images['left_leg'], left_leg_pos(images), mask=images['left_leg'])  # 左脚
    result_image.paste(images['right_leg'], right_leg_pos(images), mask=images['right_leg'])  # 右脚

    
    result_image.paste(images['left_hand'], left_hand_top_pos(images), mask=images['left_hand'])  # 左手

    result_image.paste(images['body'], body_left_top_pos(images), mask=images['body'])  # 身体
    result_image.paste(images['head'], head_left_top_pos(images), mask=images['head'])  # 头

    # result_image.paste(images['expression'], expression_left_top_pos(images), mask=images['expression'])  # 表情
    # 默认提供的表情图片太小，先放大
    result_image.paste(resize_img(images['expression']), expression_left_top_pos_enlarge(images), mask=resize_img(images['expression']))  # 表情

    if have_hair: 
        result_image.paste(resize_hair(images), hair_top_pos(images), mask=resize_hair(images))  # 头发

    result_image.paste(images['right_hand'], right_hand_top_pos(images), mask=images['right_hand'])  # 右手



    # 保存结果图像
    result_image.save(os.path.join(os.getcwd(), 'static/result_image.png'))
    # result_image.show()
              


@app.post("/merge", response_class=PlainTextResponse)
def merge(body_com: Body_Component):
    print(f"\n{body_com}\n")
    selected_images = get_selected_img(body_com)
    merge_man(selected_images, have_hair=body_com.hair != "0_NO_HAIR.png")
    return "static/result_image.png"



@app.get("/test", response_class=HTMLResponse)
def test():
    cur_dir = os.getcwd()   # 获取当前目录
    return FileResponse(f"{cur_dir}/static/test.html", media_type="text/html")



@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
