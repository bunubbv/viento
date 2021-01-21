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
        data = re.sub("'' '''.*?''' ''", "<i><b>" + bold_italic_text.group(1) + "</b></i>", data)

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

    return data