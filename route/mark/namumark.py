import re

async def namumark(data):
    ## 굵게
    bold_text = re.search("'''(.*?)'''", data)
    if bold_text:
        data = re.sub("'''.*?'''", "<b>" + bold_text.group(1) + "</b>", data)
        
    ## 기울임
    italic_text = re.search("''(.*?)''", data)
    if italic_text:
        data = re.sub("''.*?''", "<i>" + italic_text.group(1) + "</i>", data)

    ## 굵게 + 기울임
    bold_italic_text = re.search("'' '''(.*?)''' ''", data)
    if bold_italic_text:
        data = re.sub("''' ''.*?'' '''", "<i><b>" + bold_italic_text.group(1) + "</b></i>", data)

    ## 밑줄
    under_text = re.search("__(.*?)__", data)
    if under_text:
        data = re.sub("__.*?__", "<u>" + under_text.group(1) + "</u>", data)

    ## 취소선 1
    del_1_text = re.search("~~(.*?)~~", data)
    if del_1_text:
        data = re.sub("~~.*?~~", "<s>" + del_1_text.group(1) + "</s>", data)
    
    ## 취소선 2
    del_2_text = re.search("--(.*?)--", data)
    if del_2_text:
        data = re.sub("--.*?--", "<s>" + del_2_text.group(1) + "</s>", data)

    ## 위첨자
    sup_text = re.search("\^\^(.*?)\^\^", data)
    if sup_text:
        data = re.sub("\^\^.*?\^\^", "<sup>" + sup_text.group(1) + "</sup>", data)

    ## 아래첨자
    sub_text = re.search(",,(.*?),,", data)
    if sub_text:
        data = re.sub(",,.*?,,", "<sub>" + sub_text.group(1) + "</sub>", data)

    ## 텍스트 색상 1
    text_color_1 = re.search("{{{#([0-9a-fA-F]{3,6}) (.*?)}}}", data)
    if text_color_1:
        data = re.sub("{{{#([0-9a-fA-F]{3,6}) (.*?)}}}", "<span style='color:#" + text_color_1.group(1) + "'>" + text_color_1.group(2) + "</span>", data)

    ## 텍스트 색상 2
    text_color_2 = re.search("{{{#(.{1,}) (.*?)}}}", data)
    if text_color_2:
        data = re.sub("{{{#(.{1,}) (.*?)}}}", "<span style='color:" + text_color_2.group(1) + "'>" + text_color_2.group(2) + "</span>", data)

    ## 글자 크게
    text_big = re.search("{{{\+([1-5]{1}) (.*?)}}}", data)
    if text_big:
        data = re.sub("{{{\+([1-5]{1}) (.*?)}}}", "<span style='font-size:" + str(int(text_big.group(1)) * 30 + 100) + "%'>" + text_big.group(2) + "</span>", data)

    ## 글자 작게
    text_small = re.search("{{{\-([1-5]{1}) (.*?)}}}", data)
    if text_small:
        data = re.sub("{{{\-([1-5]{1}) (.*?)}}}", "<span style='font-size:" + str(int(text_small.group(1)) * -10 + 100) + "%'>" + text_small.group(2) + "</span>", data)

    ## 리터럴
    text_literal = re.search("{{{(.*?)}}}", data)
    if text_literal:
        data = re.sub("{{{(.*?)}}}", "<code>" + text_literal.group(1) + "</code>", data)

    return data