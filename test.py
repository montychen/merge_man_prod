import os
from PIL import Image


def img_info(dir):  # 列出目录下，图片的分辨率
    # '/Users/dj/STUDY/merge_man/static/body_com/身体'

    # 遍历目录中的文件
    for filename in os.listdir(dir):
        if filename.endswith(".png"):  # 检查文件扩展名是否为.png
            filepath = os.path.join(dir, filename)  # 获取文件的完整路径
            with Image.open(filepath) as img:
                width, height = img.size  # 获取图片的尺寸
                print(f"{filename}: {width}x{height}")  # 打印文件名和分辨率




def change_filename(top_level_dir):
# 遍历顶级目录
    for root, dirs, files in os.walk(top_level_dir):
        print(f"root:{root}\ndirs:{dirs}\nfiles:{files}\n")
        for dir_name in dirs:
            # 构建第二级目录的完整路径
            second_level_dir = os.path.join(root, dir_name)
            # 遍历第二级目录中的所有文件
            for filename in os.listdir(second_level_dir):
                # 构建原始文件的完整路径
                old_file = os.path.join(second_level_dir, filename)
                # 构建新的文件名，以第二级目录名称作为前缀
                new_filename = f"{dir_name}_{filename}"
                # 构建新文件的完整路径
                new_file = os.path.join(second_level_dir, new_filename)
                # 重命名文件
                os.rename(old_file, new_file)
                # print(f"Renamed '{old_file}' to '{new_file}'")

# change_filename("/Users/dj/STUDY/mojo_study/body")
                
def get_selected_img():
    image_files = {
        'hair': '头发.png',
        'head': 'head.png',
        'expression': '普通表情_15.png',   # 表情
        'body': 'body.png',
        'left_hand': 'hand2.png',
        'right_hand': 'hand1.png',
        'left_leg': 'foot2.png',
        'right_leg': 'foot1.png'
    }

    base_dir = os.path.join(os.getcwd(), "static/test_merge_img")
    # 加载所有图片
    return  {name: Image.open(os.path.join(base_dir, path)) for name, path in image_files.items()}

def result_man_width_height(images):   
    # man_width = (left_hand + body + right_hand)的width之和
    # man_height = (hair + head + body + left_leg)的height之和
    man_width = images['left_hand'].size[0] + images['body'].size[0] + images['right_hand'].size[0] 
    man_height = images['hair'].size[1] + images['head'].size[1] + images['body'].size[1] + images['left_leg'].size[1] 

    print(man_width, "\t", man_height)
    return man_width, man_height


# images = get_selected_img()
# man_width, man_height = result_man_width_height(images)

def head_left_top_pos(images):       # pil 坐标的原点在 左上角
    # head_top_center = left_hand.width + body.width/2
    head_top_center = images["left_hand"].size[0] + images["body"].size[0] // 2
    head_left_top_x = head_top_center - images["head"].size[0] // 2
    head_left_top_y = 0
    return head_left_top_x, head_left_top_y

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

def body_left_top_pos(images):  # pil 坐标的原点在 左上角
    head_x, head_y = head_left_top_pos(images)
    head_width, head_height = images["head"].size
    head_center_x, head_center_y = (head_x + head_width//2, head_y + head_height // 2)

    body_left_top_x = head_center_x - images["body"].size[0] // 2
    body_left_top_y = head_center_y + head_height // 2

    BODY_INTO_HEAD = 120   # 头要压在脖子上面
    return body_left_top_x, body_left_top_y - BODY_INTO_HEAD

def left_hand_top_pos(images):
    body_x, body_y = body_left_top_pos(images)

    LEFT_HAND_INTO_BODY_X = 100
    LEFT_HAND_INTO_BODY_Y = 300

    left_hand_x = body_x + LEFT_HAND_INTO_BODY_X
    left_hand_y = body_y + LEFT_HAND_INTO_BODY_Y
    return left_hand_x, left_hand_y

def right_hand_top_pos(images):
    body_x, body_y = body_left_top_pos(images)

    RIGHT_HAND_INTO_BODY_X = 500
    RIGHT_HAND_INTO_BODY_Y = 350

    right_hand_x = body_x + RIGHT_HAND_INTO_BODY_X
    right_hand_y = body_y + RIGHT_HAND_INTO_BODY_Y
    return right_hand_x, right_hand_y

def left_leg_pos(images):
    body_x, body_y = body_left_top_pos(images)

    LEFT_LEG_INTO_BODY_X = 150
    LEFT_LEG_INTO_BODY_Y = 100

    left_leg_x = body_x + LEFT_LEG_INTO_BODY_X
    left_leg_y = body_y + images["body"].size[1] - LEFT_LEG_INTO_BODY_Y
    return left_leg_x, left_leg_y

def right_leg_pos(images):
    body_x, body_y = body_left_top_pos(images)

    RIGHT_LEG_INTO_BODY_X = 150
    RIGHT_LEG_INTO_BODY_Y = 100

    right_leg_x = body_x + images["head"].size[0] - RIGHT_LEG_INTO_BODY_X
    right_leg_y = body_y + images["body"].size[1] - RIGHT_LEG_INTO_BODY_Y
    return right_leg_x, right_leg_y

def merge_man():   # pil 坐标的原点在 左上角
    images = get_selected_img()
    man_width, man_height = result_man_width_height(images)

    # 创建一个新的图像，背景透明
    result_image = Image.new('RGBA', (man_width, man_height))

   
    result_image.paste(images['left_leg'], left_leg_pos(images), mask=images['left_leg'])  # 左脚
    result_image.paste(images['right_leg'], right_leg_pos(images), mask=images['right_leg'])  # 右脚

    
    result_image.paste(images['right_hand'], right_hand_top_pos(images), mask=images['right_hand'])  # 右手
    
    result_image.paste(images['body'], body_left_top_pos(images), mask=images['body'])  # 身体
    result_image.paste(images['head'], head_left_top_pos(images), mask=images['head'])  # 头
    result_image.paste(images['expression'], expression_left_top_pos(images), mask=images['expression'])  # 表情
    result_image.paste(images['left_hand'], left_hand_top_pos(images), mask=images['left_hand'])  # 左手


    # 保存结果图像
    result_image.save('完整的人体.png')
    result_image.show()
              
# merge_man()
    
def test_paste():

    base_dir = os.path.join(os.getcwd(), "static")

    nomask_bg = Image.open(os.path.join(base_dir, "img/girl0.jpg"))
    mask_bg = Image.open(os.path.join(base_dir, "img/girl0.jpg"))
    hair = Image.open(os.path.join(base_dir, "test_merge_img/头发.png"))

    nomask_bg.paste(hair)
    mask_bg.paste(hair, mask=hair)     # mask：遮罩、掩膜图像。 遮罩的透明区域不合成， 透明的部分保持透明

    # nomask_bg.save("nomask_bg.png")
    mask_bg.save("mask_bg.png")

    mask_bg.show()
    nomask_bg.show()

# test_paste()
    
def img_flip_left_reght():
    file = os.path.join(os.getcwd(), "static/body_com/发型/头发 4.png")
    img = Image.open(file).transpose(Image.FLIP_LEFT_RIGHT)
    img.save(os.path.join(os.getcwd(), "static/body_com/发型/头发 4_mirror.png"))
    img.show()


# img_flip_left_reght()



def sorted_file():
    # 获取当前目录下的所有文件和目录
    dir = os.path.join(os.getcwd(), "static/body_com/头")

    items =  os.listdir(dir)

    # 过滤出所有文件（排除目录）
    files = [item for item in items if item.endswith(".png")]

    # 对文件列表进行排序
    sorted_files = sorted(files)

    # 打印排序后的文件列表
    for file in sorted_files:
        print(file)

# sorted_file()
        
def resize_img():
    file = os.path.join(os.getcwd(), "static/body_com/发型/hair1.png")
    factor = 2
    with Image.open(file) as im:
        width, height = round(im.width * factor), round(im.height * factor)
        im_resized = im.resize((width, height))
        im_resized.save(os.path.join(os.getcwd(), "static/body_com/发型/hair1_resize.png"))
        # im_resized.show()
        # im.show()

# resize_img()

def resize_img(img, factor = 2.0):  # 放大图片，默认放大2倍
    width, height = round(img.width * factor), round(img.height * factor)
    return img.resize((width, height))

def expression_width_is_one_half_of_head(): # 表情的宽度是头的 1/2   pil 坐标的原点在 左上角 
    head_img = Image.open(os.path.join(os.getcwd(), "static/body_com/头/g_f_8001_1.png"))
    expression_img = Image.open(os.path.join(os.getcwd(), "static/body_com/表情/胡子_h1.png"))

    head_width= head_img.size[0]
    expression_width = expression_img.size[0]
    factor = 0.5 * head_width / expression_width    #  expression_width * factor = 0.5 * head_width
    new_expression_img = resize_img(expression_img, factor)

    head_img.show()
    expression_img.show()
    new_expression_img.show()

expression_width_is_one_half_of_head()

