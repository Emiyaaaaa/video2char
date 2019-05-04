#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Li Haozheng
# @Time    : 2019/5/3 15:56

from PIL import Image, ImageDraw, ImageFont
import cv2
import math

video_path = r'E:\python\untitled\common2\output.mp4' #视频存放路径

font_size = 16 #字号
font_color = (255, 255, 255) #字符颜色
background_color = (0, 0, 0) #背景颜色

gif_width = 640 #输出的 gif 宽，单位：px
start_time = '00:15' #开始转换的时间
end_time = '00:16' #结束转换的时间，相当于裁剪视频，''或None表示不裁剪
str_tailor = (0, 0, 0, 0) #可裁剪字符画，四个参数为上，右，下，左需裁剪的字符数
timeF = 7 #可自行修改帧数，但不推荐修改

class Char2pic():

    font = ImageFont.truetype("simhei.ttf", font_size)

    def __init__(self, text):

        self.width = gif_width
        self.text = text
        self.duanluo, self.note_height, self.line_height = self.split_text()

    def get_duanluo(self, text):
        txt = Image.new('RGBA', (100, 100), (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        duanluo = ""
        sum_width = 0
        line_count = 1
        line_height = 0
        for char in text:
            width, height = draw.textsize(char, self.font)
            sum_width += width
            if sum_width > self.width:
                line_count += 1
                sum_width = 0
                duanluo += '\n'
            duanluo += char
            line_height = max(height, line_height)
        if not duanluo.endswith('\n'):
            duanluo += '\n'
        return duanluo, line_height, line_count

    def split_text(self):
        max_line_height, total_lines = 0, 0
        allText = []
        for text in self.text.split('\n'):
            duanluo, line_height, line_count = self.get_duanluo(text)
            max_line_height = max(line_height, max_line_height)
            total_lines += line_count
            allText.append((duanluo, line_count))
        line_height = max_line_height
        total_height = total_lines * line_height
        return allText, total_height, line_height

    def main(self,gif_height):
        img = Image.new('RGB', (gif_width, gif_height), background_color)
        draw = ImageDraw.Draw(img)
        # 左上角开始
        x, y = 0, 0
        for duanluo, line_count in self.duanluo:
            draw.text((x, y), duanluo, fill=font_color, font=self.font)
            y += self.line_height * line_count
        return img


class Video2char():
    def __init__(self):
        try:
            self.split_video = True
            if start_time != '' and start_time != None:
                start_sec = self.time2sec(start_time)
            else:
                start_sec = 0
            if end_time != '' and end_time != None and end_time != '00:00':
                end_sec = self.time2sec(end_time)
            else:
                end_sec = 0
            self.start_sec = start_sec
            self.end_sec = end_sec
        except:
            self.split_video = False


        vc = cv2.VideoCapture(video_path)
        frame_width = vc.get(cv2.CAP_PROP_FRAME_WIDTH)
        frame_height = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)
        en_font_size = math.ceil(font_size / 2)
        self.char_width_num = int(gif_width / en_font_size)
        gif_height = gif_width * frame_height / frame_width
        self.char_height_num = int(gif_height / (font_size + 1))
        self.gif_height = self.char_height_num * (font_size + 1)

    def time2sec(self,time):
        min = time.split(':')[0]
        sec = time.split(':')[1]
        all_sec = int(min) * 60 + int(sec)
        return all_sec

    def pic2gif(self,images):
        image = images[0]
        image.save('result.gif', save_all=True, append_images=images, loop=1, duration=1, comment=b"aaabb")

    def get_char(self,r,g,b,alpha=255):
        ascii_char = list(r"@$B%&W%M#*XhkbdpqwmZO0QLCJUYoazcvunxrjft/|()1{}[[-_+~<>i!lI;:,^`'.  ")
        if alpha == 0:
            return ' '
        length = len(ascii_char)
        gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)
        unit = (256.0 + 1)/length
        return ascii_char[int(gray/unit)]

    def pic2char(self,image):
        width_out = self.char_width_num
        height_out = self.char_height_num
        im = image.resize((width_out, height_out), Image.NEAREST)
        txt = ""
        for i in range(height_out):
            for j in range(width_out):
                txt += self.get_char(*im.getpixel((j, i)))
            txt = txt + '\n'
        return txt

    def main(self):
        vc = cv2.VideoCapture(video_path)
        frame_count = vc.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = vc.get(cv2.CAP_PROP_FPS)

        c = 1
        end_frame = frame_count

        if self.split_video == True:
            start_frame = fps * self.start_sec
            end_frame = fps * self.end_sec
            if end_frame == 0:
                end_frame = frame_count
            c = start_frame

        images = []
        if vc.isOpened():
            rval,frame = vc.read()
        else:
            rval = False
        while rval and c <= end_frame:
            rval,frame = vc.read()
            if(c%timeF==0):#c为第几帧
                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                text = self.pic2char(image)
                img = Char2pic(text).main(self.gif_height)
                images.append(img)
            c = c + 1
            cv2.waitKey(1)
        vc.release()
        self.pic2gif(images)


if __name__=='__main__':
    Video2char().main()
